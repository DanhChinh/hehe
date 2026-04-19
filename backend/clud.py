import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
from cleanlab.filter import find_label_issues
from handle_data import make_data


import matplotlib.pyplot as plt
from handle_data import handle_progress
from connect_database import get_last_n
import json

# =========================
# 1. CLEAN DATA (NO LEAK)
# =========================
def clean_data(X, y):
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=1)

    pred_probs = cross_val_predict(
        clf, X, y_enc, cv=5, method='predict_proba'
    )

    issues = find_label_issues(
        labels=y_enc,
        pred_probs=pred_probs,
        return_indices_ranked_by='self_confidence'
    )

    # chỉ xóa 10% lỗi nặng nhất
    remove_n = int(0.1 * len(issues))
    issues = issues[:remove_n]

    mask = np.ones(len(y_enc), dtype=bool)
    mask[issues] = False

    return X[mask], y_enc[mask], le


# =========================
# 2. TRAIN PIPELINE
# =========================
def train_pipeline(n_clusters=10):
    X_raw, y_raw = make_data()

    # split trước
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X_raw, y_raw, test_size=0.15, random_state=42, stratify=y_raw
    )

    # clean train
    X_clean, y_clean, le = clean_data(X_train_full, y_train_full)

    # scale (quan trọng cho clustering)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)

    # ======================
    # CLUSTERING
    # ======================
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    # ======================
    # TRAIN MODEL CHO TỪNG CLUSTER
    # ======================
    models = {}

    for c in np.unique(clusters):
        mask = clusters == c

        model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=1
        )

        model.fit(X_clean[mask], y_clean[mask])
        models[c] = model

        print(f"Cluster {c}: {np.sum(mask)} samples")

    # ======================
    # EVALUATE
    # ======================
    y_test_enc = le.transform(y_test)

    X_test_scaled = scaler.transform(X_test)
    cluster_test = kmeans.predict(X_test_scaled)

    preds = []

    for i in range(len(X_test)):
        c = cluster_test[i]
        model = models[c]
        pred = model.predict(X_test[i].reshape(1, -1))[0]
        preds.append(pred)

    acc = accuracy_score(y_test_enc, preds)
    print(f"\nAccuracy (clustered model): {acc:.4f}")

    # ======================
    # SAVE
    # ======================
    joblib.dump(models, "cluster_models.pkl")
    joblib.dump(kmeans, "kmeans.pkl")
    joblib.dump(scaler, "scaler.pkl")
    joblib.dump(le, "label_encoder.pkl")

    print("✅ Training done & saved")


# =========================
# 3. INFERENCE
# =========================
def predict_new(x_new, models, kmeans, scaler, le, distance_threshold=2.5, confidence_threshold=0.6):

    x_new = np.array(x_new).reshape(1, -1)
    x_scaled = scaler.transform(x_new)

    # 1. tìm cluster
    cluster = kmeans.predict(x_scaled)[0]

    # 2. kiểm tra khoảng cách tới centroid
    center = kmeans.cluster_centers_[cluster]
    dist = np.linalg.norm(x_scaled - center)

    if dist > distance_threshold:
        return {
            "status": "rejected",
            "reason": "too_far_from_cluster",
            "distance": float(dist)
        }

    # 3. predict
    model = models[cluster]
    proba = model.predict_proba(x_new)
    confidence = np.max(proba)

    if confidence < confidence_threshold:
        return {
            "status": "rejected",
            "reason": "low_confidence",
            "confidence": float(confidence)
        }

    pred = model.predict(x_new)
    label = le.inverse_transform(pred)

    return {
        "status": "accepted",
        "cluster": int(cluster),
        "prediction": label[0],
        "confidence": float(confidence),
        "distance": float(dist)
    }


# =========================
# RUN
# =========================
# if __name__ == "__main__":
#     train_pipeline(n_clusters=3)

#     # ví dụ dữ liệu mới
#     x_new = [270, 30, 180, 100 ]  # sửa theo dữ liệu thật
#     result = predict_new(x_new)

#     print(result)











def run_mmodel2():
    real_time = get_last_n()  # Lấy 1000 dòng dữ liệu mới nhất
    models = joblib.load("cluster_models.pkl")
    kmeans = joblib.load("kmeans.pkl")
    scaler = joblib.load("scaler.pkl")
    le = joblib.load("label_encoder.pkl")

    history = []

    for rt in real_time:

        x_pred = handle_progress(rt['progress'], isEnd=False)
        pred = predict_new(x_pred, models, kmeans, scaler, le)
        result = 1 if int(rt['d1']) + int(rt['d2']) + int(rt['d3']) > 10 else 2

        history.append({
            "x_pred": x_pred,
            "pred": pred,
            "result": result
        })

        
    
    #ve biểu đồ lịch sử của bot
    acc_history = []
    for h in history:
        if h['pred']['status'] == 'accepted':
            acc = 1 if h['pred']['prediction'] == h['result'] else  -1
            acc_history.append(acc)
    plt.plot(np.cumsum(acc_history), label="Cumulative Accuracy")
    plt.title("Lịch sử tích lũy của bot")   
    plt.xlabel("Phiên giao dịch")
    plt.ylabel("Lợi nhuận tích lũy")
    plt.legend()
    plt.show()

train_pipeline(2)
run_mmodel2()