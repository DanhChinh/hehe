import numpy as np


# =========================
# STATE (TRAIN + RUNTIME dùng chung)
# =========================
def extract_state(compare, current_index=None, window_size=20, block_size=5):
    if current_index is None:
        current_index = len(compare)

    past = compare[current_index - window_size:current_index]

    state_blocks = []
    for i in range(0, window_size, block_size):
        block = past[i:i + block_size]
        state_blocks.append(int(np.sum(block)))

    return str(tuple(state_blocks))

def calculate_reward(compare, current_index, future_size=10):
    future = compare[current_index:current_index + future_size]
    return int(np.sum(future))