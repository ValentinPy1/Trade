#!/usr/bin/python3
# -*- coding: iso-8859-1 -*
""" Python starter bot for the Crypto Trader games, from ex-Riddles.io """
__version__ = "1.0"

import sys
import numpy as np
import tensorflow as tf
from keras.models import load_model
import pandas as pd
import pandas_ta as ta

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            if key == "date":
                self.date = int(value)
            if key == "high":
                self.high = float(value)
            if key == "low":
                self.low = float(value)
            if key == "open":
                self.open = float(value)
            if key == "close":
                self.close = float(value)
            if key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)


class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)


class BotState:
    def __init__(self):
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = dict()
        self.charts = dict()

    def update_chart(self, pair: str, new_candle_str: str):
        if not (pair in self.charts):
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        if key == "time_per_move":
            self.timePerMove = int(value)
        if key == "candle_interval":
            self.candleInterval = int(value)
        if key == "candle_format":
            self.candleFormat = value.split(",")
        if key == "candles_total":
            self.candlesTotal = int(value)
        if key == "candles_given":
            self.candlesGiven = int(value)
        if key == "initial_stack":
            self.initialStack = int(value)
        if key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))

    def update(self, input : str):
        input = input.split(" ")
        if input[0] == "update":
            self.update_game(input[2], input[3])
            return 'update'
        if input[0] == "settings":
            self.update_settings(input[1], input[2])
            return 'settings'
        return 'action'



class Bot:
    def __init__(self, args):
        self.args = args

        self.botState = BotState()
        self.dollars = 0
        self.bitcoins = 0
        self.btc_affordable = 0

        self.history = pd.DataFrame(columns=['Open', 'High', 'Low', 'Adj Close', 'RSI', 'EMAF', 'EMAM', 'EMAS', 'Target', 'TargetClass'])

        self.model = load_model('/home/vpy/delivery/2year/CNA/Trade/Experiments/LSTM_BTC_1.h5')

# data['RSI']=ta.rsi(data.Close, length=15)
# data['EMAF']=ta.ema(data.Close, length=20)
# data['EMAM']=ta.ema(data.Close, length=100)
# data['EMAS']=ta.ema(data.Close, length=150)

# data['Target'] = data['Adj Close']-data.Open
# data['Target'] = data['Target'].shift(-1)

# data['TargetClass'] = [1 if data.Target[i]>0 else 0 for i in range(len(data))]

# data['TargetNextClose'] = data['Adj Close'].shift(-1)

# data.dropna(inplace=True)
# data.reset_index(inplace = True)
# data.drop(['Volume', 'Close', 'Datetime'], axis=1, inplace=True)

    def update(self):
        self.dollars = self.botState.stacks["USDT"]
        self.bitcoins = self.botState.stacks["BTC"]
        closing_price = self.botState.charts["USDT_BTC"].closes[-1]
        self.btc_affordable = self.dollars / closing_price

        rsi = ta.rsi(self.botState.charts["USDT_BTC"].closes, length=15)
        emaf = ta.ema(self.botState.charts["USDT_BTC"].closes, length=20)
        emam = ta.ema(self.botState.charts["USDT_BTC"].closes, length=100)
        emas = ta.ema(self.botState.charts["USDT_BTC"].closes, length=150)
        target = [self.botState.charts["USDT_BTC"].closes[i] - self.botState.charts["USDT_BTC"].opens[i] for i in range(len(self.botState.charts["USDT_BTC"].closes))]
        targetclass = [1 if target[i] > 0 else 0 for i in range(len(target))]

        entry = {
            "Open" : self.botState.charts["USDT_BTC"].opens[-1],
            "High" : self.botState.charts["USDT_BTC"].highs[-1],
            "Low" : self.botState.charts["USDT_BTC"].lows[-1],
            "Adj Close" : self.botState.charts["USDT_BTC"].closes[-1],
            "RSI" : rsi[-1],
            "EMAF" : emaf[-1],
            "EMAM" : emam[-1],
            "EMAS" : emas[-1],
            "Target" : target[-1],
            "TargetClass" : targetclass[-1]
        }
        self.history.append(entry)

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            state = self.botState.update(reading)
            if state == 'update':
                continue
            elif state == 'action':
                self.update()
                self.take_action()

    def buy(self):
        if self.dollars == 0:
            print("Balance: ", self.dollars, self.bitcoins, file=sys.stderr, flush=True)
            print("no_moves", flush=True)
            return
        print(f'buy USDT_BTC {self.btc_affordable * self.args["capital_invested"]}', flush=True)
        print(f'buy USDT_BTC {self.btc_affordable * self.args["capital_invested"]}', file=sys.stderr, flush=True)

    def sell(self):
        if self.bitcoins == 0:
            print("Balance: ", self.dollars, self.bitcoins, file=sys.stderr, flush=True)
            print("no_moves", flush=True)
            return
        print(f'sell USDT_BTC {self.bitcoins * self.args["capital_invested"]}', flush=True)
        print(f'sell USDT_BTC {self.bitcoins * self.args["capital_invested"]}', file=sys.stderr, flush=True)

# from sklearn.preprocessing import MinMaxScaler
# sc = MinMaxScaler(feature_range=(0,1))
# data_set_scaled = sc.fit_transform(data_set)
# print(data_set_scaled)

# # multiple feature from data provided to the model
# X = []
# #print(data_set_scaled[0].size)
# #data_set_scaled=data_set.values
# backcandles = 30
# print(data_set_scaled.shape[0])
# for j in range(8):#data_set_scaled[0].size):#2 columns are target not X
#     X.append([])
#     for i in range(backcandles, data_set_scaled.shape[0]):#backcandles+2
#         X[j].append(data_set_scaled[i-backcandles:i, j])

# #move axis from 0 to position 2
# X=np.moveaxis(X, [0], [2])

# #Erase first elements of y because of backcandles to match X length
# #del(yi[0:backcandles])
# #X, yi = np.array(X), np.array(yi)
# # Choose -1 for last column, classification else -2...
# X, yi =np.array(X), np.array(data_set_scaled[backcandles:,-2])
# y=np.reshape(yi,(len(yi),1))
# #y=sc.fit_transform(yi)
# #X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
# print(X)
# print(X.shape)
# print(y)
# print(y.shape)
    def prepare_input_data(self):
        X = []
        for i in range(len(self.history) - self.args["period_length"], len(self.history)):
            X.append([])
            for key in self.history[i]:
                X[-1].append(self.history[i][key])
        X = np.array(X)
        X = np.reshape(X, (1, X.shape[0], X.shape[1]))
        return X

    def take_action(self):
        if len(self.history) < self.args["period_length"]:
            print("no_moves", flush=True)
            return
        X = self.prepare_input_data()
        y = self.model.predict(X)
        if y[0][0] > 0.5:
            self.buy()
        else:
            self.sell()



if __name__ == "__main__":
    args = {
        "capital_invested": 0.1,
        "period_length": 30
    }
    mybot = Bot(args)
    mybot.run()
