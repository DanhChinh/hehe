import matplotlib.pyplot as plt
from mmodel2 import *
from handle_data import handle_progress
from connect_database import get_last_n
import json


def run_mmodel2():
    real_time = get_last_n()  # Lấy 1000 dòng dữ liệu mới nhất

    for rt in real_time:

        x_pred = handle_progress(rt['progress'], isEnd=False)
        result = 1 if int(rt['d1']) + int(rt['d2']) + int(rt['d3']) > 10 else 2

        PREDICT(x_pred)
        CHECK(result)


    #ve biểu đồ lịch sử của bot
    for model in models:
        info = model.get_info()
        plt.plot(info['history_cumsum'], label=model.name)
    plt.title("Lịch sử tích lũy của các bot")
    plt.xlabel("Phiên giao dịch")
    plt.ylabel("Lợi nhuận tích lũy")
    plt.legend()
    plt.show()

    #luu lai history cua bot
    for model in models:
        with open(f"history/{model.name}.json", "w") as f:
            json.dump(model.history, f)

run_mmodel2()