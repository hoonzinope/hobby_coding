import pyupbit
import numpy as np
import time

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
 
def get_coin():
    tickers = ['KRW-BTC',"KRW-ETH","KRW-ETC",'KRW-XRP','KRW-ADA','KRW-BCH','KRW-XLM']
 
    hprs = []
    for ticker in tickers:
        hpr = get_hpr(ticker)
        hprs.append((ticker, hpr))

    sorted_hprs = sorted(hprs, key=lambda x:x[1], reverse=True)
    return sorted_hprs[:1][0][0]

print(get_coin())