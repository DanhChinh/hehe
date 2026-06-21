import json
import numpy as np
import pandas as pd
from collections import Counter
from handle_db import load_data_from_pickle as make_data


from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

def print_model_info(model, X, y, title=None):
    """
    In thông tin đánh giá model.

    Parameters
    ----------
    model : sklearn model đã fit
    X     : dữ liệu đầu vào
    y     : nhãn thực tế
    title : tên model (optional)
    """

    y_pred = model.predict(X)

    print("=" * 60)

    if title:
        print(f"MODEL: {title}")
    else:
        print(f"MODEL: {model.__class__.__name__}")

    print("=" * 60)

    print(f"Accuracy : {accuracy_score(y, y_pred):.4f}")
    print(f"Precision: {precision_score(y, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"Recall   : {recall_score(y, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"F1 Score : {f1_score(y, y_pred, average='weighted', zero_division=0):.4f}")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y, y_pred))

    print("\nClassification Report:")
    print(classification_report(y, y_pred, zero_division=0))

    print("=" * 60)
####

def calc_total_money(start_money, rounds, repeat_each_round):
    return repeat_each_round * start_money * (2**rounds - 1)

def calc_start_money(total_money, rounds=5, repeat_each_round=5):
    return round(total_money / (repeat_each_round * (2**rounds - 1)), 2)

# Biến toàn cục lưu trữ trạng thái của các mô hình (Global Session Cache)
_GLOBAL_MODELS = None  


# class MoneyManager:
#     """
#     Bộ quản lý vốn và kích thước vị thế (Anti-Martingale / Streak-based Scaling).
#     Tự động tăng quy mô vị thế khi đạt chuỗi thắng và giảm quy mô vị thế khi gặp chuỗi thua.
#     """
#     def __init__(self, streak_threshold=5):
#         self.position_size = 1    # Khối lượng vào lệnh hiện tại (bet)
#         self.streak_counter = 0                    # Bộ đếm chuỗi hiệu suất (counter_profit)
#         self.accumulated_profit = 155              # Tổng lợi nhuận tích lũy (total_profit)
#         self.streak_threshold = streak_threshold    # Ngưỡng dịch chuyển khối lượng (take_profit)

#     def update_performance(self, is_win):
#         """Cập nhật trạng thái tài sản và tính toán lại quy mô vị thế cho phiên sau"""
#         if is_win:
#             self.accumulated_profit += self.position_size
#             self.streak_counter += 1
#             if self.streak_counter == self.streak_threshold:
#                 self.position_size = calc_start_money(self.accumulated_profit)
        
#                 self.streak_counter = 0
#         else:
#             self.accumulated_profit -= self.position_size
#             self.streak_counter -= 1
#             if self.streak_counter == -self.streak_threshold:
#                 self.position_size *= 2        
#                 self.streak_counter = 0
class MoneyManager:
    """
    Bộ quản lý vốn theo chiến thuật D'Alembert cải tiến dựa trên Chuỗi (Streak-based).
    Tự động GIẢM quy mô vị thế khi đạt chuỗi THẮNG và TĂNG quy mô vị thế khi gặp chuỗi THUA.
    """
    def __init__(self, streak_threshold=5, base_size=1.0):
        self.base_size = float(base_size)          # Khối lượng cơ sở tối thiểu (đơn vị tăng/giảm)
        self.position_size = float(base_size)      # Khối lượng vào lệnh hiện tại (bet)
        self.streak_counter = 0                    # Bộ đếm chuỗi hiệu suất (counter_profit)
        self.accumulated_profit = 0.0            # Tổng lợi nhuận tích lũy (total_profit)
        self.streak_threshold = streak_threshold    # Ngưỡng dịch chuyển khối lượng (take_profit)

    def update_performance(self, is_win):
        """Cập nhật trạng thái tài sản và tính toán lại quy mô vị thế theo D'Alembert dựa trên Streak"""
        
        # Làm tròn lợi nhuận về 2 chữ số thập phân để tránh lỗi sai số floating-point
        if is_win:
            self.accumulated_profit = round(self.accumulated_profit + self.position_size, 2)
            self.streak_counter += 1
            
            # Nếu chạm ngưỡng chuỗi THẮNG liên tiếp -> GIẢM mức cược theo D'Alembert
            if self.streak_counter == self.streak_threshold:
                # Giảm đi 1 lượng bằng base_size, nhưng không được thấp hơn base_size
                self.position_size = max(self.base_size, round(self.position_size - self.base_size, 2))
                self.streak_counter = 0  # Reset chuỗi
        else:
            self.accumulated_profit = round(self.accumulated_profit - self.position_size, 2)
            self.streak_counter -= 1
            
            # Nếu chạm ngưỡng chuỗi THUA liên tiếp -> TĂNG mức cược theo D'Alembert để gỡ
            if self.streak_counter == -self.streak_threshold:
                # Tăng tuyến tính thêm 1 lượng bằng base_size
                self.position_size = round(self.position_size + self.base_size, 2)
                self.streak_counter = 0  # Reset chuỗi


class TradingModel:
    def __init__(self, model_name, base_model, ncc_threshold=0.5, vote_window=3):
        print(model_name)
        self.model_name = model_name
        self.base_model = base_model
        
        # Cấu hình kiểm soát nhiễu NCC
        self.ncc_threshold = ncc_threshold
        self.vote_window = vote_window
        self.raw_trend_history = []
        
        # Trạng thái dự đoán và quản lý lệnh phiên hiện tại
        self.raw_prediction = None
        self.fixed_prediction = None
        self.expected_bet = 0.0           # Khối lượng vào lệnh kỳ vọng cho phiên hiện tại
        self.position_enabled = True       # Trạng thái kích hoạt bộ lọc thủ công
        
        # Khởi tạo bộ quản lý vốn độc lập cho từng mô hình
        self.money_manager = MoneyManager()
        
        # Đường cong hiệu suất thô (15 phiên gần nhất) làm mẫu trượt NCC
        self.raw_history = [0]
        self.short_equity_curve = np.cumsum(self.raw_history)
        
        # Đường cong vốn thực tế dựa trên số tiền tài sản (Lưu lịch sử từ MoneyManager)
        self.fixed_equity_curve = []
        
        # Các phân đoạn hiệu suất liên tục ở quá khứ (Part 2)
        self.long_segments = []

    def initialize_pipeline(self, data_train, label_train, data_long, label_long, sid_long):
        """Pha 1: Huấn luyện mô hình và chuẩn bị các phân đoạn mẫu quá khứ"""
        self.base_model.fit(data_train, label_train)
        
        pred_long = self.base_model.predict(data_long)
        match_long = np.where(pred_long == label_long, 1, -1)

        # print_model_info(self.base_model, data_long, label_long, title=self.model_name)
        
        self.long_segments = []
        if len(sid_long) > 0:
            current_seg = [match_long[0]]
            for i in range(1, len(sid_long)):
                if sid_long[i] == sid_long[i-1] + 1:
                    current_seg.append(match_long[i])
                else:
                    if len(current_seg) >= 15:
                        self.long_segments.append(np.cumsum(current_seg))
                    current_seg = [match_long[i]]
            if len(current_seg) >= 15:
                self.long_segments.append(np.cumsum(current_seg))

    def make_predict(self, x_new):
        if x_new is None:# or self.money_manager.accumulated_profit <= 0:
            self.fixed_prediction = None
            self.expected_bet = 0.0
            self.raw_prediction = None

            return None
        """Pha 2: Dự đoán, nắn xu hướng và đưa ra mức kỳ vọng phân bổ vốn (Expected Bet)"""
        market_trend = self._detect_market_trend_ncc()
        
        pred_raw = int(self.base_model.predict([x_new])[0])
        self.raw_prediction = 1 if pred_raw == 1 else 2
        
        self.raw_trend_history.append(market_trend)
        self.raw_trend_history = self.raw_trend_history[-self.vote_window:]
        filtered_trend = Counter(self.raw_trend_history).most_common(1)[0][0]
        
        # Tiến hành nắn kết quả dự đoán
        if filtered_trend == "down":
            self.fixed_prediction = 2 if self.raw_prediction == 1 else 1
        elif filtered_trend in ["---", "error"]:
            self.fixed_prediction = None  
        else:
            self.fixed_prediction = self.raw_prediction
            
        # Bộ chặn thủ công (nếu vị thế bị tắt)
        if not self.position_enabled:
            self.fixed_prediction = None

        # TÍNH TOÁN MỨC KỲ VỌNG VÀO LỆNH CHO PHIÊN NÀY
        if self.fixed_prediction is None:
            self.expected_bet = 0.0  # Đứng ngoài thị trường, mức kỳ vọng giao dịch bằng 0
        else:
            self.expected_bet = float(self.money_manager.position_size)

        return self.fixed_prediction

    def check(self, actual_label):
        """Pha 3: Kiểm tra kết quả thực tế khi đóng phiên, cập nhật bộ quản lý vốn và lưu lịch sử tài sản"""
        # 1. Tịnh tiến đường cong hiệu suất gốc phục vụ tính toán NCC phiên sau
        if self.raw_prediction is not None:
            score_raw = 1 if self.raw_prediction == actual_label else -1
            self.raw_history.append(score_raw)
            self.raw_history = self.raw_history[-15:]  
            self.short_equity_curve = np.cumsum(self.raw_history)
            
        # 2. Đồng bộ kết quả thực tế với bộ quản lý vốn cá nhân
        if self.fixed_prediction is not None:
            is_win = (self.fixed_prediction == actual_label)
            self.money_manager.update_performance(is_win)
            
        # 3. Ghi nhận giá trị tài sản thực tế vào đường cong vốn dài hạn
        self.fixed_equity_curve.append(float(self.money_manager.accumulated_profit))

    def set_toggle_position(self):
        """Đảo trạng thái cho phép/chặn mô hình vào lệnh thủ công"""
        self.position_enabled = not self.position_enabled
        print(f"🔄 [{self.model_name}] Position Toggle: {self.position_enabled}")

    def get_info(self):
        """Trả về dữ liệu tổng hợp trạng thái phiên (Đảm bảo 100% JSON Serializable)"""
        return {
            "model_name": str(self.model_name),
            "predict": int(self.fixed_prediction) if self.fixed_prediction is not None else None,
            "expected_bet": float(self.expected_bet),
            "current_position_size": float(self.money_manager.position_size),
            "accumulated_profit": int(self.money_manager.accumulated_profit),
            "streak_counter": int(self.money_manager.streak_counter),
            "fixed_equity_curve": [float(x) for x in self.fixed_equity_curve]
        }

    def _detect_market_trend_ncc(self):
        S = np.array(self.short_equity_curve, dtype=float)
        N = len(S)
        S_mean, S_std = np.mean(S), np.std(S)
        
        best_ncc_score = -2.0
        best_segment = None
        best_match_idx = -1
        
        for segment in self.long_segments:
            if len(segment) < N:
                continue
            for i in range(len(segment) - N + 1):
                window = segment[i : i + N]
                W_mean, W_std = np.mean(window), np.std(window)
                
                if S_std == 0 or W_std == 0:
                    ncc = 0.0
                else:
                    ncc = np.sum((window - W_mean) * (S - S_mean)) / (N * W_std * S_std)
                
                if ncc > best_ncc_score:
                    best_ncc_score = ncc
                    best_match_idx = i
                    best_segment = segment

        if best_ncc_score < self.ncc_threshold or best_segment is None:
            return "---"
            
        K = 5
        future_start = best_match_idx + N
        future_end = min(len(best_segment), future_start + K)
        future_window = best_segment[future_start : future_end]
        
        if len(future_window) < 2:
            return "---"
            
        slope = future_window[-1] - future_window[0]
        return "up" if slope > 0.0001 else "down" if slope < -0.0001 else "---"


# =========================================================================
# HỆ THỐNG ĐIỀU PHỐI ĐƠN LUỒNG MỖI PHIÊN (SESSION OPERATIONS)
# =========================================================================

def _get_or_load_models():
    """Quản lý vòng đời bộ nhớ Singleton: Tự động tải pha nền khi hệ thống bắt đầu kích hoạt"""
    global _GLOBAL_MODELS
    if _GLOBAL_MODELS is None:
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.neural_network import MLPClassifier
        from sklearn.ensemble import (
            RandomForestClassifier,
            ExtraTreesClassifier
        )
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier

        models_config = {

            # 1
            "LDA": LinearDiscriminantAnalysis(),

            # 
        
            # 4
            "KNN": KNeighborsClassifier(
                n_neighbors=15,
                weights="distance"
            ),

            # 5
            "DecisionTree": DecisionTreeClassifier(
                max_depth=5,
                min_samples_leaf=20,
                random_state=42
            ),

            # 6
            "RandomForest": RandomForestClassifier(
                n_estimators=200,
                max_depth=5,
                min_samples_leaf=20,
                max_features="sqrt",
                random_state=42,
                n_jobs=-1
            ),

            # 7
            "ExtraTrees": ExtraTreesClassifier(
                n_estimators=200,
                max_depth=5,
                min_samples_leaf=20,
                random_state=42,
                n_jobs=-1
            ),
            # 11 (nếu muốn thay thế model khác)
            "MLP": MLPClassifier(
                hidden_layer_sizes=(32, 16),
                alpha=0.01,          # regularization
                max_iter=500,
                early_stopping=True,
                validation_fraction=0.1,
                random_state=42
            )
        }
        # Nạp dữ liệu gốc từ hàm make_data() của bạn
        df, dataall, labelall = make_data()
        lendic = len(models_config)

        dataall = np.array_split(dataall, lendic) 
        labelall = np.array_split(labelall, lendic) 
        
        sid = df['sid'].values
        sidall = np.array_split(sid, lendic)

        _GLOBAL_MODELS = []

        for i, (name, algorithm) in enumerate(models_config.items()):
            data = dataall[i]
            label = labelall[i]
            sid = sidall[i]
            
            train_ratio = 0.7
            split_idx = int(len(label) * train_ratio)

            data_train, label_train = data[:split_idx], label[:split_idx]
            data_long, label_long, sid_long = data[split_idx:], label[split_idx:], sid[split_idx:]

            model = TradingModel(model_name=name, base_model=algorithm)
            model.initialize_pipeline(data_train, label_train, data_long, label_long, sid_long)
            _GLOBAL_MODELS.append(model)
            
    return _GLOBAL_MODELS


def PREDICT(x_pred):
    """
    Gọi ở ĐẦU PHIÊN:
    Tính toán và nắn dòng dự đoán, đồng thời xác lập mức kỳ vọng khối lượng vào lệnh hiện tại.
    """
    models = _get_or_load_models()
    for model in models:
        model.make_predict(x_pred)


def CHECK(result):
    """
    Gọi ở CUỐI PHIÊN:
    Nạp kết quả thực tế (nhãn đúng của phiên) để tính toán lãi lỗ và cập nhật lại bộ quản lý vốn.
    """
    models = _get_or_load_models()
    for model in models:
        model.check(result)


def SET_POSITION(index):
    """Bật/Tắt vị thế hoạt động của một mô hình cụ thể qua chỉ mục index"""
    models = _get_or_load_models()
    if 0 <= index < len(models):
        models[index].set_toggle_position()
    else:
        print(f"⚠️ Index {index} nằm ngoài phạm vi danh sách mô hình.")


def GET_ALL_INFO():
    """Lấy dữ liệu tổng hợp của phiên hiện tại kết hợp rà soát lỗi đồng bộ JSON"""
    models = _get_or_load_models()
    data = []
    for model in models:
        data.append(model.get_info())
        
    for dt in data:
        try:
            json.dumps(dt)
        except TypeError as e:
            print("❌ JSON ERROR:", e)
            for k, v in dt.items():
                try:
                    json.dumps(v)
                except TypeError:
                    print(f"👉 Lỗi ở field: {k}, type = {type(v)}")
    obj_mean = {
            "model_name": "Mean",
            "predict": None,
            "expected_bet": None,
            "current_position_size": None,
            "accumulated_profit": 0,
            "streak_counter": None,
            "fixed_equity_curve": []
    }
    for key in ["accumulated_profit", "fixed_equity_curve"]:
        # Chuyển tất cả giá trị của key này thành một mảng numpy để tính toán
        values = np.array([obj[key] for obj in data])
        
        # axis=0 giúp tính trung bình theo chiều dọc (cho cả số và mảng)
        avg_value = np.mean(values, axis=0)
        
        # Chuyển ngược từ numpy array về list/float thuần của Python nếu cần
        obj_mean[key] = avg_value.tolist() if isinstance(data[0][key], list) else round(float(avg_value), 2)
    data.insert(0, obj_mean)
    return data

print("⏳ Đang khởi động ứng dụng và huấn luyện hệ thống mô hình nền...")

# Chủ động gọi hàm này để ép hệ thống chạy pha initialize_pipeline trước
_get_or_load_models() 

print("✅ Hệ thống đã sẵn sàng nhận dữ liệu realtime!")

# Từ lúc này, mỗi khi gọi PREDICT(x_pred) ở các phiên tiếp theo, 
# tốc độ phản hồi sẽ gần như ngay lập tức (< 0.01 giây) vì mô hình đã nằm sẵn trên RAM.




