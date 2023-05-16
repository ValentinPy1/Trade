#!/usr/bin/python3
# -*- coding: iso-8859-1 -*
""" Python starter bot for the Crypto Trader games, from ex-Riddles.io """
__version__ = "1.0"

import sys
import numpy as np
from Api.trade import BotState

class Bot:
    def __init__(self, args):
        self.args = args

        self.botState = BotState()
        self.dollars = 0
        self.bitcoins = 0
        self.opening_price = 0
        self.closing_price = 0
        self.btc_affordable = 0
        self.short_ema = 0
        self.long_ema = 0
        self.last_action = self.args["action_interval"]

        self.history = []

    def update_ema(self):
        self.opening_price = self.botState.charts["USDT_BTC"].opens[-1]
        self.closing_price = self.botState.charts["USDT_BTC"].closes[-1]
        if self.short_ema == 0:
            self.short_ema = self.closing_price
            self.long_ema = self.closing_price
        else:
            self.short_ema = self.short_ema * (1 - 2 / (self.args["short_ema_period"] + 1)) + self.closing_price * 2 / (self.args["short_ema_period"] + 1)
            self.long_ema = self.long_ema * (1 - 2 / (self.args["long_ema_period"] + 1)) + self.closing_price * 2 / (self.args["long_ema_period"] + 1)
        self.history.append({
            "closing_price": self.closing_price,
            "short_ema": self.short_ema,
            "long_ema": self.long_ema
        })

    def update(self):
        self.dollars = self.botState.stacks["USDT"]
        self.bitcoins = self.botState.stacks["BTC"]
        self.btc_affordable = self.dollars / self.closing_price

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            state = self.botState.update(reading)
            if state == 'update':
                self.update_ema()
                continue
            elif state == 'action':
                self.update()
                self.take_action()

    def buy(self):
        if self.dollars == 0:
            # print("Balance: ", self.dollars, self.bitcoins, file=sys.stderr, flush=True)
            print("no_moves", flush=True)
            return
        print(f'buy USDT_BTC {self.btc_affordable * self.args["capital_invested"]}', flush=True)
        self.last_action = 0
        # print(f'buy USDT_BTC {self.btc_affordable * self.args["capital_invested"]}', file=sys.stderr, flush=True)

    def sell(self):
        if self.bitcoins == 0:
            # print("Balance: ", self.dollars, self.bitcoins, file=sys.stderr, flush=True)
            print("no_moves", flush=True)
            return
        print(f'sell USDT_BTC {self.bitcoins * self.args["capital_invested"]}', flush=True)
        self.last_action = 0
        # print(f'sell USDT_BTC {self.bitcoins * self.args["capital_invested"]}', file=sys.stderr, flush=True)

    def take_action(self):
        if self.last_action < self.args["action_interval"]:
            self.last_action += 1
            print("no_moves", flush=True)
            return
        trigger_buy = self.short_ema - self.long_ema > self.args["diff_threshold"]
        trigger_sell = self.long_ema - self.short_ema > self.args["diff_threshold"]
        for i in range(1, self.args["duration_treshold"]):
            trigger_buy = trigger_buy and self.history[-i]["short_ema"] - self.history[-i]["long_ema"] > self.args["diff_threshold"]
            trigger_sell = trigger_sell and self.history[-i]["long_ema"] - self.history[-i]["short_ema"] > self.args["diff_threshold"]
        if trigger_buy:
            self.buy()
        elif trigger_sell:
            self.sell()
        else:
            print("no_moves", flush=True)


if __name__ == "__main__":
    args = {
        "capital_invested": 1,
        "short_ema_period": 10,
        "long_ema_period": 25,
        "action_interval": 30,
        "diff_threshold": 0.3,
        "duration_treshold": 5
    }
    mybot = Bot(args)
    mybot.run()
