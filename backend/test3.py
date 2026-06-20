import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# ========================================================
# 1. HÀM TIỀN XỬ LÝ CHUỖI NÂNG CAO (ADVANCED FEATURE ENGINEERING)
# ========================================================
def preprocess_sequence_data_advanced(df, lag_steps=3, window_size=5):
    """
    Hàm tiền xử lý nâng cao:
    - Trích xuất lịch sử target, đếm độ dài chuỗi (streak).
    - Tính toán hệ số dốc (slope) và gia tốc (acceleration) của các feat.
    - Tính toán độ biến động cuộn (rolling std) và trung bình trượt (rolling mean).
    - Cắt bỏ hoàn toàn các mẫu dữ liệu bị nhảy cóc/ngắt quãng phiên (sid).
    """
    # Sắp xếp chuẩn theo thứ tự phiên sid để đảm bảo tính tuyến tính
    data = df.copy().sort_values('sid').reset_index(drop=True)
    
    # Tự động nhận diện các cột đặc trưng gốc bắt đầu bằng 'feat_'
    feature_cols = [col for col in data.columns if col.startswith('feat_')]
    new_cols = {}
    
    # ----------------------------------------------------
    # NHÓM 1: TRÍCH XUẤT LỊCH SỬ TARGET & CHUỖI ĐANG DIỄN RA
    # ----------------------------------------------------
    for lag in range(1, lag_steps + 1):
        # Lưu kết quả của các phiên trước đó vào phiên hiện tại
        new_cols[f'target_lag_{lag}'] = data['target'].shift(lag)
    
    # Tính chuỗi lặp liên tiếp thực tế (Streak Length) của target đứng trước
    target_shifted = data['target'].shift(1)
    streak_group = (target_shifted != target_shifted.shift(1)).cumsum()
    new_cols['target_streak_len'] = target_shifted.groupby(streak_group).cumcount() + 1

    # ----------------------------------------------------
    # NHÓM 2: TÍNH HỆ SỐ DỐC (SLOPE) & GIA TỐC CỦA CÁC FEAT
    # ----------------------------------------------------
    for col in feature_cols:
        # Độ dốc bậc 1 (Vận tốc thay đổi giữa ván này và ván trước)
        diff_1 = data[col] - data[col].shift(1)
        # Độ dốc bậc 2 (Gia tốc lực đẩy)
        diff_2 = diff_1 - diff_1.shift(1)
        
        new_cols[f'{col}_slope_v1'] = diff_1
        new_cols[f'{col}_acceleration_v2'] = diff_2

    # ----------------------------------------------------
    # NHÓM 3: MẬT ĐỘ BIẾN ĐỘNG CUỘN (ROLLING VOLATILITY)
    # ----------------------------------------------------
    for col in feature_cols:
        # Độ lệch chuẩn cuộn để đo độ bất ổn định của phiên gần nhất
        new_cols[f'{col}_roll_std_{window_size}'] = data[col].shift(1).rolling(window=window_size, min_periods=1).std()
        # Trung bình trượt cuộn để khử nhiễu tín hiệu
        new_cols[f'{col}_roll_mean_{window_size}'] = data[col].shift(1).rolling(window=window_size, min_periods=1).mean()

    # Nối tất cả các cột đặc trưng mới vào DataFrame gốc
    df_features = pd.concat([data, pd.DataFrame(new_cols)], axis=1)
    
    # ----------------------------------------------------
    # BỘ LỌC CHUỖI LIÊN TỤC (CRITICAL FILTER)
    # ----------------------------------------------------
    # Xác định độ sâu lùi lịch sử lớn nhất cần kiểm tra tính liên tục
    max_lookback = max(lag_steps, window_size)
    valid_mask = np.ones(len(df_features), dtype=bool)
    
    for lag in range(1, max_lookback + 1):
        # Khoảng cách giữa số thứ tự phiên (sid) hiện tại và quá khứ phải bằng đúng số bước nhảy
        is_continuous = (df_features['sid'] - df_features['sid'].shift(lag)) == lag
        valid_mask = valid_mask & is_continuous
        
    # Tiến hành cắt bỏ các phiên đứt gãy lịch sử
    df_cleaned = df_features[valid_mask].reset_index(drop=True)
    
    # Điền khuyết một vài giá trị NaN phát sinh nếu có bằng 0 để an toàn cho mô hình
    df_cleaned = df_cleaned.fillna(0)
    
    return df_cleaned

# ========================================================
# 2. HÀM ĐỐI CHIẾU HIỆU NĂNG (RAW VS PROCESSED)
# ========================================================
def compare_raw_vs_processed(df_train_raw, df_test_raw, lag_steps=3, window_size=5):
    """
    Huấn luyện song song mô hình trên đặc trưng gốc và đặc trưng nâng cao 
    để đánh giá mức độ cải thiện hiệu năng dự đoán trên cùng một tập Test sạch.
    """
    # Thực hiện chạy qua hàm xử lý chuỗi nâng cao
    df_train_processed = preprocess_sequence_data_advanced(df_train_raw, lag_steps, window_size)
    df_test_processed = preprocess_sequence_data_advanced(df_test_raw, lag_steps, window_size)
    
    # Định nghĩa danh sách các cột tính năng cho 2 mô hình độc lập
    raw_features = [col for col in df_train_raw.columns if col.startswith('feat_')]
    # Mô hình nâng cao lấy tất cả các cột ngoại trừ sid và target
    processed_features = [col for col in df_train_processed.columns if col not in ['sid', 'target']]
    
    # ----------------------------------------------------
    # MÔ HÌNH 1: HUẤN LUYỆN TRÊN BỘ DỮ LIỆU NGUYÊN BẢN (RAW)
    # ----------------------------------------------------
    X_train_raw = df_train_raw[raw_features]
    y_train_raw = df_train_raw['target']
    
    # Kiểm thử trên tập dữ liệu sạch để đảm bảo công bằng trong so sánh toán học
    X_test_raw_mode = df_test_processed[raw_features] 
    y_test_target = df_test_processed['target']
    
    model_raw = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model_raw.fit(X_train_raw, y_train_raw)
    y_pred_raw = model_raw.predict(X_test_raw_mode)
    
    # ----------------------------------------------------
    # MÔ HÌNH 2: HUẤN LUYỆN TRÊN BỘ DỮ LIỆU CHUỖI NÂNG CAO
    # ----------------------------------------------------
    X_train_proc = df_train_processed[processed_features]
    y_train_proc = df_train_processed['target']
    X_test_proc = df_test_processed[processed_features]
    
    model_proc = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model_proc.fit(X_train_proc, y_train_proc)
    y_pred_proc = model_proc.predict(X_test_proc)
    
    # ----------------------------------------------------
    # TRÍCH XUẤT VÀ IN BẢNG ĐỐI CHIẾU THỐNG KÊ KẾT QUẢ
    # ----------------------------------------------------
    metrics = {
        'Chỉ số Đánh giá': [
            'Accuracy (Độ chính xác)', 
            'F1-Score (Độ cân bằng)', 
            'Precision (Độ chuẩn xác)', 
            'Recall (Độ nhạy)'
        ],
        'Mô hình GỐC (Raw Data)': [
            accuracy_score(y_test_target, y_pred_raw),
            f1_score(y_test_target, y_pred_raw),
            precision_score(y_test_target, y_pred_raw),
            recall_score(y_test_target, y_pred_raw)
        ],
        'Mô hình CHUỖI (Processed)': [
            accuracy_score(y_test_target, y_pred_proc),
            f1_score(y_test_target, y_pred_proc),
            precision_score(y_test_target, y_pred_proc),
            recall_score(y_test_target, y_pred_proc)
        ]
    }
    
    df_report = pd.DataFrame(metrics)
    
    # Tính toán phần trăm cải thiện giữa 2 phương pháp
    df_report['Mức cải thiện (%)'] = ((df_report['Mô hình CHUỖI (Processed)'] - df_report['Mô hình GỐC (Raw Data)']) * 100).round(2)
    
    print("\n" + "=" * 90)
    print(f"     BẢNG SO SÁNH HIỆU NĂNG DỰ ĐOÁN THỰC TẾ TRÊN TẬP KIỂM THỬ (TEST SET)")
    print("=" * 90)
    print(df_report.to_string(index=False, formatters={
        'Mô hình GỐC (Raw Data)': '{:,.4f}'.format,
        'Mô hình CHUỖI (Processed)': '{:,.4f}'.format,
        'Mức cải thiện (%)': '{:+,}%'.format
    }))
    print("=" * 90)
    print(f"(*) Tập học thô ban đầu: {len(df_train_raw)} dòng -> Sau khi lọc chuỗi nâng cao còn: {len(df_train_processed)} dòng.")

# ========================================================
# 3. KHỞI CHẠY HỆ THỐNG VỚI PICKLE DATA
# ========================================================
if __name__ == "__main__":
    # Thiết lập seed để đồng bộ hóa ngẫu nhiên trong Random Forest
    np.random.seed(101)
    
    # Nạp dữ liệu thực tế từ module quản lý cơ sở dữ liệu của bạn
    from handle_db import load_data_from_pickle
    df, _, _ = load_data_from_pickle()
    
    # Sắp xếp tuyến tính theo sid trước khi thực hiện chia cắt tập dữ liệu
    df = df.sort_values('sid').reset_index(drop=True)
    
    # Chia tập dữ liệu Train/Test theo trình tự chuỗi (Thời gian/Thứ tự phiên)
    # Giữ 75% dữ liệu cũ để học (Train), 25% dữ liệu mới nhất để kiểm chứng (Test)
    ty_le_train = 0.75
    vi_tri_cat = int(len(df) * ty_le_train)
    
    raw_train = df.iloc[:vi_tri_cat].reset_index(drop=True)
    raw_test = df.iloc[vi_tri_cat:].reset_index(drop=True)
    
    print("=== THÔNG TIN BỘ DỮ LIỆU THỰC TẾ VỪA NẠP ===")
    print(f"• Tổng số mẫu nạp từ Pickle: {len(df)} dòng")
    print(f"• Kích thước phân bổ Train : {len(raw_train)} dòng")
    print(f"• Kích thước phân bổ Test  : {len(raw_test)} dòng")
    
    # Tiến hành đối chiếu hiệu năng
    # Bạn có thể tăng giảm cấu hình lag_steps và window_size tại đây để tối ưu mô hình
    compare_raw_vs_processed(raw_train, raw_test, lag_steps=3, window_size=5)