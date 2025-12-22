import json, math
import numpy as np
import pandas as pd
from connect_database import get_data_from_api
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
    if isEnd and len(progress_arr) != 49:
        return None
    sublist = progress_arr[30:34]
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

def make_data():
    df = get_data_from_api()

    if df is not None:
        print("Dữ liệu lấy thành công:")
    else:
        print("Lỗi khi lấy dữ liệu.")
    data_perfect = []
    label_perfect = []
    for index, row in df.iterrows():
        formater = handle_progress(row['progress'])
        if formater:
            data_perfect.append(formater)
            rs18 = row['d1']+row['d2']+row['d3']
            label_perfect.append(1 if rs18>10 else 0)


    data = np.array(data_perfect)
    label = np.array(label_perfect)
    return data, label
