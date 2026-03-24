import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

# =========================
# 1. Đọc dữ liệu + cộng 100
# =========================
def read_prices(filename="train.csv"):
    df = pd.read_csv(filename)
    prices = df['Price'].dropna().values.astype(np.float32)
    prices = prices + 100
    return prices


# =========================
# 2. ZigZag Realtime
# =========================
class RealtimeZigZag:
    def __init__(self, threshold=0.03):
        self.threshold = threshold

        self.prices = []

        self.last_pivot_idx = 0
        self.last_pivot_price = None

        self.trend = None
        self.peaks = []
        self.valleys = []

    def update(self, price):
        self.prices.append(price)
        i = len(self.prices) - 1

        if self.last_pivot_price is None:
            self.last_pivot_price = price
            return None

        eps = 1e-8
        change = (price - self.last_pivot_price) / (self.last_pivot_price + eps)

        if self.trend is None:
            if abs(change) >= self.threshold:
                if change > 0:
                    self.valleys.append(self.last_pivot_idx)
                    self.trend = "up"
                else:
                    self.peaks.append(self.last_pivot_idx)
                    self.trend = "down"

                self.last_pivot_idx = i
                self.last_pivot_price = price

                return ("init", i, price)

        elif self.trend == "up":
            if price > self.last_pivot_price:
                self.last_pivot_idx = i
                self.last_pivot_price = price

            elif (self.last_pivot_price - price) / (self.last_pivot_price + eps) >= self.threshold:
                self.peaks.append(self.last_pivot_idx)
                self.trend = "down"
                self.last_pivot_idx = i
                self.last_pivot_price = price

                return ("peak", self.last_pivot_idx, self.last_pivot_price)

        elif self.trend == "down":
            if price < self.last_pivot_price:
                self.last_pivot_idx = i
                self.last_pivot_price = price

            elif (price - self.last_pivot_price) / (self.last_pivot_price + eps) >= self.threshold:
                self.valleys.append(self.last_pivot_idx)
                self.trend = "up"
                self.last_pivot_idx = i
                self.last_pivot_price = price

                return ("valley", self.last_pivot_idx, self.last_pivot_price)

        return None


# =========================
# 3. Backtest + Trading Logic
# =========================
prices = read_prices()

zz = RealtimeZigZag(threshold=0.03)

x_data = []
y_data = []

position = None   # None / "LONG"
entry_price = 0
profit = 0

trades = []  # lưu lịch sử giao dịch

plt.ion()
fig, ax = plt.subplots(figsize=(14, 6))


def update_plot():
    ax.clear()

    ax.plot(x_data, y_data, label="Price")

    if zz.peaks:
        px = zz.peaks
        py = [y_data[i] for i in px]
        ax.scatter(px, py, color='red', marker='v', label="SELL (Peak)")

    if zz.valleys:
        vx = zz.valleys
        vy = [y_data[i] for i in vx]
        ax.scatter(vx, vy, color='green', marker='^', label="BUY (Valley)")

    ax.legend()
    ax.grid(True)
    plt.pause(0.01)


# =========================
# 4. RUN STREAM
# =========================
for i in range(len(prices)):
    price = prices[i]

    x_data.append(i)
    y_data.append(price)

    signal = zz.update(price)

    # ================= BUY =================
    if signal and signal[0] == "valley":
        if position is None:
            position = "LONG"
            entry_price = price
            trades.append(("BUY", i, price))
            print(f"BUY at {price}")

    # ================= SELL =================
    elif signal and signal[0] == "peak":
        if position == "LONG":
            pnl = price - entry_price
            profit += pnl
            trades.append(("SELL", i, price))
            print(f"SELL at {price} | PnL: {pnl}")

            position = None
            entry_price = 0

    update_plot()
    time.sleep(0.1)

plt.ioff()
plt.show()

print("Total Profit:", profit)