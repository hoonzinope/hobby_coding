import pyupbit
import datetime
import time, calendar
import numpy as np
import requests
import telegram as tel
import json

token = ""
id_ = ""
access = ""
secret = ""

with open("secret.json", "r") as temp_json:
    temp_dict = json.load(temp_json)

    token = temp_dict['token']
    id_ = temp_dict['id']
    access = temp_dict['access']
    secret = temp_dict['secret']

def get_ma7(coin):
    """7일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(coin, interval="day", count=7)
    ma7 = df['close'].rolling(7).mean().iloc[-1]
    return ma7

def get_hpr(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker, interval = "day", count = 21)
        df['ma7'] = df['close'].rolling(window=7).mean().shift(1)
        df['range'] = (df['high'] - df['low']) * 0.5
        df['target'] = df['open'] + df['range'].shift(1)
        df['bull'] = df['open'] > df['ma7']
 
        fee = 0.0005
        df['ror'] = np.where((df['high'] > df['target']) & df['bull'],
                            df['close'] / df['target'] - fee,
                            1)

        df['hpr'] = df['ror'].cumprod()
        df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
        return df['hpr'][-2]
    except:
        return 1
 
def get_coin(tickers):
    hprs = []
    for ticker in tickers:
        hpr = get_hpr(ticker)
        hprs.append((ticker, hpr))

    sorted_hprs = sorted(hprs, key=lambda x:x[1], reverse=True)
    return sorted_hprs[:1][0][0]

def post_message(text):
    bot = tel.Bot(token=token)
    chat_id = id_
    bot.sendMessage(chat_id=chat_id, text=text) # 메세지 보내기

def get_targetPrice(df, K) :
    range = df['high'][-2] - df['low'][-2]
    return df['open'][-1] + range * K

def buy_all(coin) :
    balance = upbit.get_balance("KRW") * 0.9995
    if balance >= 5000 :
        print(upbit.buy_market_order(coin, balance))
        post_message(coin+" 매수 체결.\n체결 단가 : "+str(pyupbit.get_current_price(coin))+" 원")

def sell_all(coin) :
    balance = upbit.get_balance(coin)
    price = pyupbit.get_current_price(coin)
    if price * balance >= 5000 :
        print(upbit.sell_market_order(coin, balance))
        post_message(coin+" 매도 체결.\n체결 단가 : "+str(pyupbit.get_current_price(coin))+" 원")

def check_loss(coin, target_price) : # stop loss 로직 추가
    curr_price = pyupbit.get_current_price(coin)
    profit = (curr_price - target_price) / target_price * 100
    if profit > 5 or profit < -10: #수익이 5% 이상이거나, -10% 라면 true!
        return True
    else:
        return False

def get_crr(df, fees, K) :
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    df['targetPrice'] = df['open'] + df['range'] * K
    df['drr'] = np.where(df['high'] > df['targetPrice'], (df['close'] / (1 + fees)) / (df['targetPrice'] * (1 + fees)) , 1)
    return df['drr'].cumprod()[-2]

def get_best_K(coin, fees) :
    df = pyupbit.get_ohlcv(coin, interval = "day", count = 21)
    max_crr = 0
    best_K = 0.5
    for k in np.arange(0.1, 1.0, 0.1) :
        crr = get_crr(df, fees, k)
        if crr > max_crr :
            max_crr = crr
            best_K = k
    return best_K

def get_coin_ver2(tickers): # K값이 가장 작은 코인을 선택
    fee = 0.005
    recommand = []
    for coin in tickers:
        recommand.append([coin, get_best_K(coin,fee)])
    sorted_recomm = sorted(recommand, key=lambda x : x[1])
    return sorted_recomm[0][0]

if __name__ == '__main__': 
    try:
        upbit = pyupbit.Upbit(access, secret)

        # set variables
        coin = "KRW-BTC"
        tickers = ['KRW-BTC',"KRW-ETH","KRW-ETC",'KRW-XRP','KRW-ADA','KRW-BCH',"KRW-DOT",'KRW-XLM']
 
        try:
            coin = get_coin_ver2(tickers=tickers)
        except:
            coin = "KRW-BTC"

        fees = 0.0005
        K = 0.5
        
        ma7 = get_ma7(coin)
        start_balance = upbit.get_balance("KRW")
        df = pyupbit.get_ohlcv(coin, count = 2, interval = "day")
        targetPrice = get_targetPrice(df, get_best_K(coin, fees))
        print(datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S'), "\t\tBalance :", start_balance, "KRW \t\tYield :", ((start_balance / start_balance) - 1) * 100, "% \t\tNew targetPrice :", targetPrice, "KRW")
        post_message("자동매매를 시작합니다.\n잔액 : "+str(start_balance)+" 원\n"+coin+" 목표매수가 : "+str(targetPrice)+" 원")

        while True :
            now = datetime.datetime.now()
            if now.hour == 9 and now.minute == 2 :    # when am 09:02:00
                sell_all(coin)
                time.sleep(10)
                
                try:
                    coin = get_coin_ver2(tickers=tickers)
                except:
                    coin = "KRW-BTC"

                df = pyupbit.get_ohlcv(coin, count = 2, interval = "day")
                targetPrice = get_targetPrice(df, get_best_K(coin, fees))
                ma7 = get_ma7(coin)

                cur_balance = upbit.get_balance("KRW")
                print(now.strftime('%y/%m/%d %H:%M:%S'), "\t\tBalance :", cur_balance, "KRW \t\tYield :", ((cur_balance / start_balance) - 1) * 100, "% \t\tNew targetPrice :", targetPrice, "KRW")
                post_message("새로운 장 시작\n수익률 : "+str(((cur_balance / start_balance) - 1) * 100)+" %\n잔액 : "+str(cur_balance)+" 원\n"+coin+" 목표매수가 : "+str(targetPrice)+" 원")
                time.sleep(60)
            else:
                balance = upbit.get_balance(coin) # 코인을 구매했다면 
                if balance > 0: # 코인의 수량이 0 보다 큼
                    if check_loss(coin=coin, target_price= targetPrice): # 목표치에 도달 혹은 손실량이 기준치에 도달 체크
                        sell_all(coin) # 도달했다면 바로 팔기
                        time.sleep(10)

                        start_time = df.index[-1] # 팔고 내일 9시 2분까지 손떼
                        end_time = start_time + datetime.timedelta(days=1)
                        end_time += datetime.timedelta(minutes=2)
                        if end_time > now :
                            time.sleep((end_time - now).seconds)
                else: # 코인을 산게 없다면 일단 사기 (전액)
                    if targetPrice <= pyupbit.get_current_price(coin) and ma7 <= pyupbit.get_current_price(coin):
                        buy_all(coin)
    
            time.sleep(1)

    except Exception as e:
        print(e)
        post_message("error occured! check code please!")
        time.sleep(1)