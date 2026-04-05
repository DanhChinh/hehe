import numpy as np
import random as rd
import json
from handle_data import make_data, handle_progress, handle_last_30

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    ExtraTreesClassifier
)
from sklearn.neural_network import MLPClassifier


# =========================
# TREND EVALUATION
# =========================
def evaluate_trend(data_points):
    # Lọc dữ liệu hợp lệ
    valid_points = [(x, y) for x, y in data_points if x != "-" and y != "-"]

    if len(valid_points) < 2:
        return "error"

    slopes = []
    for (x1, y1), (x2, y2) in zip(valid_points[:-1], valid_points[1:]):
        if x2 != x1:
            slopes.append((y2 - y1) / (x2 - x1))

    if not slopes:
        return "---"

    avg_slope = sum(slopes) / len(slopes)

    threshold = 0.0001

    if avg_slope > threshold:
        return "up"
    elif avg_slope < -threshold:
        return "down"
    else:
        return "---"


# =========================
# MODEL CLASS
# =========================
class TradingModel:
    def __init__(
        self,
        model_name,
        model_instance,
        X_train,
        y_train,
        X_long,
        y_long,
        X_backtest,
        y_backtest
    ):
        self.model_name = model_name
        self.model = model_instance

        # prediction
        self.raw_prediction = None
        self.adjusted_prediction = None

        # pattern matching
        self.best_match_info = None

        # performance tracking
        self.raw_history = [0]
        self.adjusted_history = [0]
        self.adjusted_cumsum = np.array([0])
        self.short_performance = np.cumsum(self.raw_history)

        # train model
        self.model.fit(X_train, y_train)

        # evaluate on long data
        long_predictions = self.model.predict(X_long)
        compare_result = np.where(long_predictions == y_long, 1, -1)
        self.long_performance = np.cumsum(compare_result)

        print(f"Training model: {model_name}...")

        # backtest loop
        for i in range(len(X_backtest)):
            x = X_backtest[i]
            y_true = y_backtest[i]

            self.find_best_pattern_match()
            self.predict(x)
            self.update_raw_history(y_true)
            self.update_adjusted_history(y_true)

    # =========================
    # PREDICT
    # =========================
    def predict(self, x_input):
        raw = int(self.model.predict([x_input])[0])
        self.raw_prediction = 1 if raw == 1 else 2

        self.adjusted_prediction = self.raw_prediction

        if self.best_match_info["trend"] == "down":
            self.adjusted_prediction = 1 if self.raw_prediction == 2 else 2

        if self.best_match_info["trend"] in ["---", "error"]:
            self.adjusted_prediction = None

    # =========================
    # UPDATE RAW HISTORY
    # =========================
    def update_raw_history(self, true_label):
        if self.raw_prediction is None:
            return

        if self.raw_prediction == true_label:
            self.raw_history.append(1)
        else:
            self.raw_history.append(-1)

        self.raw_history = self.raw_history[-15:]
        self.short_performance = np.cumsum(self.raw_history)

    # =========================
    # UPDATE ADJUSTED HISTORY
    # =========================
    def update_adjusted_history(self, true_label):
        if self.adjusted_prediction is None:
            self.adjusted_history.append(0)
        elif self.adjusted_prediction == true_label:
            self.adjusted_history.append(1)
        else:
            self.adjusted_history.append(-1)

        self.adjusted_cumsum = np.cumsum(self.adjusted_history)


    # =========================
    # NCC MATCHING
    # =========================
    def find_best_pattern_match(self):
        short_seq = np.array(self.short_performance, dtype=float)
        long_seq = np.array(self.long_performance, dtype=float)
        window_size = len(short_seq)

        short_mean = np.mean(short_seq)
        short_std = np.std(short_seq)

        ncc_scores = []

        for i in range(len(long_seq) - window_size + 1):
            window = long_seq[i:i + window_size]

            long_mean = np.mean(window)
            long_std = np.std(window)

            if short_std == 0 or long_std == 0:
                ncc = 0.0
            else:
                numerator = np.sum((window - long_mean) * (short_seq - short_mean))
                denominator = window_size * long_std * short_std
                ncc = numerator / denominator

            ncc_scores.append(ncc)

        ncc_scores = np.array(ncc_scores)

        best_index = np.argmax(ncc_scores)
        best_score = ncc_scores[best_index]

        # window config
        future_points = 5
        past_context = 1

        start_index = int(best_index)

        local_start = max(0, start_index - past_context)
        local_end = min(len(long_seq), start_index + window_size + future_points)

        local_segment = long_seq[local_start:local_end].tolist()

        # match segment
        match_segment = []
        for i in range(len(local_segment)):
            global_idx = local_start + i
            if start_index <= global_idx < start_index + window_size:
                match_segment.append([global_idx, local_segment[i]])
            else:
                match_segment.append(['-', '-'])

        # future segment
        future_segment = []
        for i in range(len(local_segment)):
            global_idx = local_start + i
            if start_index + window_size <= global_idx < start_index + window_size + future_points:
                future_segment.append([global_idx, local_segment[i]])
            else:
                future_segment.append(['-', '-'])

        self.best_match_info = {
            "best_index": start_index,
            "max_score": float(best_score),
            "window_size": int(window_size),
            "adjusted_cumsum": self.adjusted_cumsum.tolist(),
            "local_segment": local_segment,
            "local_start": local_start,
            "match_segment": match_segment,
            "future_segment": future_segment,
            "trend": evaluate_trend(future_segment),
        }


# =========================
# DATA SPLIT
# =========================
from sklearn.model_selection import StratifiedKFold

def stratified_split_10(X, y):
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

    splits = []
    for train_idx, test_idx in skf.split(X, y):
        X_part = X[test_idx]
        y_part = y[test_idx]
        splits.append((X_part, y_part))

    return splits


# =========================
# MAIN PIPELINE
# =========================
def run_pipeline(data, label):
    backtest_size = 300

    X_backtest = data[-backtest_size:]
    y_backtest = label[-backtest_size:]

    X_long = data[-1000:-backtest_size]
    y_long = label[-1000:-backtest_size]

    X_train = data[:-1000]
    y_train = label[:-1000]

    splits = stratified_split_10(X_train, y_train)

    model_dict = {
    "knn": KNeighborsClassifier,
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
    "extra_trees": ExtraTreesClassifier,
    "decision_tree": DecisionTreeClassifier
    }

    models = []

    for i, (name, ModelClass) in enumerate(model_dict.items()):
        X_part, y_part = splits[i]

        models.append(
            TradingModel(
                name,
                ModelClass(),
                X_part, y_part,
                X_long, y_long,
                X_backtest, y_backtest
            )
        )

    # =========================
    # PLOT
    # =========================
    from matplotlib import pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for model in models:
        axes[0].plot(model.long_performance, label=model.model_name)
    axes[0].set_title("LONG PERFORMANCE")
    axes[0].legend()
    axes[0].grid()

    for model in models:
        axes[1].plot(model.adjusted_cumsum, label=model.model_name)
    axes[1].set_title("ADJUSTED CUMSUM")
    axes[1].legend()
    axes[1].grid()

    plt.tight_layout()
    plt.show()


# =========================
# RUN
# =========================
data, label = make_data()

for i in range(100, 1500, 100):
    print(f"=== RUN with {i} samples ===")
    run_pipeline(data[:-i], label[:-i])