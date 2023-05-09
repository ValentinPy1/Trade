#!/usr/bin/python3
# -*- coding: iso-8859-1 -*
""" Python starter bot for the Crypto Trader games, from ex-Riddles.io """
__version__ = "1.0"

import sys
import numpy as np
from Api.BotState import BotState
import matplotlib.pyplot as plt

class Bot:
    def __init__(self):
        self.botState = BotState()
        self.dollars = 0
        self.bitcoins = 0
        self.opening_price = 0
        self.closing_price = 0
        self.btc_affordable = 0
        self.capital_invested = 0.45

        self.history = []

        self.short_ema_period = 10
        self.short_ema = 0
        self.long_ema_period = 25
        self.long_ema = 0

    def update_ema(self):
        if self.short_ema == 0:
            self.short_ema = self.closing_price
            self.long_ema = self.closing_price
        else:
            self.short_ema = self.short_ema * (1 - 2 / (self.short_ema_period + 1)) + self.closing_price * 2 / (self.short_ema_period + 1)
            self.long_ema = self.long_ema * (1 - 2 / (self.long_ema_period + 1)) + self.closing_price * 2 / (self.long_ema_period + 1)
        self.history.append({
            "opening_price": self.closing_price,
            "short_ema": self.short_ema,
            "long_ema": self.long_ema
        })

    def update(self):
        self.dollars = self.botState.stacks["USDT"]
        self.bitcoins = self.botState.stacks["BTC"]
        self.opening_price = self.botState.charts["USDT_BTC"].opens[-1]
        self.closing_price = self.botState.charts["USDT_BTC"].closes[-1]
        self.btc_affordable = self.dollars / self.closing_price

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            if self.botState.update(reading):
                self.update_ema()
                continue
            self.update()
            self.take_action()

    def buy(self):
        if self.dollars <= 1:
            print("no_moves", flush=True)
            return
        print(f'buy USDT_BTC {self.btc_affordable * self.capital_invested}', flush=True)
        print(f'buy USDT_BTC {self.btc_affordable * self.capital_invested}', file=sys.stderr, flush=True)

    def sell(self):
        if self.bitcoins <= 0.00001:
            print("no_moves", flush=True)
            return
        print(f'sell USDT_BTC {self.bitcoins * self.capital_invested}', flush=True)
        print(f'sell USDT_BTC {self.bitcoins * self.capital_invested}', file=sys.stderr, flush=True)

    def take_action(self):
        print("Balance: ", self.dollars, self.bitcoins, file=sys.stderr, flush=True)
        if self.short_ema > self.long_ema:
            self.buy()
        else:
            self.sell()


if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
    history = np.array(mybot.history)
    plt.plot(history[:, 0], label="opening_price")
    plt.plot(history[:, 1], label="short_ema")
    plt.plot(history[:, 2], label="long_ema")
    plt.legend()
    plt.show()