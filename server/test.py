import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 10 models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from handle_data import make_data

# =========================
# 1. MAIN PIPELINE
# =========================
def run_pipeline(X, y):

    # --- train test split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, shuffle=False
    )

    # =========================
    # 2. Tạo model
    # =========================
    models = {
        "Logistic": LogisticRegression(max_iter=1000),
        "DecisionTree": DecisionTreeClassifier(),
        "RandomForest": RandomForestClassifier(),
        "KNN": KNeighborsClassifier(),
        "NaiveBayes": GaussianNB(),
        "MLP": MLPClassifier(max_iter=1000),
        "AdaBoost": AdaBoostClassifier(),
        "GradientBoost": GradientBoostingClassifier(),
        "LDA": LinearDiscriminantAnalysis()
    }

    results = {}
    cumulative_curves = []
    y_pred_all = []

    # =========================
    # 3. Train + Predict
    # =========================
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_pred_all.append(y_pred)

        # accuracy tổng
        acc = accuracy_score(y_test, y_pred)
        print(f"{name}: {acc:.4f}")

        # =========================
        # 4. Cumulative accuracy
        # =========================
        correct = np.where(y_pred == y_test, 1, -1)
        cumulative = np.cumsum(correct)

        results[name] = cumulative
        cumulative_curves.append(cumulative)
    #viet tiep code o day de tinh y_pred_all theo nguyen tac bo phieu, sau do so sanh no voi y_test, ve bieu do


    # =========================
    # 5. Trung bình
    # =========================
    avg_curve = np.mean(cumulative_curves, axis=0)
    avg_y_pred = np.mean(y_pred_all, axis=0)
    print(avg_y_pred)
    avg_y_pred = np.where(avg_y_pred > 1.5, 2, 1)

    correct = np.where(avg_y_pred == y_test, 1, -1)
    cumulative = np.cumsum(correct)

    



    # =========================
    # 6. Vẽ biểu đồ
    # =========================
    plt.figure(figsize=(12, 6))

    for name, curve in results.items():
        plt.plot(curve, label=name, alpha=0.6)

    # đường trung bình (đậm hơn)
    plt.plot(avg_curve, label="Average", linewidth=3, linestyle="--")
    # voting (đậm nhất)
    plt.plot(cumulative, label="Voting Ensemble", linewidth=3)

    plt.title("Cumulative Accuracy of Models")
    plt.xlabel("Samples")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid()

    plt.show()

    return results, avg_curve

data, label = make_data()
for i in range(10):
    run_pipeline(data, label)