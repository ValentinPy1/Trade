##
## EPITECH PROJECT, 2022
## Trade
## File description:
## plot_bot.py
##

import sys
import pandas as pd
import matplotlib.pyplot as plt

file = "training_set-new_set.csv"

def main(se_factor, le_factor):
    df = pd.read_csv(file)
    prices = df["close"].values
    short_ema = prices[0]
    long_ema = prices[0]
    history = []
    for i in range(1, len(prices)):
        short_ema = short_ema * (1 - se_factor) + prices[i] * se_factor
        long_ema = long_ema * (1 - le_factor) + prices[i] * le_factor
        prices[i] = prices[i]
        history.append({
            "price": prices[i],
            "short_ema": short_ema,
            "long_ema": long_ema
        })
    prices = [x["price"] for x in history]
    short_emas = [x["short_ema"] for x in history]
    long_emas = [x["long_ema"] for x in history]

    plt.plot(prices, label="prices")
    plt.plot(short_emas, label="short_ema")
    plt.plot(long_emas, label="long_ema")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 plot_bot.py short_ema long_ema")
        exit(84)
    try:
        short_ema = int(sys.argv[1])
        long_ema = int(sys.argv[2])
    except ValueError:
        print("Usage: python3 plot_bot.py short_ema long_ema")
        exit(84)
    short_ema_factor = 2 / (short_ema + 1)
    long_ema_factor = 2 / (long_ema + 1)
    main(short_ema_factor, long_ema_factor)