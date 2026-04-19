import json, math
import numpy as np
import pandas as pd
import os
from handle_csv import load_from_csv, save_to_csv
from connect_database import get_data_from_api

def handle_progress(progress, isEnd = True):
    progress_arr = json.loads(progress)
    if isEnd and len(progress_arr) < 49 and len(progress_arr) > 63:
        return None
    sublist = progress_arr[10:34]
    data = []
    bc2 = []
    v2 = []
    bc1 = []
    v1 =  []
    for pair in sublist:
        bc2.append(pair[0]['bc'])
        bc1.append(pair[1]['bc'])
        v2.append(pair[0]['v'])
        v1.append(pair[1]['v'])
    return [bc2, bc1, v2, v1]

def make_data():
    if os.path.exists('dataset.csv'):
        return load_from_csv()
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
            label_perfect.append(1 if rs18>10 else 2)


    data = np.array(data_perfect)
    label = np.array(label_perfect)

    print("Dữ liệu đã được xử lý thành công.")
    print("Kich thước dữ liệu:", data.shape)
    save_to_csv(data, label)
    return data, label

