from beautydata import *
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier)


class MoneyManager:
    def __init__(self):
        self.gold = 100
        self.bet = 0
        self.history = [self.gold]
        self.isPlay = False
    def update(self, profit):
        if profit == 1:
            self.gold += self.bet*0.97
        elif profit == -1:
            self.gold -= self.bet
        else:
            pass
        self.history.append(self.gold)
    def calc_bet(self, isPlay, predict):
        self.bet = round(0.05 * self.gold, 2) if (isPlay and predict) else 0

class TradingModel:
    def __init__(self, X_clean, y_clean, le):
        self.name = "knn"
        self.predict = None
        self.predict_fixed = None
        self.le = le
        self.history = [0]
        self.clf_final, X_train_for_iso = get_beauty_model(X_clean, y_clean, KNeighborsClassifier())
        self.iso_model = IsolationForest(contamination=0.01, random_state=42)
        self.iso_model.fit(X_train_for_iso)

        self.isReverse = False
        self.isPlay = False
        self.mm = MoneyManager()

        self.tp = 50
        self.sl = -50
        self.isShow = True
        self.volume = 1000
        self.invest = 0

    def make_predict(self, new_data_sample):
        self.predict = evaluate_new_data(new_data_sample, self.clf_final, self.iso_model, self.le)
        self.predict_fixed = 3 - self.predict if (self.predict and self.isReverse) else self.predict
        self.mm.calc_bet(self.isPlay, self.predict_fixed)
        print(f"Predict: {self.predict}, Bet: {self.mm.bet}, Gold: {self.mm.gold}, isPlay: {self.isPlay}, isReverse: {self.isReverse}")
    def check(self, actual_label):
        isTrue = 1 if self.predict == actual_label else -1 if self.predict is not None else 0
        profit = 1 if self.predict_fixed == actual_label else -1 if self.predict_fixed is not None else 0
        self.history.append(isTrue)
        self.mm.update(profit)
        self.predict = None
        self.predict_fixed = None
    def get_all_info(self):
        return {
            "name": self.name,
            "predict": self.predict_fixed if (self.isReverse and self.predict_fixed) else self.predict_fixed,
            "history_tm":np.cumsum(self.history).tolist(),
            "history_mm":np.array(self.mm.history).tolist(),
            "bet":self.mm.bet,
            "gold":self.mm.gold,
            "isPlay":self.isPlay,
            "isReverse": self.isReverse,
            "tp":self.tp,
            "sl":self.sl,
            "isShow": self.isShow,
            "volume":self.volume,
            "invest":self.invest
        }

class TMM:
    def __init__(self, zipxy, le):
        self.arr = [TradingModel(x, y, le) for x, y in zipxy]
    def make_predict(self, new_data_sample):
        for item in self.arr:
            item.make_predict(new_data_sample)
    def check(self, actual_label):
        for item in self.arr:
            item.check(actual_label)
    def get_all_info(self):
        data = []
        for item in self.arr:
            data.append(item.get_all_info())
        return data
    def set_property(self, idx, prop, val):
        if 0 <= idx < len(self.arr):
            # Sử dụng setattr để gán giá trị cho thuộc tính của đối tượng
            setattr(self.arr[idx], prop, val)


# --- CÁCH KHẮC PHỤC DÙNG SINGLETON SAFE-THREAD ---
from threading import Lock
_tmm_instance = None
_tmm_lock = Lock()


def get_tmm_instance():
    global _tmm_instance
    if _tmm_instance is None:
        with _tmm_lock:
            if _tmm_instance is None:
                X_clean, y_clean, le = load_clean()
                X_splits = np.array_split(X_clean, 10)
                y_splits = np.array_split(y_clean, 10)

                _tmm_instance = TMM(zip(X_splits, y_splits), le) 

                # setattr(_tmm_instance.arr[0], "tp", 1000)
    return _tmm_instance
    