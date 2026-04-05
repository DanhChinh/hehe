import numpy as np
import os
import json
import joblib
from state import extract_state, calculate_reward

class RLTradingSystem:

    def __init__(self, name, model, X_train, y_train, X_test, y_test):
        self.name = name
        self.path_qtable =f"qtable_{self.name}.json"
        self.path_model = f"model_{self.name}.pkl"
        self.predict = None
        self.score = 0
        self.compare_history = []
        self.score_history = []

        if os.path.exists(self.path_qtable) and os.path.exists(self.path_model):
            self.load_qtable()
            self.load_model()
        else:
            self.model = model
            self.model.fit(X_train, y_train)
            pred_test = self.model.predict(X_test)
            compare = np.where(pred_test == y_test, 1, -1)
            self.train_qtable(compare)
            self.save_qtable()
            self.save_model()


    def train_qtable(self, compare, window_size=20, future_size=10):
        self.qtable = {}

        for i in range(window_size, len(compare) - future_size):
            state = extract_state(compare, i, window_size)
            reward = calculate_reward(compare, i, future_size)

            if state not in self.qtable:
                self.qtable[state] = 0

            self.qtable[state] += reward
    def save_qtable(self):
        with open(self.path_qtable, 'w') as f:
            json.dump(self.qtable, f)
        print(f"Q-table saved to {self.path_qtable}")
    def load_qtable(self):
        with open(self.path_qtable, 'r') as f:
            self.qtable = json.load(f)
        print(f"Q-table loaded from {self.path_qtable}")
    def save_model(self):
        joblib.dump(self.model, self.path_model)    
        print(f"Model saved to {self.path_model}")
    def load_model(self):
        self.model = joblib.load(self.path_model)
        print(f"Model loaded from {self.path_model}")
    def make_predict_proba(self, x):
        self.predict = self.model.predict([x])[0]
        state = extract_state(self.compare_history)
        score = self.qtable.get(state, 0)
        self.score = score if score > 0 else 0
        return self.predict, self.score
    def check_predict_proba(self, y_true):
        if self.predict is None:
            return 
        if self.predict == y_true:
            self.score_history.append(self.score)
            self.compare_history.append(1)
        else:
            self.score_history.append(-self.score)
            self.compare_history.append(-1)