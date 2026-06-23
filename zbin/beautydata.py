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

def doidudoan(nhan):
    if nhan == 1:
        return 2
    return 1


def evaluate_new_data(new_row, model, iso_model, le, threshold=0.8):
    """
    Đánh giá xem một dòng dữ liệu mới có đạt tiêu chuẩn 'vàng' để dự đoán hay không.
    """
    # Đảm bảo đầu vào là ma trận (1, 4)
    row = np.array(new_row).reshape(1, -1)
    
    # 1. Kiểm tra Outlier (Sử dụng Isolation Forest đã fit trên X_train sạch)
    # 1 là bình thường (Inlier), -1 là bất thường (Outlier)
    is_outlier_signal = iso_model.predict(row)[0]
    
    # 2. Lấy xác suất dự đoán từ RandomForest
    probs = model.predict_proba(row)[0]
    max_prob = float(np.max(probs)) # Chuyển về float chuẩn
    predicted_class_idx = np.argmax(probs)
    
    # Dịch ngược về nhãn gốc từ LabelEncoder
    original_label = le.inverse_transform([predicted_class_idx])[0]
    
    reasons = []
    
    # Kiểm tra điều kiện 1: Phải nằm trong phân phối quen thuộc
    if is_outlier_signal == -1:
        reasons.append("Outlier (Dữ liệu lạ)")
    
    # Kiểm tra điều kiện 2: Độ tin cậy phải vượt ngưỡng (ví dụ 80%)
    if max_prob < threshold:
        reasons.append(f"Confidence thấp ({max_prob*100:.1f}%)")
        
    # CHỈ COI LÀ TỐT khi không có bất kỳ lý do loại bỏ nào
    is_good = len(reasons) == 0
    
    return {
        "is_good": is_good,
        "label": int(doidudoan(original_label)), # Ép kiểu về int để an toàn cho JSON/Trading
        "confidence": max_prob,
        "reasons": reasons
    }

# from handle_db import load_db_as_df, update_local_db


# df = load_db_as_df()

# progress = np.stack(df['progress'].values)

# print(progress)

#tai sao ket qua tra ve lai la [list([,,,,]), list([,,,]), ...] thay vi [[,,,],[,,,],...]
