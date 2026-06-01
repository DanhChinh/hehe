import requests, os, json, time
import pandas as pd
import numpy as np

# --- CẤU HÌNH ---
API_URL = "http://cyan.io.vn/xg79/sync_api.php"
PKL_FILE = "data_ratio.pkl"
ID_COL = "sid"

def process_ratios_step45(progress):
    """Trích xuất tỉ lệ v và bc tại bước 45 để làm đặc trưng huấn luyện"""
    try:
        data = json.loads(progress)
        if len(data) < 45: return None
        s45 = data[44] # Lấy chính xác bước 45
        
        # Phe 1
        v1, bc1 = float(s45[0]['v']), float(s45[0]['bc'])
        # Phe 2
        v2, bc2 = float(s45[1]['v']), float(s45[1]['bc'])
        
        return {
            'v_ratio': v1 / (v1 + v2 + 1e-9),
            'bc_ratio': bc1 / (bc1 + bc2 + 1e-9)
        }
    except:
        return None


import time

def update_local_db():
    """Vòng lặp lấy toàn bộ dữ liệu từ API cho đến khi hết sạch"""
    # 1. Khởi tạo/Tải database hiện có
    if os.path.exists(PKL_FILE):
        df_local = pd.read_pickle(PKL_FILE)
    else:
        df_local = pd.DataFrame()

    print("[*] Bắt đầu tiến trình đồng bộ toàn bộ dữ liệu...")

    while True:
        # Lấy SID cao nhất hiện tại để làm điểm bắt đầu cho yêu cầu tiếp theo
        last_id = int(df_local[ID_COL].max()) if not df_local.empty else 0
        
        try:
            # Lấy từng đợt 2000 phiên để tránh quá tải API
            response = requests.get(API_URL, params={'last_id': last_id, 'limit': 2000}, timeout=30)
            
            if response.status_code != 200:
                print(f"[X] Lỗi Server ({response.status_code}). Đang tạm dừng...")
                break

            new_data = response.json()

            # ĐIỀU KIỆN DỪNG: Nếu API trả về mảng rỗng nghĩa là đã lấy hết dữ liệu
            if not new_data or len(new_data) == 0:
                print("[!] Đã đồng bộ xong! Không còn dữ liệu mới trên Server.")
                break

            df_new = pd.DataFrame(new_data)
            print(f"[*] Đang xử lý đợt SID: {last_id} -> {df_new[ID_COL].max()} ({len(df_new)} dòng)")

            # Xử lý đặc trưng (Step 45)
            df_new['extracted'] = df_new['progress'].apply(process_ratios_step45)
            
            # Lưu ý: Chúng ta xử lý Target trước khi Dropna để không mất dấu last_id
            df_new['target'] = df_new.apply(
                lambda r: 1 if (int(r['d1']) + int(r['d2']) + int(r['d3']) <= 10) else 0, axis=1
            )

            # Lọc bỏ các dòng không đủ 45 bước
            df_valid = df_new.dropna(subset=['extracted']).copy()
            
            if not df_valid.empty:
                df_feats = pd.DataFrame(df_valid['extracted'].tolist(), index=df_valid.index)
                df_final_chunk = pd.concat([df_valid[[ID_COL, 'target']], df_feats], axis=1)
                
                # Gộp vào local
                df_local = pd.concat([df_local, df_final_chunk], ignore_index=True)
                df_local[ID_COL] = pd.to_numeric(df_local[ID_COL])
                df_local = df_local.drop_duplicates(subset=[ID_COL])
                df_local = df_local.sort_values(ID_COL).reset_index(drop=True)
                
                # Lưu file tạm sau mỗi vòng lặp để tránh mất dữ liệu nếu gặp lỗi mạng
                df_local.to_pickle(PKL_FILE)
            else:
                # Nếu đợt này không có phiên nào hợp lệ, chúng ta vẫn phải cập nhật last_id 
                # bằng cách tạo một dòng dummy chứa SID cao nhất để vòng lặp sau tiến lên tiếp
                max_sid_in_batch = int(df_new[ID_COL].max())
                dummy = pd.DataFrame({ID_COL: [max_sid_in_batch], 'target': [0], 'v_ratio': [0], 'bc_ratio': [0]})
                df_local = pd.concat([df_local, dummy]).drop_duplicates(subset=[ID_COL])
                df_local.to_pickle(PKL_FILE)

            # Nghỉ ngắn giữa các lần gọi để tránh bị Server chặn (Rate Limit)
            time.sleep(0.5)

        except requests.exceptions.Timeout:
            print("[X] Timeout! Đang thử lại sau 5 giây...")
            time.sleep(5)
            continue
        except Exception as e:
            print(f"[X] Lỗi không xác định: {e}")
            break

    print(f"[OK] Tổng cộng database hiện có: {len(df_local)} phiên.")



def load_data():
    if os.path.exists(PKL_FILE):
        return pd.read_pickle(PKL_FILE)
    return pd.DataFrame()

if __name__ == "__main__":
    update_local_db()