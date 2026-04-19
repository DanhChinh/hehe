import pandas as pd
import numpy as np
import gc
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import cross_val_predict, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from cleanlab.filter import find_label_issues
from cleanlab.dataset import health_summary



def clean_data(X, y, x_new):
    """
    Sử dụng Cleanlab để tìm và loại bỏ các dòng dữ liệu lỗi nhãn hoặc nhiễu.
    """
    print(f"--- Đang làm sạch dữ liệu ---")
    print(f"Shape gốc: X: {X.shape}, y: {y.shape}")

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    num_classes = len(le.classes_)
    print(f"Số lượng lớp: {num_classes} ({le.classes_})")

    #them x_new vào dữ liệu để đánh giá luôn: neu ra cac giai phap khi xnew chua co nhan

    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    pred_probs = cross_val_predict(clf, X, y_encoded, cv=5, method='predict_proba')

    issue_indices = find_label_issues(
        labels=y_encoded,
        pred_probs=pred_probs,
        return_indices_ranked_by='self_confidence', 
    )

    print(f"Số lượng dòng nghi ngờ lỗi: {len(issue_indices)}")

    mask = np.ones(len(y_encoded), dtype=bool)
    mask[issue_indices] = False

    X_clean = X[mask]
    y_clean_encoded = y_encoded[mask] 

    print(f"Kích thước sau khi lọc: {X_clean.shape}")
    
    health_summary(y_encoded, pred_probs)

    #kiem tra x_new con ton tai trong x_clean khong, tra ve ket qua
    
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
# # --- THỰC THI TOÀN BỘ QUY TRÌNH ---

# # 1. Load và làm sạch


import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from cleanlab.filter import find_label_issues
from cleanlab.dataset import health_summary

import matplotlib.pyplot as plt

class DataInspector:
    def __init__(self, threshold=0.6, n_estimators=100):
        self.threshold = threshold
        self.clf = RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)
        self.le = LabelEncoder()
        self.is_fitted = False

    def clean_and_train(self, X, y):
        """
        Thực hiện lọc lỗi nhãn và huấn luyện mô hình trên dữ liệu sạch.
        """
        print(f"--- Bắt đầu quá trình làm sạch dữ liệu ---")
        
        # 1. Mã hóa nhãn (Ví dụ: [1, 2] -> [0, 1])
        y_encoded = self.le.fit_transform(y)
        num_classes = len(self.le.classes_)
        print(f"Lớp phát hiện: {self.le.classes_} -> Chuyển thành: {np.unique(y_encoded)}")

        # 2. Dự đoán xác suất bằng Stratified Cross-Validation
        # Điều này đảm bảo mỗi fold đều có đủ các lớp, tránh lỗi thiếu cột trong pred_probs
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        print("Đang tính toán xác suất dự đoán (Cross-validation)...")
        pred_probs = cross_val_predict(
            self.clf, X, y_encoded, cv=skf, method='predict_proba'
        )

        # 3. Tìm các dòng lỗi nhãn bằng Cleanlab
        issue_indices = find_label_issues(
            labels=y_encoded,
            pred_probs=pred_probs,
            return_indices_ranked_by='self_confidence',
        )

        # 4. Tạo tập dữ liệu sạch
        mask = np.ones(len(y_encoded), dtype=bool)
        mask[issue_indices] = False
        
        X_clean = X[mask]
        y_clean_encoded = y_encoded[mask]
        
        print(f"Số lượng dòng lỗi bị loại bỏ: {len(issue_indices)}")
        print(f"Kích thước dữ liệu sạch: {X_clean.shape}")

        # 5. Huấn luyện mô hình chính thức trên tập dữ liệu sạch
        self.clf.fit(X_clean, y_clean_encoded)
        self.is_fitted = True

        # Hiển thị tóm tắt sức khỏe dữ liệu
        try:
            health_summary(y_encoded, pred_probs)
        except Exception as e:
            print(f"Không thể hiển thị health_summary: {e}")

        return X_clean, self.le.inverse_transform(y_clean_encoded)

    def validate_new_data(self, x_new):
        """
        Kiểm tra dữ liệu mới có hợp lệ (thuộc tập đã lọc) hay không.
        """
        if not self.is_fitted:
            raise Exception("Cần chạy clean_and_train trước khi validate!")

        # Tính xác suất cho dữ liệu mới
        probs = self.clf.predict_proba(x_new)
        max_probs = np.max(probs, axis=1)
        preds_encoded = np.argmax(probs, axis=1)
        
        # Chuyển đổi ngược nhãn về dạng gốc (1, 2)
        preds_original = self.le.inverse_transform(preds_encoded)

        results = []
        for i in range(len(x_new)):
            is_valid = max_probs[i] >= self.threshold
            results.append({
                "id": i,
                "label_pred": preds_original[i],
                "confidence": round(max_probs[i], 4),
                "is_valid": is_valid,
                "status": "Hợp lệ" if is_valid else "Nghi ngờ/Nhiễu"
            })
        
        return pd.DataFrame(results)

# --- VÍ DỤ SỬ DỤNG ---

from handle_data import make_data
if __name__ == "__main__":
    # Giả sử X là features, y là nhãn [1, 2, 1, 2...]
    X, y = make_data()  # Hàm này cần trả về X (2D array) và y (1D array)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(X_train.shape, y_train.shape)
    print(X_test.shape, y_test.shape)

    
    # Khởi tạo bộ kiểm tra với ngưỡng tin cậy 60%
    inspector = DataInspector(threshold=0.8)

    # 1. Lọc và huấn luyện
    X_clean, y_clean = inspector.clean_and_train(X_train, y_train)
    df_results = inspector.validate_new_data(X_test)
    print(df_results)
    
    #so sánh với nhãn gốc   va ve bieu do cong don
    is_true = []
    for idx, row in df_results.iterrows():        
        if row['is_valid']:
            is_true.append(1 if row['label_pred'] == y_test[idx] else -1)
        else:
            is_true.append(0)
    
    # Ve bieu do cong don
    plt.plot(np.cumsum(is_true), label="Lịch sử tích lũy")
    plt.title("Lịch sử tích lũy của mô hình sau khi lọc dữ liệu")
    plt.xlabel("Phiên giao dịch")
    plt.ylabel("Lợi nhuận tích lũy")
    plt.legend()
    plt.show()
    
