import numpy as np
import random as rd
from handle_data import make_data, handle_progress, handle_last_30

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from zigzag_engine import ZigZagTradingBot

def danh_gia_huong(data):
    # 1. Lọc dữ liệu hợp lệ
    clean = [(x, y) for x, y in data if x != "-" and y != "-"]

    # Nếu ít hơn 2 điểm => không đánh giá được
    if len(clean) < 2:
        return "error"

    # 2. Tính slope (độ dốc)
    slopes = []
    for (x1, y1), (x2, y2) in zip(clean[:-1], clean[1:]):
        if x2 != x1:
            slopes.append((y2 - y1) / (x2 - x1))

    if not slopes:
        return "---"

    avg_slope = sum(slopes) / len(slopes)

    # 3. Đánh giá xu hướng
    threshold = 0.0001  # ngưỡng gần 0 để coi như đi ngang

    if avg_slope > threshold:
        return "up"
    elif avg_slope < -threshold:
        return "down"
    else:
        return "---"
def check_pattern(arr, down_threshold=0.6, flat_threshold=0.05):
    arr = np.array(arr, dtype=float)
    n = len(arr)
    
    if n < 5:
        return False
    
    split_idx = int(n * 0.8)
    
    first_part = arr[:split_idx]
    last_part = arr[split_idx:]
    
    # kiểm tra dốc xuống
    diffs = np.diff(first_part)
    down_ratio = np.sum(diffs < 0) / len(diffs)
    is_downtrend = down_ratio >= down_threshold
    
    # kiểm tra đi ngang
    mean_last = np.mean(last_part)
    std_last = np.std(last_part)
    is_flat = (std_last / mean_last) <= flat_threshold if mean_last != 0 else False
    
    return is_downtrend and is_flat

class MYMODEL:
    def __init__(self, name, model, data_train, label_train, data_long, label_long, data_formakehs, label_formakehs):
        self.name = name
        self.model = model
        self.predict = None
        self.predict_fix = None
        self.best_match = None
        self.history = [0]
        self.history_fix = [0]
        self.history_fix_cumsum = np.array([])
        self.short_array = np.cumsum(self.history)
        

        self.model.fit(data_train, label_train)
        pred_p2 = self.model.predict(data_long)
        compare = np.where(pred_p2 == label_long, 1, -1)
        self.LONG_ARRAY = np.cumsum(compare)

        for i in range(len(data_formakehs)):
            x = data_formakehs[i]
            y_true = label_formakehs[i]
            self.find_best_match_ncc()
            self.make_predict(x)
            self.check(y_true)
            # self.check_fix(y_true)

    def make_predict(self, x_pred):
        self.predict = 1 if int(self.model.predict([x_pred])[0]) ==1 else 2
        self.predict_fix = self.predict
        if self.best_match["trend"] == "down":
            self.predict_fix = 1 if self.predict == 2 else 2
        if self.best_match["trend"] == "---" or self.best_match["trend"] == "error":
            self.predict_fix = None
        print(self.name, self.best_match["trend"], self.predict, self.predict_fix)

    def check(self, result):
        if self.predict == None:
            return
        if self.predict == result:
            self.history.append(1)
        else:
            self.history.append(-1)
        self.history = self.history[-15:]
        self.short_array = np.cumsum(self.history)
    def check_fix(self, result):
        if self.predict_fix == None:
            self.history_fix.append(0)
        elif self.predict_fix == result:
            self.history_fix.append(1)
        else:
            self.history_fix.append(-1)
        self.history_fix_cumsum = np.cumsum(self.history_fix)
        signal = self.bot.update(self.history_fix_cumsum[-1] +100 ) # BUY, SELL, None
        if signal == "BUY":
            self.signal = signal
        elif signal == "SELL":
            self.signal = None
        else:
            pass

    def find_best_match_ncc(self):
        S = np.array(self.short_array, dtype=float)
        L = np.array(self.LONG_ARRAY, dtype=float)
        N = len(S)
        
        S_mean = np.mean(S); S_std = np.std(S)
        ncc_scores = []
        
        for i in range(len(L) - N + 1):
            window = L[i:i + N]
            L_mean = np.mean(window); L_std = np.std(window)
            if S_std == 0 or L_std == 0: ncc = 0.0
            else:
                numerator = np.sum((window - L_mean) * (S - S_mean))
                denominator = (N * L_std * S_std)
                ncc = numerator / denominator
            ncc_scores.append(ncc)
            
        ncc_scores = np.array(ncc_scores)
        best_match_index = np.argmax(ncc_scores)
        max_ncc_score = ncc_scores[best_match_index]
        
        # ----------------------------------------------------
        # SỬA ĐỔI CHÍNH: Xây dựng CỬA SỔ HIỂN THỊ CỤC BỘ
        # ----------------------------------------------------
        
        K = 5  # Số lượng phần tử tương lai muốn hiển thị
        P = 1   # Số lượng phần tử quá khứ muốn hiển thị (ngữ cảnh)
        
        start_index_int = int(best_match_index)
        
        # Xác định phạm vi hiển thị (từ P điểm trước đến K điểm sau đoạn khớp)
        local_start_index = max(0, start_index_int - P)
        local_end_index = min(len(L), start_index_int + N + K)
        
        # Cắt đoạn dữ liệu cục bộ
        local_data = L[local_start_index : local_end_index].tolist()
        
        # Xây dựng dữ liệu cho các series vẽ
        
        # 1. Đoạn khớp (Match Segment)
        match_data_local = []
        for i in range(len(local_data)):
            global_index = local_start_index + i
            if global_index >= start_index_int and global_index < start_index_int + N:
                match_data_local.append([global_index, local_data[i]])
            else:
                match_data_local.append(['-', '-']) # Dùng '-' để ECharts vẽ đường rời rạc
        
        # 2. Dữ liệu Tương lai (Prediction Segment)
        predicted_data_local = []
        for i in range(len(local_data)):
            global_index = local_start_index + i
            if global_index >= start_index_int + N and global_index < start_index_int + N + K:
                predicted_data_local.append([global_index, local_data[i]])
            else:
                predicted_data_local.append(['-', '-'])

        # Chuẩn bị dữ liệu cho biểu đồ 2 (Hình dạng)
        best_match_window = L[start_index_int : start_index_int + N]
        S_centered = S - np.mean(S)
        W_centered = best_match_window - np.mean(best_match_window)

        self.best_match =  {
            # Dữ liệu chính
            "best_index": start_index_int,       
            "max_score": float(max_ncc_score),    
            "n_points": int(N),
            "history_fix_cumsum":self.history_fix_cumsum.tolist(),
            
            # Dữ liệu cục bộ cho Biểu đồ 1
            "local_data": local_data,
            "local_start_index": local_start_index,
            "match_data_local": match_data_local,
            "predicted_data_local": predicted_data_local,
            "trend": danh_gia_huong(predicted_data_local),
            
            # Dữ liệu cho Biểu đồ 2
            "S_centered": S_centered.tolist(),
            "W_centered": W_centered.tolist()
        }

    def get_info(self):
        return {
            "name": self.name,
            "predict_fix": self.predict_fix,
            "best_match": self.best_match,
            "signal": self.signal
        }




def FIND_BEST_MATCHS(): 
    for model in models:
        model.find_best_match_ncc()
def PREDICT(x_pred):
    for model in models:
        model.make_predict(x_pred)
def CHECK(result):
    for model in models:
        model.check(result)
        model.check_fix(result)


def GET_ALL_INFO():
    data = []
    for model in models:
        data.append(model.get_info())
    return data


from sklearn.model_selection import StratifiedKFold
def split_10_stratified(X, y):
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

    splits = []
    for train_idx, test_idx in skf.split(X, y):
        X_part = X[test_idx]
        y_part = y[test_idx]
        splits.append((X_part, y_part))

    return splits

# def make_data(n=200, seed=42):
#     np.random.seed(seed)

#     # --- tạo chuỗi giá ---
#     t = np.arange(n)

#     trend = 0.05 * t
#     seasonal = 2 * np.sin(0.2 * t)
#     noise = np.random.normal(0, 0.5, n)

#     prices = 10 + trend + seasonal + noise

#     # --- tạo label ---
#     # 1 = tăng, 0 = giảm
#     y = (prices[1:] > prices[:-1]).astype(int)

#     # --- tạo feature ---
#     # dùng giá hiện tại và quá khứ gần nhất
#     X = np.column_stack([
#         prices[:-1],  # t-1
#         prices[1:]    # t
#     ])

#     return X, y
def LOAD():
    data, label = make_data()

    data_formakehs = data[-15:]
    label_formakehs = label[-15:]

    data_long = data[-1000:-15]
    label_long = label[-1000:-15]

    data = data[:-1000]
    label = label[:-1000]

    splits = split_10_stratified(data, label)



    # ===============================
    # 2. TRAIN RANDOM FOREST
    # ===============================

    models = []
    LONGS = []

    for i in range(10):
        (dt, lb) = splits[i]

        models.append(
            MYMODEL(
                f"LDA_{i+1}", 
                LinearDiscriminantAnalysis(),
                dt, lb,
                data_long, label_long,
                data_formakehs, label_formakehs
                )
        )


    for model in models:
        LONGS.append(model.LONG_ARRAY)
    return models, LONGS

models, LONGS = LOAD()