from flask import Flask, request, jsonify
import numpy as np
from flask_cors import CORS 
import random
app = Flask(__name__)
CORS(app) # Cho phép truy cập từ frontend

# Dữ liệu long CỐ ĐỊNH (np.float64)
LONG_ARRAY = [random.choice([-1, 1]) for i in range(100)]
LONG_ARRAY = np.cumsum(LONG_ARRAY)

def find_best_match_ncc(short_array, long_array):
    """
    Tính Tương quan chéo Chuẩn hóa (NCC) và trả về dữ liệu cần thiết cho ECharts.
    Đã sửa lỗi JSON serialization bằng cách dùng .item(), int(), float().
    """
    S = np.array(short_array, dtype=float)
    L = np.array(long_array, dtype=float)
    N = len(S)
    
    # 1. Tính toán NCC
    S_mean = np.mean(S); S_std = np.std(S)
    ncc_scores = []
    
    for i in range(len(L) - N + 1):
        window = L[i:i + N]
        L_mean = np.mean(window); L_std = np.std(window)
        if S_std == 0 or L_std == 0: 
            ncc = 0.0
        else:
            numerator = np.sum((window - L_mean) * (S - S_mean))
            denominator = (N * L_std * S_std)
            ncc = numerator / denominator
        ncc_scores.append(ncc)
        
    ncc_scores = np.array(ncc_scores)
    best_match_index = np.argmax(ncc_scores)
    max_ncc_score = ncc_scores[best_match_index]
    
    # 2. Chuẩn bị dữ liệu cho biểu đồ ECharts
    best_match_window = L[best_match_index : best_match_index + N]
    
    # Chuẩn hóa để so sánh hình dạng (trừ trung bình)
    S_centered = S - np.mean(S)
    W_centered = best_match_window - np.mean(best_match_window)
    
    start_index_int = int(best_match_index)
    end_index_int = int(best_match_index + N - 1)
    
    # Dữ liệu cho biểu đồ 1: Segment cần float() cho giá trị và int() cho chỉ mục
    match_segment = [
        {'coord': [start_index_int, float(LONG_ARRAY[start_index_int])]}, 
        {'coord': [end_index_int, float(LONG_ARRAY[end_index_int])]}
    ]
                     
    return {
        # Sửa lỗi JSON: Chuyển các giá trị số NumPy đơn lẻ sang kiểu Python gốc
        "best_index": start_index_int,       
        "max_score": float(max_ncc_score),    
        
        # .tolist() tự động xử lý kiểu NumPy trong mảng
        "long_array": LONG_ARRAY.tolist(),
        "match_segment": match_segment,
        "S_centered": S_centered.tolist(),
        "W_centered": W_centered.tolist(),
        "n_points": int(N)                    
    }

@app.route('/api/match', methods=['POST'])
def match_template():
    data = request.json
    short_array = data.get('short_array')
    
    if not short_array:
        return jsonify({"error": "Missing short_array"}), 400
    
    results = find_best_match_ncc(short_array, LONG_ARRAY)
    return jsonify(results)

if __name__ == '__main__':
    # Chạy server tại cổng 5000
    print("Running Flask server on http://127.0.0.1:5000")
    # Tắt debug=True khi deploy chính thức
    app.run(debug=True, port=5000)