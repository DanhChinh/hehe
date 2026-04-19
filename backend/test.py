import gymnasium as gym
import gym_anytrading
from gym_anytrading.envs import StocksEnv
import pandas as pd

# 1. Giả sử bạn có file CSV dữ liệu giá
# df = pd.read_csv('data.csv') 

# Ở đây tôi dùng dữ liệu mẫu có sẵn trong thư viện
from gym_anytrading.datasets import STOCKS_GOOGL

df = STOCKS_GOOGL.copy()

print(df.head())

# # Định nghĩa hàm tạo môi trường
# def make_env():
#     env = gym.make('stocks-v0', df=df, frame_bound=(10, 100), window_size=10)
#     return env

# env = make_env()



# from stable_baselines3 import PPO

# # Khởi tạo model
# # MlpPolicy: Mạng thần kinh đa lớp (Multi-layer Perceptron)
# model = PPO("MlpPolicy", env, verbose=1, 
#             learning_rate=0.0003, 
#             device='cpu') # Có thể đổi thành 'cuda' nếu có GPU

# # --- BƯỚC 3.1: Huấn luyện ---
# print("Đang bắt đầu huấn luyện...")
# model.learn(total_timesteps=20000)

# # --- BƯỚC 3.2: Kiểm thử (Backtesting) ---
# print("Đang kiểm tra hiệu suất...")
# obs, info = env.reset()
# while True:
#     # Model dự đoán hành động dựa trên quan sát (giá hiện tại)
#     action, _states = model.predict(obs, deterministic=True)
    
#     # Thực hiện hành động vào môi trường
#     obs, reward, terminated, truncated, info = env.step(action)
    
#     if terminated or truncated:
#         print("Kết quả cuối cùng:", info)
#         break

# # Hiển thị biểu đồ kết quả
# import matplotlib.pyplot as plt

# plt.figure(figsize=(15,6))
# plt.cla()
# env.unwrapped.render_all()
# plt.show()