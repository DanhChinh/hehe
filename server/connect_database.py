import requests
import pandas as pd
import numpy as np


def fetch_data_from_api(url, params=None):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f'get:{url} ->done')
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}")

def get_all_data(api_url="https://cyan.io.vn/xg79/get_data_1.php"):
    all_data = []
    params = {'page': 1, 'limit': 2000}  # page = 1, limit = 100 rows per page
    while True:
        data = fetch_data_from_api(api_url, params)
        if not data:  # Nếu không còn dữ liệu
            break
        all_data.extend(data)
        params['page'] += 1  # Tiến sang trang tiếp theo
    return all_data


def get_data_from_api():
    data_rows = get_all_data()
    df = pd.DataFrame(data_rows)

    # Đảm bảo cột 'progress' là kiểu object, các cột còn lại là int64
    for col in df.columns:
        if col == 'progress':
            # Giữ kiểu 'progress' là object (chuỗi hoặc bất kỳ kiểu dữ liệu nào không phải là số)
            df[col] = df[col].astype('object')
        else:
            # Chuyển tất cả các cột còn lại thành int64
            df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')

    return df


def get_jsonmodels():
    return fetch_data_from_api("https://cyan.io.vn/xg79/models_api.php")


def saveModel(modelName, session):
    print(modelName, session)
    if isinstance(session, np.ndarray):
        session = session.tolist()
    requests.post(
        "http://cyan.io.vn/xg79/models_api.php",
        json={
            "model": modelName,
            "session": session
        }
    )
