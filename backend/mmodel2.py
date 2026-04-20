import numpy as np
import random as rd
import json

from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from beautydata import *
from handle_db import load_db_as_df, handle_progress

def get_price(arr):
    if len(arr)<1:
        return 0
    return int(np.cumsum(arr)[-1])



class MYMODEL:
    def __init__(self, name, model, X_clean, y_clean, le):
        self.name = name
        self.history = []  # Danh sách lưu các giao dịch hoặc kết quả dự đoán
        self.position = None
        self.stop_loss = None
        self.take_profit = None
        self.predict = None
        self.le = le


        # Khởi tạo mô hình chính và bộ lọc Outlier
        self.clf_final, X_train_for_iso = get_beauty_model(X_clean, y_clean, model)
        self.iso_model = IsolationForest(contamination=0.01, random_state=42)
        self.iso_model.fit(X_train_for_iso)

    def make_predict(self, new_data_sample):
        self.predict = evaluate_new_data(new_data_sample, self.clf_final, self.iso_model, self.le, threshold=0.55)
        # current_observation = self.history[-5:] if len(self.history) >= 5 else self.history
        # self.avg_future_score = self.analyzer.get_score_by_state(current_observation)['avg_future_score']

    def check(self, actual_result):
        if self.predict is None or self.predict['is_good'] is False:
            self.history.append(0)
            self.predict = None
            return

        confidence = self.predict['confidence']
        if self.predict['label'] == actual_result:
            self.history.append(1)
        else:
            self.history.append(-1)
        self.predict = None


    def get_info(self):

        return {
            "name": str(self.name),
            "predict": self.predict['label'] if self.predict else None,
            "is_good": self.predict['is_good'] if self.predict else None,
            "confidence": self.predict['confidence'] if self.predict else None,
            "position": self.position, 
            "stop_loss": float(self.stop_loss) if self.stop_loss  else None,
            "take_profit": float(self.take_profit) if self.take_profit  else None,
            "price": get_price(self.history),
            "history_cumsum": np.cumsum(self.history).tolist()
        }

    def set_toggle_position(self):
        if self.position == "BUY":
            self.set_sell()
        else:
            self.set_buy()

    def set_buy(self):
        price = get_price(self.history)
        self.position = "BUY"
        self.stop_loss = float(price - 5)
        self.take_profit = float(price + 10)

    def set_sell(self):
        self.position = None
        self.stop_loss = None 
        self.take_profit = None




def PREDICT(x_pred):
    for model in models:
        model.make_predict(x_pred)
def CHECK(result):
    for model in models:
        model.check(result)
def SET_POSITON(index):
    models[index].set_toggle_position()


def GET_ALL_INFO():
    data = []
    for model in models:
        data.append(model.get_info())
    for dt in data:
        try:
            json.dumps(dt)
        except TypeError as e:
            print("❌ JSON ERROR:", e)
            
            # check từng field
            for k, v in dt.items():
                try:
                    json.dumps(v)
                except TypeError:
                    print(f"👉 Lỗi ở field: {k}, type = {type(v)}")
    return data





def LOAD():

    df = load_db_as_df()#.iloc[:-800]
    print(df)
    X_clean, y_clean, le = clean_data(np.stack(df['progress'].values), df['label'].to_numpy())

    model_dict = {
        "knn": KNeighborsClassifier,
        "random_forest": RandomForestClassifier,
        "decision_tree": DecisionTreeClassifier
    }

    models = []


    for i, (name, Model) in enumerate(model_dict.items()):
        models.append(
            MYMODEL(
                name, 
                Model(),
                X_clean, y_clean,
                le
                )
        )


    return models

models = LOAD()