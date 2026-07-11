import json
import numpy as np
import pandas as pd
import pickle
import os
from collections import Counter
from handle_db import load_data_from_pickle as make_data

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

# Biến toàn cục lưu trữ trạng thái của các mô hình (Global Session Cache)
_GLOBAL_MODELS = None  


class MoneyManager:
    """
    Bộ quản lý vốn theo chiến thuật D'Alembert cải tiến dựa trên Chuỗi (Streak-based).
    Tự động GIẢM quy mô vị thế khi đạt chuỗi THẮNG và TĂNG quy mô vị thế khi gặp chuỗi THUA.
    """
    def __init__(self, streak_threshold=8, base_size=1.0):
        self.base_size = float(base_size)          # Khối lượng cơ sở tối thiểu (đơn vị tăng/giảm)
        self.position_size = float(base_size)      # Khối lượng vào lệnh hiện tại (bet)
        self.streak_counter = 0                    # Bộ đếm chuỗi hiệu suất (counter_profit)
        self.accumulated_profit = 0.0              # Tổng lợi nhuận tích lũy (total_profit)
        self.streak_threshold = streak_threshold    # Ngưỡng dịch chuyển khối lượng (take_profit)

    def update_performance(self, is_win):
        """Cập nhật trạng thái tài sản và tính toán lại quy mô vị thế theo D'Alembert dựa trên Streak"""
        if is_win:
            self.accumulated_profit = round(self.accumulated_profit + self.position_size, 2)
            self.streak_counter += 1
            
            # Nếu chạm ngưỡng chuỗi THẮNG liên tiếp -> GIẢM mức cược theo D'Alembert
            if self.streak_counter == self.streak_threshold:
                self.position_size = max(self.base_size, round(self.position_size - self.base_size, 2))
                self.streak_counter = 0  # Reset chuỗi
        else:
            self.accumulated_profit = round(self.accumulated_profit - self.position_size, 2)
            self.streak_counter -= 1
            
            # Nếu chạm ngưỡng chuỗi THUA liên tiếp -> TĂNG mức cược theo D'Alembert để gỡ
            if self.streak_counter == -self.streak_threshold:
                self.position_size = round(self.position_size + self.base_size, 2)
                self.streak_counter = 0  # Reset chuỗi


class TradingModel:
    def __init__(self, model_name, base_model=None, ncc_threshold=0.5, vote_window=3):
        self.model_name = model_name
        self.base_model = base_model
        
        # Cấu hình kiểm soát nhiễu NCC
        self.ncc_threshold = ncc_threshold
        self.vote_window = vote_window
        
        # Lịch sử dự đoán (Trạng thái tạm thời theo phiên)
        self.raw_trend_history = []
        self.raw_prediction = None
        self.fixed_prediction = None
        self.expected_bet = 0.0           

        # Thống kê chi tiết số lần đúng / sai của mô hình thực tế (Phục vụ đánh giá)
        self.total_trades = 0             
        self.total_wins = 0               
        self.total_losses = 0             
        
        # Khởi tạo bộ quản lý vốn độc lập cho từng mô hình
        self.money_manager = MoneyManager()
        
        # Đường cong hiệu suất thô ngắn hạn làm mẫu trượt NCC
        self.raw_history = [0]
        self.short_equity_curve = np.cumsum(self.raw_history)
        
        # Đường cong vốn thực tế dựa trên số tiền tài sản
        self.fixed_equity_curve = [0.0] # Khởi tạo điểm bắt đầu bằng 0
        
        # Các phân đoạn hiệu suất liên tục ở quá khứ (Phục vụ dự đoán)
        self.long_segments = []

    def initialize_pipeline(self, data_train, label_train, data_long, label_long, sid_long):
        """Pha 1: Huấn luyện mô hình và chuẩn bị các phân đoạn mẫu quá khứ"""
        if self.base_model is None:
            raise ValueError(f"Không thể train vì base_model của {self.model_name} chưa được gán!")
            
        self.base_model.fit(data_train, label_train)
        
        pred_long = self.base_model.predict(data_long)
        match_long = np.where(pred_long == label_long, 1, -1)
        
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
                
        # Khởi động lại đồ thị vốn khớp với trạng thái ban đầu sau khi train mới
        self.fixed_equity_curve = [float(self.money_manager.accumulated_profit)]

    def make_predict(self, x_new):
        if x_new is None or self.base_model is None:
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

        # Tính toán mức kỳ vọng vào lệnh cho phiên này
        if self.fixed_prediction is None:
            self.expected_bet = 0.0  
        else:
            self.expected_bet = float(self.money_manager.position_size)

        return self.fixed_prediction

    def check(self, actual_label):
        """Pha 3: Kiểm tra kết quả thực tế khi đóng phiên, cập nhật bộ quản lý vốn và bộ đếm đúng/sai"""
        if self.raw_prediction is not None:
            score_raw = 1 if self.raw_prediction == actual_label else -1
            self.raw_history.append(score_raw)
            self.raw_history = self.raw_history[-15:]  
            self.short_equity_curve = np.cumsum(self.raw_history)
            
        if self.fixed_prediction is not None:
            is_win = (self.fixed_prediction == actual_label)
            
            # Cập nhật bộ đếm thống kê chi tiết
            self.total_trades += 1
            if is_win:
                self.total_wins += 1
            else:
                self.total_losses += 1
                
            self.money_manager.update_performance(is_win) 
            
        # FIXED: Đi ngang hoặc biến động đều được lưu trọn vẹn theo từng phiên toàn cục
        self.fixed_equity_curve.append(float(self.money_manager.accumulated_profit))

    def set_toggle_position(self):
        pass

    def get_info(self, origin_idx=None):
        """Trả về dữ liệu tổng hợp trạng thái phiên kèm chỉ mục gốc trên RAM"""
        win_rate = (self.total_wins / self.total_trades * 100) if self.total_trades > 0 else 0.0
        return {
            "model_name": str(self.model_name),
            "predict": int(self.fixed_prediction) if self.fixed_prediction is not None else None,
            "expected_bet": float(self.expected_bet),
            "current_position_size": float(self.money_manager.position_size),
            "accumulated_profit": float(self.money_manager.accumulated_profit),
            "streak_counter": int(self.money_manager.streak_counter),
            "total_trades": int(self.total_trades),
            "total_wins": int(self.total_wins),
            "total_losses": int(self.total_losses),
            "win_rate_percent": round(win_rate, 2),
            "fixed_equity_curve": [float(x) for x in self.fixed_equity_curve],
            "is_main": False,
            "original_index": origin_idx  
        }

    # =========================================================================
    # ĐỒNG BỘ ĐỌC/LƯU: ĐÃ SỬA ĐỂ LƯU THÊM MẢNG ĐỒ THỊ
    # =========================================================================
    def save_model_package(self, folder_path="saved_models"):
        """Lưu đồng thời file trạng thái JSON và file thuật toán học máy PKL"""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        clean_name = self.model_name.replace(' ', '_').lower()
        json_path = os.path.join(folder_path, f"{clean_name}_state.json")
        pkl_path = os.path.join(folder_path, f"{clean_name}_base.pkl")
        
        win_rate = (self.total_wins / self.total_trades * 100) if self.total_trades > 0 else 0.0
        
        # Đóng gói dữ liệu (FIXED: Đã bổ sung fixed_equity_curve vào stats)
        state_data = {
            "model_name": self.model_name,
            "stats": {
                "total_trades": self.total_trades,
                "total_wins": self.total_wins,
                "total_losses": self.total_losses,
                "win_rate_percent": round(win_rate, 2),
                "accumulated_profit": float(self.money_manager.accumulated_profit),
                "fixed_equity_curve": [float(x) for x in self.fixed_equity_curve]
            },
            "history": {
                "long_segments": [seg.tolist() for seg in self.long_segments] 
            }
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=4)
            
        if self.base_model is not None:
            with open(pkl_path, 'wb') as f:
                pickle.dump(self.base_model, f)
        print(f"💾 Saved core package for [{self.model_name}]")

    def load_model_package(self, folder_path="saved_models"):
        """Khôi phục các tham số đã lưu từ tệp tin"""
        clean_name = self.model_name.replace(' ', '_').lower()
        json_path = os.path.join(folder_path, f"{clean_name}_state.json")
        pkl_path = os.path.join(folder_path, f"{clean_name}_base.pkl")
        
        if not os.path.exists(json_path):
            return False
            
        with open(json_path, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
            
        # 1. Cài đặt các giá trị cốt lõi được khôi phục từ tệp tin
        self.model_name = state_data["model_name"]
        self.total_trades = state_data["stats"]["total_trades"]
        self.total_wins = state_data["stats"]["total_wins"]
        self.total_losses = state_data["stats"]["total_losses"]
        self.long_segments = [np.array(seg) for seg in state_data["history"]["long_segments"]]
        self.money_manager.accumulated_profit = state_data["stats"]["accumulated_profit"]
        
        # FIXED: Khôi phục trọn vẹn biểu đồ lịch sử đi ngang từ file JSON nếu tồn tại
        # if "fixed_equity_curve" in state_data["stats"]:
        #     self.fixed_equity_curve = [float(x) for x in state_data["stats"]["fixed_equity_curve"]]
        # else:
        #     self.fixed_equity_curve = [float(self.money_manager.accumulated_profit)]
        self.fixed_equity_curve = [0.0]
        
        # 2. Thiết lập MẶC ĐỊNH hoàn toàn và đồng bộ hóa cấu trúc mảng
        self.ncc_threshold = 0.5
        self.vote_window = 3
        self.raw_trend_history = []
        self.raw_prediction = None
        self.fixed_prediction = None
        self.expected_bet = 0.0
        
        self.raw_history = [0]
        self.short_equity_curve = np.cumsum(self.raw_history)
        
        self.money_manager.position_size = float(self.money_manager.base_size)
        self.money_manager.streak_counter = 0
        
        # FIXED: Xóa bỏ khối mở file ghi 'wb' thừa gây lỗi xóa nội dung mô hình cũ
        if os.path.exists(pkl_path):
            with open(pkl_path, 'rb') as f:
                self.base_model = pickle.load(f)
        return True

    def _detect_market_trend_ncc(self):
        S = np.array(self.short_equity_curve, dtype=float)
        N = len(S)
        S_mean, S_std = np.mean(S), np.std(S)
        best_ncc_score, best_segment, best_match_idx = -2.0, None, -1
        
        for segment in self.long_segments:
            if len(segment) < N: continue
            for i in range(len(segment) - N + 1):
                window = segment[i : i + N]
                W_mean, W_std = np.mean(window), np.std(window)
                ncc = 0.0 if (S_std == 0 or W_std == 0) else np.sum((window - W_mean) * (S - S_mean)) / (N * W_std * S_std)
                if ncc > best_ncc_score:
                    best_ncc_score, best_match_idx, best_segment = ncc, i, segment

        if best_ncc_score < self.ncc_threshold or best_segment is None: return "---"
        K = 5
        future_start = best_match_idx + N
        future_window = best_segment[future_start : min(len(best_segment), future_start + K)]
        if len(future_window) < 2: return "---"
        slope = future_window[-1] - future_window[0]
        return "up" if slope > 0.0001 else "down" if slope < -0.0001 else "---"


# =========================================================================
# QUYẾT ĐỊNH CHIẾN LƯỢC: ĐÁNH GIÁ TỔNG QUAN ĐỂ LOAD HOẶC REBUILD MỚI
# =========================================================================
def evaluate_and_decide_model(model_name, folder_path="saved_models", min_trades=20, min_win_rate=50.0):
    """Đọc nhanh file cấu hình JSON để kiểm tra chất lượng mô hình cũ"""
    clean_name = model_name.replace(' ', '_').lower()
    json_path = os.path.join(folder_path, f"{clean_name}_state.json")
    pkl_path = os.path.join(folder_path, f"{clean_name}_base.pkl")
    
    if not os.path.exists(json_path) or not os.path.exists(pkl_path):
        return "REBUILD"
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    trades = data["stats"]["total_trades"]
    win_rate = data["stats"]["win_rate_percent"]
    profit = data["stats"]["accumulated_profit"]

    # Đánh giá điều kiện đạt tiêu chuẩn hiệu suất
    if trades >= min_trades and win_rate >= min_win_rate and profit > 0:
        return "LOAD"
    return "REBUILD"
    

# =========================================================================
# HỆ THỐNG ĐIỀU PHỐI ĐƠN LUỒNG MỖI PHIÊN (SESSION OPERATIONS)
# =========================================================================
def _get_or_load_models():
    global _GLOBAL_MODELS
    if _GLOBAL_MODELS is None:
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.neural_network import MLPClassifier
        from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.tree import DecisionTreeClassifier

        models_config = {
            "LDA": LinearDiscriminantAnalysis(),
            "KNN": KNeighborsClassifier(n_neighbors=15, weights="distance"),
            "DecisionTree": DecisionTreeClassifier(max_depth=5, min_samples_leaf=20, random_state=42),
            "RandomForest": RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_leaf=20, random_state=42, n_jobs=-1),
            "ExtraTrees": ExtraTreesClassifier(n_estimators=200, max_depth=5, min_samples_leaf=20, random_state=42, n_jobs=-1),
            "MLP": MLPClassifier(hidden_layer_sizes=(32, 16), alpha=0.01, max_iter=500, early_stopping=True, random_state=42)
        }
        
        df, dataall, labelall = make_data()
        lendic = len(models_config)

        dataall = np.array_split(dataall, lendic) 
        labelall = np.array_split(labelall, lendic) 
        sid = df['sid'].values
        sidall = np.array_split(sid, lendic)

        _GLOBAL_MODELS = []

        for i, (name, algorithm) in enumerate(models_config.items()):
            data, label, sid = dataall[i], labelall[i], sidall[i]
            train_ratio = 0.7
            split_idx = int(len(label) * train_ratio)
            data_train, label_train = data[:split_idx], label[:split_idx]
            data_long, label_long, sid_long = data[split_idx:], label[split_idx:], sid[split_idx:]

            decision = evaluate_and_decide_model(model_name=name)
            
            model = TradingModel(model_name=name)
            if decision == "LOAD":
                model.load_model_package()
                print(f"📂 [SUCCESS] Loaded stored weights & historical curves for: {name}")
            else:
                print(f"🚀 [REBUILD] Training new model pipeline for: {name}")
                model.base_model = algorithm
                model.initialize_pipeline(data_train, label_train, data_long, label_long, sid_long)
                model.save_model_package()
                
            _GLOBAL_MODELS.append(model)
            
    return _GLOBAL_MODELS


def PREDICT(x_pred):
    models = _get_or_load_models()
    for model in models: 
        model.make_predict(x_pred)


def CHECK(result):
    models = _get_or_load_models()
    for model in models: 
        model.check(result)
        model.save_model_package() 


def SET_POSITION(original_index):
    models = _get_or_load_models()
    if 0 <= original_index < len(models): 
        models[original_index].set_toggle_position()
    else:
        print(f"⚠️ Không tìm thấy mô hình nào có index gốc trên RAM là {original_index}")


def GET_ALL_INFO():
    models = _get_or_load_models()
    data = []
    
    for i, model in enumerate(models):
        info = model.get_info(origin_idx=i)
        data.append(info)

    obj_mean = {
        "model_name": "Mean", 
        "predict": None, 
        "expected_bet": None, 
        "current_position_size": None, 
        "accumulated_profit": 0, 
        "streak_counter": None, 
        "fixed_equity_curve": [], 
        "is_main": True,
        "original_index": -1
    }
    
    if data:
        # Tính trung bình số thực đơn lẻ
        profits = [obj["accumulated_profit"] for obj in data]
        obj_mean["accumulated_profit"] = round(float(np.mean(profits)), 2)
        
        # FIXED: Tính trung bình an toàn tuyệt đối, loại bỏ padding c[-1] lỗi thời gian
        curves = [obj["fixed_equity_curve"] for obj in data if len(obj["fixed_equity_curve"]) > 0]
        max_len = max(len(c) for c in curves) if curves else 0
        
        avg_curve = []
        for step in range(max_len):
            step_values = []
            for c in curves:
                # Chỉ tính toán các mô hình thực sự có dữ liệu tại thời điểm (step) đó
                if step < len(c):
                    step_values.append(c[step])
            if step_values:
                avg_curve.append(round(float(np.mean(step_values)), 2))
            
        obj_mean["fixed_equity_curve"] = avg_curve
    
    data.insert(0, obj_mean)
    return data

print("⏳ Đang khởi động ứng dụng và rà soát hệ thống mô hình nền...")
_get_or_load_models() 
print("✅ Hệ thống đã sẵn sàng nhận dữ liệu realtime!")