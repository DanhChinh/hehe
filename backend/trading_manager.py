from beautydata import *

from handle_db import load_data_from_pickle as make_data
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier)


class TradingModel:
    def __init__(self, name, model, X_clean, y_clean, le):
        self.name = name
        self.predict = None
        self.history = [100] 
        self.money = 100
        self.bet = 0
        self.le = le

        self.clf_final, X_train_for_iso = get_beauty_model(X_clean, y_clean, model)
        self.iso_model = IsolationForest(contamination=0.01, random_state=42)
        self.iso_model.fit(X_train_for_iso)

        self.status = 0
                

    def make_predict(self, new_data_sample):
        self.predict = evaluate_new_data(new_data_sample, self.clf_final, self.iso_model, self.le, threshold=0.55)
        self.bet = self.money * 0.05 if self.predict else 0

        self.status = 1 if self.predict else 0


    def check(self, actual_label):
        self.money += self.bet*0.97 if (self.predict == actual_label) else - self.bet
        self.history.append(self.money)

        self.predict = None
        self.bet = 0

        self.status = 0

    def get_info(self):
        return {
            "name": str(self.name),
            "predict": self.predict,
            "history":self.history,
            "money":round(self.money, 2),
            "bet":round(self.bet, 4),
            "status":self.status

        }



class TradingModelManager:
    def __init__(self):
        self.models = []

        df, data, label = make_data()
        X_clean, y_clean, le = clean_data(data, label)
        models_config = {
            "knn": KNeighborsClassifier,
            "random_forest": RandomForestClassifier,
            "extra_trees": ExtraTreesClassifier,
            "decision_tree": DecisionTreeClassifier
        }

        for i, (name, model) in enumerate(models_config.items()):
            self.models.append(TradingModel(name, model(), X_clean, y_clean, le)) 
    def predict(self, x_pred):
        for model in self.models:
            model.make_predict(x_pred)
    def check(self, result):
        for model in self.models:
            model.check(result)
    def get_all_info(self):
        data = []
        for model in self.models:
            data.append(model.get_info())

        total_models = len(data)

        # 1. Tính toán Vote cho Predict và Bet
        total_bet_buy = sum(d.get("bet", 0) for d in data if d.get("predict") == 1)
        total_bet_sell = sum(d.get("bet", 0) for d in data if d.get("predict") == 2)

        if total_bet_buy > total_bet_sell:
            mean_predict = 1
            mean_bet = total_bet_buy - total_bet_sell
        elif total_bet_sell > total_bet_buy:
            mean_predict = 2
            mean_bet = total_bet_sell - total_bet_buy
        else:
            mean_predict = 0  # HOẶC None (Trạng thái HOLD / Hòa cược)
            mean_bet = 0

        # 2. Tính trung bình cộng Money và Status
        mean_money = sum(d.get("money", 0) for d in data) / total_models
        mean_status = sum(d.get("status", 0) for d in data) / total_models

        # 3. Tính trung bình từng phần tử trong History (nếu các model có lịch sử cùng độ dài)
        mean_history = []
        if any(d.get("history") for d in data):
            # Lấy độ dài history nhỏ nhất để tránh lỗi lệch index
            min_len = min(len(d.get("history", [])) for d in data)
            for idx in range(min_len):
                avg_val = sum(d["history"][idx] for d in data) / total_models
                mean_history.append(avg_val)

        obj_mean = {
            "name": "⭐ MEAN", 
            "predict": mean_predict, 
            "history": mean_history, 
            "money": round(mean_money, 2), 
            "bet": round(mean_bet, 2),
            "status": round(mean_status, 2),
            "is_main": True
        }

        data.insert(0, obj_mean)
        return data

# --- CÁCH KHẮC PHỤC DÙNG SINGLETON SAFE-THREAD ---
from threading import Lock
_tmm_instance = None
_tmm_lock = Lock()


def get_tmm_instance():
    """Hàm lấy instance duy nhất của TradingModelManager (Thread-safe)"""
    global _tmm_instance
    if _tmm_instance is None:
        with _tmm_lock:
            # Double-check locking để tránh tạo 2 instance cùng lúc
            if _tmm_instance is None:
                _tmm_instance = TradingModelManager()
    return _tmm_instance