import numpy as np
import pandas as pd
from handle_data import make_data

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    ExtraTreesClassifier
)
from matplotlib import pyplot as pt


# =========================
# LOAD DATA
# =========================
scaler = StandardScaler()
data, label = make_data()
data = scaler.fit_transform(data)

index = 300

X_train = data[:-index]
y_train = label[:-index]
X_test = data[-index:]
y_test = label[-index:]


# =========================
# MODEL LIST
# =========================
model_dict = {
    "knn": KNeighborsClassifier,
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
    "extra_trees": ExtraTreesClassifier,
    "decision_tree": DecisionTreeClassifier
}


# =========================
# BUILD STATE FROM RESULT
# =========================
def build_state_from_result(results, window_size=20, future_size=10):
    rows = []

    for model_name, compare in results.items():

        for i in range(window_size, len(compare) - future_size):
            past_window = compare[i - window_size:i]
            future_window = compare[i:i + future_size]

            # =========================
            # STATE (GIẢM OVERFIT)
            # =========================
            block_size = 5
            state_blocks = []

            for j in range(0, window_size, block_size):
                block = past_window[j:j + block_size]
                state_blocks.append(int(np.sum(block)))

            state = tuple(state_blocks)

            # =========================
            # REWARD (TƯƠNG LAI)
            # =========================
            reward = int(np.sum(future_window))

            rows.append({
                "model": model_name,
                "state": str(state),
                "reward": reward
            })

    return pd.DataFrame(rows)


# =========================
# RUN MODELS
# =========================
def run_models(X_train, y_train, X_test, y_test):
    results = {}

    pt.figure(figsize=(16, 6))

    for name, ModelClass in model_dict.items():
        model = ModelClass()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        # bias check
        bias = np.mean(predictions == 1)
        print(f"Tỷ lệ {name} class 1: {bias:.2%}")

        # compare result
        compare = np.where(predictions == y_test, 1, -1)
        results[name] = compare

    # =========================
    # BUILD STATE DATASET
    # =========================
    df = build_state_from_result(results)

    # =========================
    # SAVE CSV
    # =========================
    df.to_csv("state_analysis.csv", index=False)
    print("Saved: state_analysis.csv")

    # =========================
    # SUMMARY (Q-table)
    # =========================
    summary = df.groupby(["model", "state"])["reward"].mean().reset_index()
    summary.to_csv("state_summary.csv", index=False)
    print("Saved: state_summary.csv")

    return df, summary


# =========================
# RUN
# =========================
df, summary = run_models(X_train, y_train, X_test, y_test)