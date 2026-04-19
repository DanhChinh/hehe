import numpy as np

class ZigZagTradingBot:
    def __init__(self, threshold=0.03):
        self.threshold = threshold

        self.prices = []

        self.last_pivot_idx = 0
        self.last_pivot_price = None

        self.trend = None
        self.position = None  # None / "LONG"

        self.peaks = []
        self.valleys = []

    def reset(self):
        self.__init__(self.threshold)

    def _zigzag_update(self, price):
        """
        Core ZigZag logic
        """
        self.prices.append(price)
        i = len(self.prices) - 1

        if self.last_pivot_price is None:
            self.last_pivot_price = price
            return None

        eps = 1e-8
        change = (price - self.last_pivot_price) / (self.last_pivot_price + eps)

        signal = None

        # chưa có trend
        if self.trend is None:
            if abs(change) >= self.threshold:
                if change > 0:
                    self.valleys.append(self.last_pivot_idx)
                    self.trend = "up"
                    signal = "BUY"
                else:
                    self.peaks.append(self.last_pivot_idx)
                    self.trend = "down"
                    signal = "SELL"

                self.last_pivot_idx = i
                self.last_pivot_price = price

        elif self.trend == "up":
            if price > self.last_pivot_price:
                self.last_pivot_idx = i
                self.last_pivot_price = price

            elif (self.last_pivot_price - price) / (self.last_pivot_price + eps) >= self.threshold:
                self.peaks.append(self.last_pivot_idx)
                self.trend = "down"
                self.last_pivot_idx = i
                self.last_pivot_price = price
                signal = "SELL"

        elif self.trend == "down":
            if price < self.last_pivot_price:
                self.last_pivot_idx = i
                self.last_pivot_price = price

            elif (price - self.last_pivot_price) / (self.last_pivot_price + eps) >= self.threshold:
                self.valleys.append(self.last_pivot_idx)
                self.trend = "up"
                self.last_pivot_idx = i
                self.last_pivot_price = price
                signal = "BUY"

        return signal

    def update(self, price):
        """
        Public method dùng cho bot runtime

        Input:
            price: giá mới (float)

        Output:
            "BUY" / "SELL" / None
        """

        signal = self._zigzag_update(price)

        # ===== Trading logic =====
        if signal == "BUY" and self.position is None:
            self.position = "LONG"
            return "BUY"

        elif signal == "SELL" and self.position == "LONG":
            self.position = None
            return "SELL"

        return None


# =========================
# Example usage
# =========================
# if __name__ == "__main__":
#     bot = ZigZagTradingBot(threshold=0.03)

#     prices = [100, 101, 102, 105, 110, 108, 106, 104, 107, 111, 109]

#     for p in prices:
#         action = bot.update(p)

#         if action:
#             print(f"Action: {action} at price {p}")