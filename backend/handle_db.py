import requests, os, json, time, math
import pandas as pd


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
    sublist = progress_arr[30:34]
    sublist = progress_arr[10:34]
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
    return [bc2, bc1, v2, v1]


def update_local_db():
    API_URL = "http://cyan.io.vn/xg79/sync_api.php"
    PKL_FILE = "data_local.pkl"  # Đổi đuôi file
    ID_COL = "sid"
    CHUNK_SIZE = 5000  

    # 1. Lấy dữ liệu cũ nếu có
    if os.path.isfile(PKL_FILE):
        df_local = pd.read_pickle(PKL_FILE)
        last_id = int(df_local[ID_COL].max()) if not df_local.empty else 0
    else:
        df_local = pd.DataFrame()
        last_id = 0

    while True:
        print(f"Đang tải {CHUNK_SIZE} dòng tiếp theo từ ID: {last_id}...")

        try:
            response = requests.get(API_URL, params={'last_id': last_id, 'limit': CHUNK_SIZE}, timeout=60)
            new_data = response.json()

            if not new_data or len(new_data) == 0:
                print("Đã đồng bộ xong toàn bộ dữ liệu!")
                break

            # 2. Xử lý dữ liệu mới
            df_new = pd.DataFrame(new_data)
            if 'id' in df_new.columns:
                df_new = df_new.drop(columns=['id'])
            
            # Lưu ý: handle_progress lúc này nên trả về LIST thực thụ, không cần json.dumps
            #
            df_new['progress'] = df_new['progress'].apply(handle_progress)
            df_new = df_new.dropna(subset=['progress'])
            df_new = df_new[df_new['progress'].map(len) == 4]
            if df_new.empty:
                print("Dữ liệu chunk này không có dòng nào hợp lệ (None hoặc length != 96).")
                # Cập nhật last_id để không bị lặp vô hạn nếu toàn bộ chunk lỗi
                last_id = int(pd.DataFrame(new_data)[ID_COL].max())
                continue
            
            # Tính toán Label
            df_new['label'] = df_new.apply(
                lambda row: 2 if (int(row['d1']) + int(row['d2']) + int(row['d3']) <= 10) else 1, 
                axis=1
            ).astype(int)

            # 3. Gộp và Lưu
            df_local = pd.concat([df_local, df_new], ignore_index=True)
            df_local.to_pickle(PKL_FILE)
            
            # Cập nhật last_id cho vòng lặp sau
            last_id = int(df_new[ID_COL].max())
            
            print(f"Đã lưu thêm {len(df_new)} dòng. Tổng cộng: {len(df_local)}")
            
            time.sleep(0.5) 

        except Exception as e:
            print(f"Lỗi: {e}")
            break

def load_db_as_df(filename="data_local.pkl"):
    if os.path.isfile(filename):
        # Pickle giữ nguyên định dạng List cho cột 'progress'
        # Bạn có thể dùng ngay mà không cần convert gì thêm
        df = pd.read_pickle(filename)
        return df
    else:
        print(f"File {filename} không tồn tại.")
        return None


def get_last_n(n=1500):
    # Đường dẫn tới file PHP mới (hoặc file cũ đã sửa)
    url = "https://cyan.io.vn/xg79/get_last_n.php"
    
    # Truyền tham số n vào dictionary params
    params = {'n': n}

    try:
        # Gửi request kèm theo params (?n=...)
        response = requests.get(url, params=params, timeout=5)

        # Kiểm tra lỗi HTTP (404, 500, v.v.)
        response.raise_for_status()

        # Chuyển đổi JSON thành Python list
        data = response.json()

        return data

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy {n} dòng dữ liệu:", e)
        return []