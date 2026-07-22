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
        self.money += self.bet if (self.predict == actual_label) else - self.bet
        self.history.append(self.money)

        self.predict = None
        self.bet = 0

        self.status = 0

    def get_info(self):
        return {
            "name": str(self.name),
            "predict": self.predict,
            "history":self.history,
            "money":self.money,
            "bet":self.bet,
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
        return data

