import ccxt 
import time
import pandas as pd
import numpy as np
import datetime
import math
import telegram as tel
import sys, os

with open("./binance_api.txt") as file:
    lines = file.readlines()
    api_key = lines[0].strip()
    secret_key = lines[1].strip()
    token = lines[2].strip()
    id_ = lines[3].strip()

position = {
    "type": None,
    "amount": 0,
    "price" : 0,
}
K = 0.3
symbol = "BTC/USDT"
op_mode = True
binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

def post_message(text):
    bot = tel.Bot(token=token)
    chat_id = id_
    bot.sendMessage(chat_id=chat_id, text=text) # send message

# long, short count
global long_enter_count
global short_enter_count
long_enter_count = 0
short_enter_count = 0

#balance return
def current_balance():
    balance = binance.fetch_balance()
    usdt = balance['total']['USDT']
    print(usdt)
    return usdt

# current price
def current_price(symbol):
    btc = binance.fetch_ticker(symbol)
    cur_price = btc['last']
    #print(cur_price)
    return cur_price

#position exist check
def current_position_check(symbol, position):
    infos = binance.fetchPositions()
    for info in infos:
        if info['info']['symbol'] == symbol:
            if info['contracts'] > 0.0:
                position['type'] = info['side']
                position['amount'] = info['contracts']
                position['price'] = info['entryPrice']

def cal_amount(usdt_balance, cur_price):
    portion = 1 
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    
    if amount > 0.001:
        amount = int(amount * 1000) / 1000
    else:
        amount = 0
    #print(amount)
    return amount 

# long / short target calculate
def call_target(symbol):
    btc = binance.fetch_ohlcv(
    symbol=symbol, 
    timeframe='1d', 
    since=None, 
    limit=2)

    df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    
    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    long_target = today['open'] + (yesterday['high'] - yesterday['low']) * K
    short_target = today['open'] - (yesterday['high'] - yesterday['low']) * K
    #print({'long_target' : long_target, 'short_target' : short_target })
    return {'long_target' : long_target, 'short_target' : short_target }

# enter
def enter_position(symbol, cur_price, long_target, short_target, amount, position):
    global long_enter_count
    global short_enter_count
    if cur_price > long_target:         # cur_price > long 
        if long_enter_count > 3:
            position['type'] = 'long'
            position['amount'] = amount
            order = binance.create_market_buy_order(symbol=symbol, amount=amount)
            position['price'] = order['price']
            op_mode = False
            post_message(position['type']+" 포지션 진입\n"+str(position['price'])+","+str(position['amount']))
        else:
            long_enter_count += 1
            short_enter_count = 0

    elif cur_price < short_target:      # cur_price < short 
        if short_enter_count > 3:
            position['type'] = 'short'
            position['amount'] = amount
            order = binance.create_market_sell_order(symbol=symbol, amount=amount)
            position['price'] = order['price']
            op_mode = False
            post_message(position['type']+" 포지션 진입\n"+str(position['price'])+","+str(position['amount']))
        else:
            short_enter_count += 1
            long_enter_count = 0
    
# exit 
def exit_position(symbol, position):
    global long_enter_count
    global short_enter_count
    amount = position['amount']
    if position['type'] == 'long':
        binance.create_market_sell_order(symbol=symbol, amount=amount)
        position['type'] = None 
        
    elif position['type'] == 'short':
        binance.create_market_buy_order(symbol=symbol, amount=amount)
        position['type'] = None 
        
    long_enter_count = 0
    short_enter_count = 0
    balance = current_balance()
    post_message("포지션 종료\n현재 잔액 : "+str(balance)+" usd\n")

def check_exit(position, cur_price):
    if position['type'] == None:
        return False
    else:
        if position['type'] == 'long':
            diff = (cur_price - position['price']) / cur_price * 100
            if diff >= 5 or diff <= -10:
                return True
            else:
                return False
        if position['type'] == 'short':
            diff = (position['price'] - cur_price) / cur_price * 100
            if diff >= 5 or diff <= -10:
                return True
            else:
                return False

if __name__ == '__main__': 
    
    cur_price = current_price(symbol=symbol)
    target_value = call_target(symbol=symbol)
    balance = current_balance()
    str_info = "cur_price : {}, long_target : {}, short_target : {}".format(cur_price, target_value['long_target'], target_value['short_target'])
    post_message("선물매매를 시작합니다.\n잔액 : "+str(balance)+" usd\n"+str_info)

    current_position_check(symbol=symbol, position=position)
    if position['amount'] > 0.0:
        post_message("기존 포지션이 남아있습니다.\n position : {}\n price : {}\n amount : {}\n".format(position['type'], position['price'], position['amount']))
        
    while True:
        try:
            now = datetime.datetime.now()

            if now.hour == 8 and now.minute == 50 and (0 <= now.second < 10):
                if op_mode and position['type'] is not None:
                    exit_position(symbol,position)
                    op_mode = False
                    

            # udpate target price
            if now.hour == 9 and now.minute == 0 and (20 <= now.second < 30):
                target_value = call_target(symbol=symbol)
                balance = current_balance()
                op_mode = True
                time.sleep(10)

            if position['type'] == None:
                cur_price = current_price(symbol=symbol)
                amount = cal_amount(usdt_balance=balance, cur_price=cur_price)

                if op_mode:
                    enter_position(
                        symbol=symbol, 
                        cur_price=cur_price,
                        long_target=target_value['long_target'],
                        short_target=target_value['short_target'],
                        amount=amount,
                        position=position
                    )
                    time.sleep(1)
            else:
                if check_exit(position=position, cur_price=cur_price):
                    exit_position(symbol, position)
                    op_mode = False
                    balance = current_balance()
                    post_message("현재 잔액 : "+str(balance)+" usd\n")
                else:
                    time.sleep(1)
                    continue
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            post_message("선물 거래 코드 에러 발생\n"+str(e)+"line:"+str(exc_tb.tb_lineno))
            time.sleep(1)
            continue

