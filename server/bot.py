import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

# ================= DATA =================
def read_csv_add100(filename):
    df = pd.read_csv(filename)
    prices = df['Price'].dropna().values
    return prices.astype(np.float32)


# ================= AGENT =================
class TradingAgent:
    def __init__(self):
        self.q = {}
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 1.0
        self.actions = [0, 1, 2]

    def _discretize(self, x):
        return int(np.round(x * 10))  # giảm state space

    def get_state(self, i, prices, buy_price, holding):
        window = prices[max(0, i-10):i]

        if len(window) < 2:
            return "INIT"

        returns = (window[-1] - window[0]) / (window[0] + 1e-8)
        momentum = window[-1] - window[-2]

        returns = self._discretize(returns)
        momentum = self._discretize(momentum)

        if holding:
            profit = (prices[i] - buy_price) / (buy_price + 1e-8)
            profit = self._discretize(profit)
            return (returns, momentum, 1, profit)

        return (returns, momentum, 0, 0)

    def act(self, s):
        if s not in self.q:
            self.q[s] = [0.0, 0.0, 0.0]

        if random.random() < self.epsilon:
            return random.choice(self.actions)

        return np.argmax(self.q[s])

    def update(self, s, a, r, s2):
        if s2 not in self.q:
            self.q[s2] = [0.0, 0.0, 0.0]

        self.q[s][a] += self.alpha * (
            r + self.gamma * max(self.q[s2]) - self.q[s][a]
        )


# ================= TRAIN =================
def train_agent(prices, epochs=5000):
    agent = TradingAgent()

    for ep in range(epochs):
        i = 10
        holding = False
        buy_price = 0

        while i < len(prices) - 1:
            s = agent.get_state(i, prices, buy_price, holding)
            a = agent.act(s)

            reward = 0

            # BUY
            if a == 1 and not holding:
                holding = True
                buy_price = prices[i]

            # SELL
            elif a == 2 and holding:
                profit = (prices[i] - buy_price) / buy_price
                reward = profit
                holding = False

            # HOLD
            elif holding:
                reward = (prices[i+1] - prices[i]) / prices[i]

            i += 1
            s2 = agent.get_state(i, prices, buy_price, holding)
            agent.update(s, a, reward, s2)

        # decay epsilon
        agent.epsilon = max(0.01, agent.epsilon * 0.995)

        if ep % 500 == 0:
            print(f"Epoch {ep}, epsilon={agent.epsilon:.3f}")

    return agent


# ================= TEST =================
def test_agent(agent, prices):
    i = 10
    holding = False
    buy_idx, sell_idx = None, None
    buy_price = 0

    while i < len(prices) - 1:
        s = agent.get_state(i, prices, buy_price, holding)
        a = np.argmax(agent.q.get(s, [0,0,0]))

        if a == 1 and not holding:
            holding = True
            buy_price = prices[i]
            buy_idx = i

        elif a == 2 and holding:
            sell_idx = i
            break

        i += 1

    # plot
    plt.figure(figsize=(12,6))
    plt.plot(prices)

    if buy_idx:
        plt.scatter(buy_idx, prices[buy_idx], color='green', s=100)
    if sell_idx:
        plt.scatter(sell_idx, prices[sell_idx], color='red', s=100)

    plt.title("Single Trade Result")
    plt.show()

import matplotlib.pyplot as plt
import pandas as pd

def plot_market_chart(prices, buy_points=None, sell_points=None, title="Phân Tích Biểu Đồ Giao Dịch"):
    """
    Hàm vẽ biểu đồ giá chuyên nghiệp.
    - prices: List hoặc mảng Numpy chứa giá thị trường.
    - buy_points: List các tuple (index, price) - ví dụ: [(10, 105), (35, 110)]
    - sell_points: List các tuple (index, price) - ví dụ: [(20, 108), (50, 115)]
    """
    # 1. Khởi tạo khung hình
    plt.figure(figsize=(15, 7), facecolor='#f4f4f4')
    ax = plt.gca()
    ax.set_facecolor('#ffffff')

    # 2. Vẽ đường giá chính (Đường nét liền, màu xanh đậm)
    plt.plot(prices, label='Giá Thị Trường', color='#2c3e50', linewidth=2, alpha=0.8, zorder=1)

    # 3. Vẽ điểm MUA (Mũi tên hướng lên - màu xanh lá)
    if buy_points:
        b_idx, b_val = zip(*buy_points)
        plt.scatter(b_idx, b_val, color='#27ae60', label='Lệnh MUA', 
                    marker='^', s=180, edgecolors='black', linewidths=1.2, zorder=5)

    # 4. Vẽ điểm BÁN (Mũi tên hướng xuống - màu đỏ)
    if sell_points:
        s_idx, s_val = zip(*sell_points)
        plt.scatter(s_idx, s_val, color='#e74c3c', label='Lệnh BÁN', 
                    marker='v', s=180, edgecolors='black', linewidths=1.2, zorder=5)

    # 5. Định dạng trục và lưới
    plt.title(title, fontsize=18, fontweight='bold', color='#2c3e50', pad=20)
    plt.xlabel("Thời gian (Steps)", fontsize=12, fontweight='bold')
    plt.ylabel("Mức Giá (Value)", fontsize=12, fontweight='bold')
    
    plt.grid(True, linestyle='--', alpha=0.5, color='#bdc3c7')
    plt.legend(loc='best', fontsize=11, frameon=True, shadow=True)

    # Tối ưu hóa hiển thị
    plt.tight_layout()
    plt.show()

# --- VÍ DỤ CÁCH DÙNG SAU KHI ĐỌC CSV ---
def example_usage():
    # Giả sử bạn đọc file CSV đã lưu trước đó
    # df = pd.read_csv("market_data.csv")
    # prices = df['Price'].tolist()
    
    # Dữ liệu giả định để test hàm
    test_prices = [100, 102, 101, 105, 108, 107, 106, 110, 115, 112, 110, 108, 105]
    buys = [(3, 105), (7, 110)]  # Mua ở bước 3 và bước 7
    sells = [(5, 108), (9, 112)] # Bán ở bước 5 và bước 9

    plot_market_chart(test_prices, buy_points=buys, sell_points=sells, title="Kết Quả Chạy Model AI")



def get_zigzag(prices, threshold=0.05):
    """
    threshold: 0.05 tương đương với biến động 5%
    """


    zigzag = [(0, prices[0])]  # Lưu (index, price)
    trend = None  # 1 là đang lên, -1 là đang xuống

    for i in range(1, len(prices)):
        last_idx, last_price = zigzag[-1]
        diff = (prices[i] - last_price) / last_price

        if trend is None:
            if diff >= threshold:
                trend = 1
                zigzag.append((i, prices[i]))
            elif diff <= -threshold:
                trend = -1
                zigzag.append((i, prices[i]))
            continue

        if trend == 1: # Đang trong xu hướng tăng
            if prices[i] > last_price:
                # Nếu giá cao hơn, cập nhật đỉnh mới tại vị trí hiện tại
                zigzag[-1] = (i, prices[i])
            elif diff <= -threshold:
                # Nếu giá quay đầu giảm quá ngưỡng, xác nhận đáy mới
                trend = -1
                zigzag.append((i, prices[i]))

        else: # trend == -1 (Đang trong xu hướng giảm)
            if prices[i] < last_price:
                # Nếu giá thấp hơn, cập nhật đáy mới
                zigzag[-1] = (i, prices[i])
            elif diff >= threshold:
                # Nếu giá quay đầu tăng quá ngưỡng, xác nhận đỉnh mới
                trend = 1
                zigzag.append((i, prices[i]))

    return zigzag

# Ví dụ áp dụng
prices = read_csv_add100("train.csv")
result = get_zigzag(prices, threshold=0.05)

print("Các điểm xoay (Pivot points):")
for idx, val in result:
    print(f"Index {idx}: Giá {val}")
# ================= MAIN =================
plot_market_chart(prices)
