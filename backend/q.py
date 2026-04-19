import numpy as np
import random
import json
import os

class QTradingBot:
    def __init__(self, window_size=10, alpha=0.1, gamma=0.9, epsilon=0.1, filename="q_table.json"):
        self.window_size = window_size
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.filename = filename
        self.q_table = self.load_q_table()

    def load_q_table(self):
        """Tải Q-table từ file, nếu không có thì tạo mới."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                print(f"--- Đã tải Q-table từ {self.filename} ---")
                return json.load(f)
        return {}

    def save_q_table(self):
        """Lưu Q-table vào file dưới dạng JSON."""
        with open(self.filename, 'w') as f:
            json.dump(self.q_table, f, indent=4)

    def get_state(self, history):
        return ",".join(map(str, history[-self.window_size:]))

    def choose_action(self, state, train=True):
        if train:
            if state not in self.q_table:
                self.q_table[state] = [0.0, 0.0]
                return random.choice([0, 1])
            if random.uniform(0, 1) < self.epsilon:
                return random.choice([0, 1])
            return np.argmax(self.q_table[state])
        if state not in self.q_table:
            return 0
        return np.argmax(self.q_table[state])

    def update_q(self, state, action, reward, next_state):
        # print(f"--- Cập nhật Q-table ---\nState: {state}\nAction: {'VÀO LỆNH' if action == 1 else 'ĐỨNG NGOÀI'}\nReward: {reward}\nNext State: {next_state}")
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0, 0.0]
        
        # Công thức Bellman
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value




