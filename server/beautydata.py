import pandas as pd
import numpy as np
import gc
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import cross_val_predict, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from cleanlab.filter import find_label_issues
from cleanlab.dataset import health_summary



def clean_data(X, y):
    """
    Sử dụng Cleanlab để tìm và loại bỏ các dòng dữ liệu lỗi nhãn hoặc nhiễu.
    """
    print(f"--- Đang làm sạch dữ liệu ---")
    print(f"Shape gốc: X: {X.shape}, y: {y.shape}")

    # 1. Chuẩn hóa nhãn về 0, 1, 2... (Bắt buộc cho Cleanlab)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    num_classes = len(le.classes_)
    print(f"Số lượng lớp: {num_classes} ({le.classes_})")

    # 2. Lấy xác suất dự đoán thông qua Cross-Validation
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    pred_probs = cross_val_predict(clf, X, y_encoded, cv=5, method='predict_proba')

    # 3. Tìm các chỉ số (index) dữ liệu lỗi
    issue_indices = find_label_issues(
        labels=y_encoded,
        pred_probs=pred_probs,
        return_indices_ranked_by='self_confidence', 
    )

    print(f"Số lượng dòng nghi ngờ lỗi: {len(issue_indices)}")

    # 4. Lọc dữ liệu sạch
    mask = np.ones(len(y_encoded), dtype=bool)
    mask[issue_indices] = False

    X_clean = X[mask]
    y_clean_encoded = y_encoded[mask] 

    print(f"Kích thước sau khi lọc: {X_clean.shape}")
    
    # In báo cáo sức khỏe dữ liệu (Tùy chọn)
    health_summary(y_encoded, pred_probs)
    
    return X_clean, y_clean_encoded, le

def get_beauty_model(X_clean, y_clean, model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)):
    print(f"--- Đang huấn luyện mô hình {type(model).__name__} ---")
    """
    Tách dữ liệu sạch và huấn luyện mô hình mới hoàn toàn.
    """
    # Tách Test 15%
    X_temp, X_test, y_temp, y_test = train_test_split(
        X_clean, y_clean, test_size=0.15, random_state=42, stratify=y_clean
    )

    # Tách Train 70% và Val 15% (0.1765 của 85% còn lại ~ 15% tổng)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.1765, random_state=42, stratify=y_temp
    )

    print(f"\n--- Phân chia dữ liệu sạch ---")
    print(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")

    # Khởi tạo mô hình mới (tránh dùng lại bộ nhớ mô hình cũ)
    print("Đang huấn luyện mô hình chính thức...")
    clf_final = model
    clf_final.fit(X_train, y_train)

    # Đánh giá trên tập Test sạch
    y_pred_test = clf_final.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred_test)

    print("\n" + "="*30)
    print(f"ĐỘ CHÍNH XÁC TRÊN TẬP TEST: {accuracy * 100:.2f}%")
    print("="*30)
    print(classification_report(y_test, y_pred_test))

    return clf_final, X_train

def evaluate_new_data(new_row, model, iso_model, le, threshold=0.6):
    """
    Đánh giá xem một dòng dữ liệu mới có 'đáng tin' để dự đoán không.
    """
    row = np.array(new_row).reshape(1, -1)
    
    # 1. Kiểm tra Outlier (Tính bất thường)
    is_outlier = iso_model.predict(row)[0]
    
    # 2. Kiểm tra độ tự tin của Model (Xác suất dự đoán cao nhất)
    probs = model.predict_proba(row)[0]
    max_prob = np.max(probs)
    predicted_class_idx = np.argmax(probs)
    
    # Dịch ngược về nhãn gốc
    original_label = le.inverse_transform([predicted_class_idx])[0]
    
    reasons = []
    is_good = True
    
    if is_outlier == -1:
        is_good = False
        reasons.append("Dữ liệu lạ/ngoại lai (Outlier)")
    
    if max_prob < threshold:
        is_good = False
        reasons.append(f"Độ tin cậy thấp ({max_prob*100:.1f}%)")
        
    return {
        "is_good": is_good,
        "label": int(original_label),
        "confidence": max_prob,
        "reasons": reasons
    }

# # --- THỰC THI TOÀN BỘ QUY TRÌNH ---

# # 1. Load và làm sạch
# X_raw, y_raw = make_data()
# X_clean, y_clean, label_encoder = clean_data(X_raw, y_raw)

# # Giải phóng bộ nhớ dữ liệu gốc
# del X_raw, y_raw
# gc.collect()

# # 2. Huấn luyện mô hình chuẩn
# clf_final, X_train_for_iso = get_beauty_model(X_clean, y_clean)

# # 3. Xây dựng bộ lọc Outlier dựa trên vùng dữ liệu Train sạch
# iso_forest = IsolationForest(contamination=0.01, random_state=42)
# iso_forest.fit(X_train_for_iso)

# # 4. Thử nghiệm dự đoán dữ liệu mới
# print("\n--- Đánh giá mẫu dữ liệu mới ---")
# new_data_sample = [0.5, 1.2, -0.3, 0.8] # Thay bằng dữ liệu thực tế của bạn
# eval_result = evaluate_new_data(new_data_sample, clf_final, iso_forest, label_encoder)

# if eval_result["is_good"]:
#     print(f"✅ Dữ liệu TỐT.")
#     print(f"   Dự đoán: {eval_result['label']}")
#     print(f"   Độ tin cậy: {eval_result['confidence']*100:.2f}%")
# else:
#     print(f"❌ Dữ liệu NGHI NGỜ: {', '.join(eval_result['reasons'])}")