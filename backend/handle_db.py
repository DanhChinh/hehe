import requests, os, json, time
import pandas as pd
import numpy as np
import math
import platform

# --- CẤU HÌNH ---
API_URL = "http://cyan.io.vn/xg79/sync_api.php"
PKL_FILE = "data.pkl"
ID_COL = "sid"

if platform.system() == "Linux":
    import sys
    sys.modules['numpy._core'] = np.core
    sys.modules['numpy._core.numeric'] = np.core.numeric

def lam_tron_bac_thu_2(n):
    if n == 0:
        return 0
    bac = int(math.log10(abs(n)))  # Bậc lớn nhất
    if bac == 0:
        return round(n)  # Không có bậc thứ 2, giữ nguyên
    base = 10 ** (bac - 1)  # Bậc lớn thứ 2
    return round(n / base) * base

def tinh_trung_binh_lam_tron_bac_thu_2(mang):
    if not mang:
        return 0
    tb = sum(mang) / len(mang)
    return lam_tron_bac_thu_2(tb)

# Đọc file CSV

def handle_progress(progress, isEnd = True):
    progress_arr = json.loads(progress)
    if isEnd and len(progress_arr) < 49 and len(progress_arr) > 63:
        return None
    sublist = progress_arr[25:29]
    data = []
    bc2 = []
    v2 = []
    bc1 = []
    v1 =  []
    for pair in sublist:
        # data.extend([pair[0]['bc'], pair[1]['bc'], pair[0]['v'],pair[1]['v']])
        bc2.append(pair[0]['bc'])
        bc1.append(pair[1]['bc'])
        v2.append(pair[0]['v'])
        v1.append(pair[1]['v'])
    bc2 = tinh_trung_binh_lam_tron_bac_thu_2(bc2)
    bc1 = tinh_trung_binh_lam_tron_bac_thu_2(bc1)
    v2 = tinh_trung_binh_lam_tron_bac_thu_2(v2)//1000000
    v1 = tinh_trung_binh_lam_tron_bac_thu_2(v1)//1000000
    if bc1 and bc2 and v1 and v2:
        return [round(bc1/(bc1+bc2), 2), round(v1/(v1+v2), 2)]
    return None

def update_local_db():
    """Vòng lặp lấy toàn bộ dữ liệu từ API cho đến khi hết sạch (Hỗ trợ Dynamic Columns)"""
    # 1. Khởi tạo/Tải database hiện có
    if os.path.exists(PKL_FILE):
        df_local = pd.read_pickle(PKL_FILE)
    else:
        df_local = pd.DataFrame()

    print("[*] Bắt đầu tiến trình đồng bộ toàn bộ dữ liệu...")

    while True:
        last_id = int(df_local[ID_COL].max()) if not df_local.empty else 0
        
        try:
            response = requests.get(API_URL, params={'last_id': last_id, 'limit': 2000}, timeout=30)
            
            if response.status_code != 200:
                print(f"[X] Lỗi Server ({response.status_code}). Đang tạm dừng...")
                break

            new_data = response.json()

            if not new_data or len(new_data) == 0:
                print("[!] Đã đồng bộ xong! Không còn dữ liệu mới trên Server.")
                break

            df_new = pd.DataFrame(new_data)
            print(f"[*] Đang xử lý đợt SID: {last_id} -> {df_new[ID_COL].max()} ({len(df_new)} dòng)")

            # Xử lý đặc trưng (Step 45) -> nhận về một mảng
            df_new['extracted'] = df_new['progress'].apply(handle_progress)
            
            df_new['target'] = df_new.apply(
                lambda r: 1 if (int(r['d1']) + int(r['d2']) + int(r['d3']) > 10) else 2, axis=1
            )

            # Lọc bỏ các dòng không đủ 45 bước
            df_valid = df_new.dropna(subset=['extracted']).copy()
            
            if not df_valid.empty:
                # --- CẢI TIẾN DÒNG NÀY: Tự động tạo tên cột feat_0, feat_1... theo độ dài mảng ---
                df_feats = pd.DataFrame(df_valid['extracted'].tolist(), index=df_valid.index)
                df_feats.columns = [f'feat_{i}' for i in range(df_feats.shape[1])]
                
                df_final_chunk = pd.concat([df_valid[[ID_COL, 'target']], df_feats], axis=1)
                
                # Gộp vào local (Pandas sẽ tự mở rộng cột nếu batch mới nhiều phần tử hơn batch cũ)
                df_local = pd.concat([df_local, df_final_chunk], ignore_index=True)
                df_local[ID_COL] = pd.to_numeric(df_local[ID_COL])
                df_local = df_local.drop_duplicates(subset=[ID_COL])
                df_local = df_local.sort_values(ID_COL).reset_index(drop=True)
                
                # Điền giá trị 0 cho các cột tính năng bị thiếu (nếu có sự lệch số lượng cột giữa các phiên bản)
                feat_cols = [c for c in df_local.columns if c not in [ID_COL, 'target']]
                df_local[feat_cols] = df_local[feat_cols].fillna(0)
                
                df_local.to_pickle(PKL_FILE)
            else:
                # --- CẢI TIẾN DÒNG NÀY: Tạo dòng dummy động, tự lấy các cột hiện có điền bằng 0 ---
                max_sid_in_batch = int(df_new[ID_COL].max())
                dummy_data = {ID_COL: [max_sid_in_batch], 'target': [0]}
                
                # Lấy toàn bộ các cột đặc trưng hiện có trong df_local để điền giá trị 0
                if not df_local.empty:
                    for col in df_local.columns:
                        if col not in [ID_COL, 'target']:
                            dummy_data[col] = [0]
                            
                dummy = pd.DataFrame(dummy_data)
                df_local = pd.concat([df_local, dummy], ignore_index=True).drop_duplicates(subset=[ID_COL])
                df_local = df_local.sort_values(ID_COL).reset_index(drop=True)
                df_local.to_pickle(PKL_FILE)

            time.sleep(0.5)

        except requests.exceptions.Timeout:
            print("[X] Timeout! Đang thử lại sau 5 giây...")
            time.sleep(5)
            continue
        except Exception as e:
            print(f"[X] Lỗi không xác định: {e}")
            break

    print(f"[OK] Tổng cộng database hiện có: {len(df_local)} phiên.")


def load_data_from_pickle():
    """Đọc dữ liệu từ file pickle và bóc tách tự động theo đặc trưng động"""
    if os.path.exists(PKL_FILE):
        df = pd.read_pickle(PKL_FILE)
        
        if df.empty:
            raise ValueError(f"File {PKL_FILE} tồn tại nhưng không có dữ liệu (rỗng).")
        
        df = df.sort_values(by='sid').reset_index(drop=True)
        
        # --- CẢI TIẾN DÒNG NÀY: Lấy động tất cả các cột ngoại trừ 'sid' và 'target' ---
        feature_cols = [col for col in df.columns if col not in [ID_COL, 'target']]
        print(f"[*] Đang tải dữ liệu huấn luyện với các đặc trưng: {feature_cols}")
        
        data = df[feature_cols].values  
        label = df['target'].values

        has_none = df.isna().any().any()
        print(f"[*] DataFrame có chứa giá trị None/NaN không? {has_none}")
        
        return df, data, label
    else:
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu tại đường dẫn: {PKL_FILE}")


