import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter
import json

t = []

with open("history/decision_tree.json", 'r', encoding='utf-8') as f:
    t = json.load(f)




df = pd.DataFrame({'price': np.cumsum(t)})

# 2. Làm mượt dữ liệu (Smoothing)
# Giúp loại bỏ các răng cưa nhỏ để tránh bắt nhầm đỉnh/đáy ảo
df['smoothed'] = savgol_filter(df['price'], window_length=29, polyorder=3)

# 3. Thuật toán tìm Đỉnh (Peaks) và Đáy (Troughs)
# distance: khoảng cách tối thiểu giữa 2 đỉnh
# prominence: độ cao tối thiểu của đỉnh so với vùng lân cận
peaks, _ = find_peaks(df['smoothed'], distance=10, prominence=10)
troughs, _ = find_peaks(-df['smoothed'], distance=10, prominence=10)

# 4. Hiển thị kết quả
plt.figure(figsize=(12, 6))
plt.plot(df['price'], label='Giá gốc (Nhiễu)', alpha=0.3, color='gray')
plt.plot(df['smoothed'], label='Đường đã làm mượt', color='blue', linewidth=2)

# Đánh dấu Đỉnh (Đỏ) và Đáy (Xanh)
plt.plot(peaks, df['smoothed'].iloc[peaks], "v", color='red', label='Đỉnh (Peak)')
plt.plot(troughs, df['smoothed'].iloc[troughs], "^", color='green', label='Đáy (Trough)')

plt.title("Tiền xử lý và Phát hiện Đỉnh/Đáy")
plt.legend()
plt.show()

# 5. Xuất dữ liệu để đưa vào AI training
# Bạn có thể tạo cột nhãn: 1 cho đỉnh, -1 cho đáy, 0 cho các điểm còn lại
df['label'] = 0
df.loc[peaks, 'label'] = 1
df.loc[troughs, 'label'] = -1

print(df)