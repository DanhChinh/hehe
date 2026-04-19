import requests
import pandas as pd
import os
import time
from  handle_data import handle_progress

API_URL = "http://cyan.io.vn/xg79/sync_api.php"
CSV_FILE = "data_local.csv"
ID_COL = "sid"
CHUNK_SIZE = 5000  

def sync_data():
    while True:
        # 1. Tìm ID cuối cùng từ file
        last_id = 0
        file_exists = os.path.isfile(CSV_FILE)
        if file_exists:
            df_last = pd.read_csv(CSV_FILE, usecols=[ID_COL])
            if not df_last.empty:
                last_id = int(df_last[ID_COL].max())

        print(f"Đang tải {CHUNK_SIZE} dòng tiếp theo từ ID: {last_id}...")

        # 2. Gọi API với limit
        try:
            response = requests.get(API_URL, params={'last_id': last_id, 'limit': CHUNK_SIZE}, timeout=60)

            new_data = response.json()

            if not new_data or len(new_data) == 0:
                print("Đã đồng bộ xong toàn bộ dữ liệu!")
                break
            # 3. Ghi vào CSV
            df_new = pd.DataFrame(new_data)
            if 'id' in df_new.columns:
                df_new = df_new.drop(columns=['id'])
            df_new['progress'] = df_new['progress'].apply(handle_progress)
            df_new['label'] = df_new.apply(lambda row: 0 if (int(row['d1']) + int(row['d2']) + int(row['d3']) <= 10) else 1, axis=1) 

            print(df_new)
            break
            df_new.to_csv(CSV_FILE, mode='a', index=False, header=not file_exists)
            
            print(f"Đã lưu thêm {len(df_new)} dòng.")
            
            # Nghỉ 0.5s để server "thở"
            time.sleep(0.5) 

        except Exception as e:
            print(f"Lỗi: {e}")
            break

if __name__ == "__main__":
    sync_data()