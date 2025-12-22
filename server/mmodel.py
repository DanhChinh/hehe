import numpy as np
import random as rd
from handle_data import make_data, handle_progress
from connect_database import get_jsonmodels, saveModel
from evaluate_model import rank_models


from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    ExtraTreesClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier

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


class MYMODEL:
    def __init__(self, name, model, stat):
        self.name = name
        self.model = model
        self.stat = stat
    def load(self, data_train, label_train, data_long, label_long):
        self.model.fit(data_train, label_train)
        pred_p2 = self.model.predict(data_long)
        compare = np.where(pred_p2 == label_long, 1, -1)
        self.LONG_ARRAY = np.cumsum(compare)
        self.history = [rd.choice([-1,1]) for i in range(15)]
        self.history_fix = [0]
        self.history_fix_cumsum = np.array([])
        self.short_array = np.cumsum(self.history)
        self.predict = None
        self.predict_fix = None
        self.best_match = None
        return self.LONG_ARRAY
    def make_predict(self, x_pred):
        self.predict = 1 if int(self.model.predict([x_pred])[0]) ==1 else 2
        self.predict_fix = self.predict
        if self.best_match["trend"] == "down":
            self.predict_fix = 1 if self.predict == 2 else 2
        if self.best_match["trend"] == "---" or self.best_match["trend"] == "error":
            self.predict_fix = None
        print(self.name, self.best_match["trend"], self.predict, self.predict_fix)
        return self.predict_fix

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
            "W_centered": W_centered.tolist(),

            #other
            'modelName':self.name,
            'stat_score': f"{self.stat['score']:.4f}"
        }
        return self.best_match






def FIND_BEST_MATCHS(): 
    data = []
    for model in models:
        data.append(model.find_best_match_ncc())
    return data
def PREDICT(x_pred):
    predicts = []
    for model in models:
        predicts.append(model.make_predict(x_pred))
    return predicts
def CHECK(result):
    for model in models:
        model.check(result)
        model.check_fix(result)


def SAVE_MODELS():
    for model in models:
        modelName = model.name
        session = model.history_fix_cumsum
        saveModel(modelName, session)
    print('save all: done')


def LOAD():

    models_dict = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "SVM (RBF)": SVC(kernel="rbf", probability=True),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Extra Trees": ExtraTreesClassifier(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(),
        "AdaBoost": AdaBoostClassifier(n_estimators=100),
        "Naive Bayes": GaussianNB(),
        "LDA": LinearDiscriminantAnalysis(),
        "MLP (Neural Network)": MLPClassifier(hidden_layer_sizes=(100,), max_iter=500)
    }
    data, label = make_data()
    N = len(label)

    # Chia thành 2 phần
    train_ratio = 0.7
    split_idx = int(N * train_ratio)

    # Part 1: Train
    data_train = data[:split_idx]
    label_train = label[:split_idx]

    # Part 2: Long
    data_long = data[split_idx:]
    label_long = label[split_idx:]

    # ===============================
    # 2. TRAIN RANDOM FOREST
    # ===============================
    jsmodels = get_jsonmodels()
    ranking = rank_models(jsmodels)

    models = []

    for i, (name, stat) in enumerate(ranking, 1):
        models.append( MYMODEL(name, models_dict[name], stat) )


    LONGS = []
    for model in models:
        LONGS.append(model.load(
            data_train, label_train,
            data_long, label_long
        ))
    numOfModel =  len (models)
    return models, LONGS, numOfModel

models, LONGS, numOfModel = LOAD()