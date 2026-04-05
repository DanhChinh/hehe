import numpy as np
from sklearn.preprocessing import StandardScaler
import sys
import os
sys.path.append(os.path.abspath(".."))
from handle_data import make_data


def make_data_3():

    # models = {
    #     "knn": KNeighborsClassifier(),
    #     "decision_tree": DecisionTreeClassifier(),
    #     "random_forest": RandomForestClassifier()
    # }

    X, y = make_data()
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    n = len(X)

    train_size = int(n * 0.7)
    test_size = int(n * 0.25)

    # =========================
    # SPLIT
    # =========================
    X_train = X[:train_size]
    y_train = y[:train_size]

    X_test = X[train_size:train_size + test_size]
    y_test = y[train_size:train_size + test_size]

    X_pred = X[train_size + test_size:]
    y_pred = y[train_size + test_size:]

    return scaler, X_train, y_train, X_test, y_test, X_pred, y_pred




