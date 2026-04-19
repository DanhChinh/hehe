import numpy as np
import pandas as pd

def save_to_csv(data, label, filename="dataset.csv"):
    data = np.array(data)
    label = np.array(label).reshape(-1, 1)  # đảm bảo là cột

    # ghép data + label
    combined = np.hstack((data, label))

    # tạo tên cột
    columns = [f"f{i}" for i in range(data.shape[1])] + ["label"]

    df = pd.DataFrame(combined, columns=columns)
    df.to_csv(filename, index=False)
def load_from_csv(filename="dataset.csv"):
    df = pd.read_csv(filename)

    data = df.iloc[:, :-1].values   # tất cả cột trừ label
    label = df.iloc[:, -1].values   # cột label

    return data, label

