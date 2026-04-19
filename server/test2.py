import numpy as np
import pandas as pd

class TradingEnv:
    def __init__(self, df, window_size=10):
        self.df = df
        self.window_size = window_size
        self.n_steps = len(df)
        
        # Trạng thái ban đầu
        self.reset()

    def reset(self):
        self.current_step = self.window_size
        self.done = False
        self.total_reward = 0
        self.inventory = [] # Lưu giá mua vào
        self.history = []   # Lưu lịch sử để vẽ biểu đồ
        return self._get_observation()

    def _get_observation(self):
        # Trả về cụm dữ liệu giá trong khoảng window_size
        return self.df.iloc[self.current_step - self.window_size : self.current_step].values

    def step(self, action):
        """
        Action: 0 = Đứng ngoài/Giữ, 1 = Mua, 2 = Bán
        """
        reward = 0
        current_price = self.df.iloc[self.current_step]['Close']
        
        # Logic xử lý hành động
        if action == 1: # Mua
            self.inventory.append(current_price)
            # print(f"Mua tại: {current_price}")
            
        elif action == 2 and len(self.inventory) > 0: # Bán
            buy_price = self.inventory.pop(0)
            reward = current_price - buy_price # Lãi/Lỗ thực tế
            self.total_reward += reward
            # print(f"Bán tại: {current_price} | Lãi: {reward}")

        # Sang bước tiếp theo
        self.current_step += 1
        if self.current_step >= self.n_steps - 1:
            self.done = True

        return self._get_observation(), reward, self.done