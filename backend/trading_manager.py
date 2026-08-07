from beautydata import *

from handle_db import load_data_from_pickle as make_data
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
            "bet":self.mm.bet,
            "history_mm":np.array(self.mm.history).tolist(),
            "gold":self.mm.gold,
            "isPlay":self.isPlay
        }



# --- CÁCH KHẮC PHỤC DÙNG SINGLETON SAFE-THREAD ---
from threading import Lock
_tmm_instance = None
_tmm_lock = Lock()


def get_tmm_instance():
    global _tmm_instance
    if _tmm_instance is None:
        with _tmm_lock:
            if _tmm_instance is None:
                df, data, label = make_data()
                X_clean, y_clean, le = clean_data(data, label)
                _tmm_instance = TradingModel(X_clean, y_clean, le)
    return _tmm_instance