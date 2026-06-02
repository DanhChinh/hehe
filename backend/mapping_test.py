import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score

def stop():
    print("Đã dừng chương trình.")
    exit()

warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt

def plot_all_pattern_waves(pattern_waves):
    """
    Vẽ toàn bộ các chuỗi tích lũy từ danh sách pattern_waves.
    Mỗi chuỗi đại diện cho một đoạn SID liên tục trong Part 2.
    """
    if not pattern_waves:
        print("Dữ liệu pattern_waves trống, không thể vẽ.")
        return

    # Thiết lập phong cách đồ thị
    plt.figure(figsize=(14, 7))
    plt.style.use('seaborn-v0_8-darkgrid') # Nếu không có style này có thể dùng 'ggplot'
    
    # Vẽ từng wave
    for i, wave in enumerate(pattern_waves):
        # Chúng ta vẽ từ gốc 0 để dễ dàng so sánh biên độ và hình dáng các sóng với nhau
        plt.plot(wave, alpha=0.6, linewidth=1.5, label=f'Wave {i}' if len(pattern_waves) < 15 else None)

    # Thêm đường tham chiếu 0 (điểm cân bằng giữa đúng và sai)
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.4, label='Break-even')

    # Định dạng biểu đồ
    plt.title(f"Phân tích {len(pattern_waves)} chuỗi dự đoán tích lũy (Pattern Waves - Part 2)", fontsize=14)
    plt.xlabel("Số phiên liên tục (Relative SID)", fontsize=12)
    plt.ylabel("Điểm tích lũy (Đúng +1 / Sai -1)", fontsize=12)
    
    if len(pattern_waves) < 15:
        plt.legend()
    
    plt.tight_layout()
    plt.show()

# --- CÁCH SỬ DỤNG TRONG LUỒNG CỦA BẠN ---
# 1. Khởi tạo wave engine với model đã train
# wave_engine = PredictionWave(model)
# 2. Tạo ra danh sách các mảng tích lũy từ Part 2
# patterns = wave_engine.generate_waves(p2)
# 3. Gọi hàm vẽ
# plot_all_pattern_waves(patterns)
# =========================================================
# 1. DATA ENGINE (LOAD & PREPARE)
# =========================================================
def load_data(filename="data_ratio.pkl"):
    if not os.path.exists(filename):
        print(f"[X] Không tìm thấy file {filename}")
        return pd.DataFrame()
    df = pd.read_pickle(filename)
    df['sid'] = pd.to_numeric(df['sid'])
    return df.sort_values('sid').reset_index(drop=True)

# =========================================================
# 2. META MAPPING ENGINE (UPGRADED)
# =========================================================
class MetaMappingEngine:
    def __init__(self, model, name="Model"):
        self.model = model
        self.name = name
        self.pattern_waves = [] 
        self.live_history = []  
        self.mapping_log = []   
        self.last_sid = None

    def _z_normalize(self, data):
        """Chuẩn hóa để so khớp hình dáng (shape) thay vì biên độ"""
        std = np.std(data)
        if std == 0: return data - np.mean(data)
        return (data - np.mean(data)) / std

    def generate_patterns(self, df_part2):
        X = df_part2[['v_ratio', 'bc_ratio']]
        y = df_part2['target'].values
        preds = self.model.predict(X)
        sids = df_part2['sid'].values
        
        current_wave, cumulative = [], 0
        for i in range(len(df_part2)):
            if i > 0 and sids[i] != sids[i-1] + 1:
                if len(current_wave) > 35: self.pattern_waves.append(np.array(current_wave))
                current_wave, cumulative = [], 0
            
            point = 1 if preds[i] == y[i] else -1
            cumulative += point
            current_wave.append(cumulative)
        if len(current_wave) > 35: self.pattern_waves.append(np.array(current_wave))
        # print(f"[{self.name}] Nạp {len(self.pattern_waves)} pattern mẫu.")

    def find_best_trend(self, window_size=30, forecast_horizon=10):
        if len(self.live_history) < window_size: return 1
            
        current_win = self._z_normalize(np.array(self.live_history[-window_size:]))
        total_weight, weighted_trend = 0, 0
        
        for p in self.pattern_waves:
            if len(p) < (window_size + forecast_horizon): continue
            
            for start in range(len(p) - (window_size + forecast_horizon)):
                sub_p_raw = p[start : start + window_size]
                sub_p_norm = self._z_normalize(sub_p_raw)
                
                # So khớp hình dáng
                corr = np.corrcoef(current_win, sub_p_norm)[0, 1]
                
                if corr > 0.85:
                    # Tính độ dốc trung bình của 10 phiên tới thay vì chỉ lấy điểm cuối
                    future_seg = p[start + window_size : start + window_size + forecast_horizon]
                    avg_slope = (future_seg[-1] - future_seg[0]) / forecast_horizon
                    
                    weight = corr ** 4 # Tăng lũy thừa để lọc cực gắt
                    weighted_trend += avg_slope * weight
                    total_weight += weight
                    
        if total_weight == 0: return 1
        return 1 if weighted_trend >= 0 else -1

    def run_mapping_test(self, df_part3):
        results = []
        self.live_history, self.mapping_log, self.last_sid = [], [], None
        
        for _, row in df_part3.iterrows():
            if self.last_sid is not None and row['sid'] != self.last_sid + 1:
                if self.live_history: self.mapping_log.append(np.array(self.live_history))
                self.live_history = []

            X_row = row[['v_ratio', 'bc_ratio']].values.reshape(1, -1)
            raw_pred = self.model.predict(X_row)[0]
            
            trend = self.find_best_trend()
            final_pred = raw_pred if trend == 1 else (1 - raw_pred)
            
            correct_raw = 1 if raw_pred == row['target'] else 0
            correct_map = 1 if final_pred == row['target'] else 0
            
            # Lưu để tính phiên sau
            self.live_history.append((self.live_history[-1] if self.live_history else 0) + (1 if correct_raw else -1))
            self.last_sid = row['sid']
            
            results.append({'target': row['target'], 'raw_correct': correct_raw, 'map_correct': correct_map})
            
        if self.live_history: self.mapping_log.append(np.array(self.live_history))
        return pd.DataFrame(results)

# =========================================================
# 3. TRỰC QUAN HÓA & SO SÁNH ĐA MÔ HÌNH
# =========================================================
def analyze_multi_models(df):
    n = len(df)
    p1, p2, p3 = df.iloc[:int(n*0.7)], df.iloc[int(n*0.7):int(n*0.9)], df.iloc[int(n*0.9):]
    print(f"Phân chia dữ liệu: Part 1 = {len(p1)} | Part 2 = {len(p2)} | Part 3 = {len(p3)}")
    # stop()


    # Danh sách các "đấu sĩ"
    engines = [
        MetaMappingEngine(XGBClassifier(n_estimators=100, max_depth=3), "XGBoost"),
        MetaMappingEngine(RandomForestClassifier(n_estimators=100, max_depth=5), "RandomForest"),
        MetaMappingEngine(GradientBoostingClassifier(), "GradBoost")
    ]

    plt.figure(figsize=(15, 8))
    print(f"{'MODEL':<15} | {'RAW ACC':<10} | {'MAPPED ACC':<10} | {'IMPROVE'}")
    print("-" * 55)

    for engine in engines:
        # Train & Generate Patterns
        engine.model.fit(p1[['v_ratio', 'bc_ratio']], p1['target'])
        engine.generate_patterns(p2)
        # plot_all_pattern_waves(engine.pattern_waves)
        
        # Test
        res = engine.run_mapping_test(p3)
        raw_acc, map_acc = res['raw_correct'].mean(), res['map_correct'].mean()
        improvement = map_acc - raw_acc
        
        print(f"{engine.name:<15} | {raw_acc:.4f}     | {map_acc:.4f}       | {improvement:+.4f}")
        
        # Vẽ Cumulative Profit
        map_cum = (res['map_correct'] * 2 - 1).cumsum()
        plt.plot(map_cum.values, label=f'Mapped {engine.name} (Acc: {map_acc:.2%})')

    plt.axhline(0, color='black', lw=1, ls='--')
    plt.title("So sánh đường cong lợi nhuận của các Model sau khi Mapping", fontsize=14)
    plt.xlabel("Số phiên (Part 3)")
    plt.ylabel("Điểm tích lũy")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    data = load_data().tail(5000)
    print(f"Tổng số phiên đã tải: {len(data)}")
    if not data.empty:
        analyze_multi_models(data)