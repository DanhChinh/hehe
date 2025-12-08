import numpy as np
import matplotlib.pyplot as plt

# Hàm tìm kiếm NCC được giả định đã có và hoạt động.
# Để hàm này hoạt động độc lập, tôi sẽ thêm tham số ncc_scores vào hàm plot.

def plot_best_match_single_frame(short_array, long_array, best_index, ncc_scores):
    """
    Vẽ hai biểu đồ (subplot) trong cùng một khung hình (figure) để so sánh.
    
    Args:
        short_array (np.array): Mảng mẫu.
        long_array (np.array): Mảng dữ liệu lớn.
        best_index (int): Vị trí bắt đầu khớp tốt nhất.
        ncc_scores (np.array): Mảng điểm NCC (cần để hiển thị điểm tối đa).
    """
    S = np.array(short_array, dtype=float)
    L = np.array(long_array, dtype=float)
    N = len(S)
    
    best_match_window = L[best_index : best_index + N]
    max_ncc_score = np.max(ncc_scores) if len(ncc_scores) > 0 else 0.0
    
    # ----------------------------------------------------
    # Sử dụng plt.subplots(rows, cols, ...) để tạo khung hình chung
    # ----------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle(f'So sánh Khớp Mẫu (Template Matching) | Max NCC Score: {max_ncc_score:.4f}', fontsize=16)

    # --- SUBPLOT 1: Mảng Long và Đoạn Khớp (Bao gồm độ lớn) ---
    
    # Vẽ toàn bộ mảng Long
    ax1.plot(L, label='Mảng Long (Dữ liệu)', color='gray', linewidth=1.5, marker='.')
    
    # Vẽ đoạn khớp tốt nhất
    ax1.plot(range(best_index, best_index + N), best_match_window, 
             label=f'Đoạn Khớp Tốt nhất (Index {best_index})', 
             color='red', linewidth=3)
    
    ax1.set_title('1. Dữ liệu Long và Đoạn Khớp Tốt nhất (Bao gồm Độ lớn)')
    ax1.set_xlabel('Chỉ số')
    ax1.set_ylabel('Giá trị')
    ax1.legend()
    ax1.grid(True)

    # --- SUBPLOT 2: So sánh Hình dạng (Đã trừ Trung bình) ---
    
    # Chuẩn hóa Mẫu Short (trừ trung bình)
    S_centered = S - np.mean(S)
    
    # Chuẩn hóa Cửa sổ Khớp (trừ trung bình)
    W_centered = best_match_window - np.mean(best_match_window)
    
    # Vẽ Mẫu Short (Chỉ hình dạng, đã dịch về 0)
    ax2.plot(S_centered, label='Hình dạng Mẫu Short (trừ trung bình)', color='orange', linestyle='--', linewidth=2)
    
    # Vẽ Cửa sổ Khớp (Chỉ hình dạng, đã dịch về 0)
    ax2.plot(W_centered, label='Hình dạng Cửa sổ Khớp (trừ trung bình)', color='blue', linewidth=2, marker='o', markersize=4)
    
    ax2.set_title(f'2. So sánh Hình dạng (Shape) tại Vị trí Khớp')
    ax2.set_xlabel(f'Vị trí Tương đối trong Cửa sổ (Bắt đầu từ Index {best_index})')
    ax2.set_ylabel('Giá trị (Đã trừ Trung bình)')
    ax2.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax2.legend()
    ax2.grid(True)
    
    # Tự động điều chỉnh khoảng cách giữa các subplot
    plt.tight_layout(rect=[0, 0, 1, 0.96]) 
    plt.show()

# --- SỬ DỤNG VÍ DỤ ---
# Hàm find_best_match_ncc (đã được định nghĩa trong các câu trả lời trước)
def find_best_match_ncc(short_array, long_array):
    S = np.array(short_array, dtype=float)
    L = np.array(long_array, dtype=float)
    N = len(S)
    S_mean = np.mean(S); S_std = np.std(S)
    ncc_scores = []
    for i in range(len(L) - N + 1):
        window = L[i:i + N]
        L_mean = np.mean(window); L_std = np.std(window)
        if S_std == 0 or L_std == 0: ncc = 0.0
        else:
            numerator = np.sum((window - L_mean) * (S - S_mean))
            denominator = (N * L_std * S_std)
            ncc = numerator / denominator
        ncc_scores.append(ncc)
    ncc_scores = np.array(ncc_scores)
    best_match_index = np.argmax(ncc_scores)
    max_ncc_score = ncc_scores[best_match_index]
    return best_match_index, max_ncc_score, ncc_scores


import random 
long_array = [random.choice([-1, 1]) for i in range(100)]
short_array = [random.choice([-1, 1]) for i in range(10)] 

long_array = np.cumsum(long_array)
short_array = np.cumsum(short_array)

# 1. Tính toán NCC
best_index, max_score, ncc_scores = find_best_match_ncc(short_array, long_array)

# 2. Vẽ biểu đồ (chỉ 1 frame)
plot_best_match_single_frame(short_array, long_array, best_index, ncc_scores)

