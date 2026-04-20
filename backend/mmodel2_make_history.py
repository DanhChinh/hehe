import matplotlib.pyplot as plt

from mmodel2 import *
import json
from handle_db import update_local_db, load_db_as_df, handle_progress, get_last_n



def run_mmodel2(): 
    # real_data = get_last_n(1000)
    # for rt in real_data:
    #     x_pred = handle_progress(rt['progress'], isEnd=False)
    #     result = 1 if int(rt['d1']) + int(rt['d2']) + int(rt['d3']) > 10 else 2
    #     PREDICT(x_pred)
    #     CHECK(result)


    df = load_db_as_df().tail(n=800)
    df['sid'] = df['sid'].astype(int)  # Đảm bảo cột sid là kiểu int để so sánh chính xác
    sids = df['sid'].tolist()



    for i in range(sids[0], sids[-1], 1):
        if i not in sids:
            # print(f"⚠️ Missing SID: {i}")
            CHECK(0)  # Ghi nhận là dự đoán sai nếu SID này không có trong dữ liệu

        else:
            # print(f"✅ SID {i} is present.")
            #tim hang co sid = i
            row = df[df['sid'] == i].iloc[0]
            PREDICT(row['progress'])
            CHECK(row['label'])
            

    #ve bie do cong don cac bot
    for model in models:
        info = model.get_info()
        plt.plot(info['history_cumsum'], label=info['name'])
    plt.title("Cumulative Score of Bots")
    plt.xlabel("Number of Predictions")
    plt.ylabel("Cumulative Score")
    plt.legend()
    plt.show()


run_mmodel2()