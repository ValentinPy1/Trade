##
## EPITECH PROJECT, 2022
## Trade
## File description:
## pandas_botstates.py
##

import pandas as pd

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        self.data = {}
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == 'pair':
                self.data[key] = value
            elif key == 'date':
                self.data[key] = int(value)
            else:
                self.data[key] = float(value)

    def __repr__(self):
        return str(self.data)

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
        self.data = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

    def update_chart(self, new_candle_str: str):
        new_candle = Candle(self.candleFormat, new_candle_str)
        self.data = self.data.append(new_candle.data, ignore_index=True)

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
            self.update_chart(value)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))

    def update(self, input : str):
        input = input.split(" ")
        if input[0] == "settings":
            self.update_settings(input[1], input[2])
            return 'settings'
        if input[0] == "update":
            self.update_game(input[2], input[3])
            return 'update'
        return 'action'

    def get_candle(self, index):
        return self.data.iloc[index]