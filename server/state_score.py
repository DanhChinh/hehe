import pandas as pd
import json

class StateScoreAnalyzer:
    def __init__(self, window_size: int, horizon_size: int):
        """
        window_size: Số lượng phần tử dùng để định nghĩa một trạng thái (State).
        horizon_size: Số lượng phần tử tiếp theo dùng để tính điểm dự báo (Score).
        """
        self.window_size = window_size
        self.horizon_size = horizon_size
        self.knowledge_base = pd.DataFrame()

    def format_state(self, data_segment):
        """
        Chuyển đổi một phân đoạn dữ liệu thành tuple để làm khóa tra cứu ổn định.
        """
        return tuple(data_segment)

    def fit(self, data_list):
        """
        Phân tích mảng dữ liệu và xây dựng bảng điểm số trung bình cho các trạng thái.
        """
        series = pd.Series(data_list)
        records = []

        # Chỉ chạy đến vị trí mà vẫn còn đủ phần tử cho cả window và horizon
        limit = len(series) - self.window_size - self.horizon_size + 1
        
        for i in range(limit):
            # Cắt lát dữ liệu cho trạng thái và tương lai
            state_data = series.iloc[i : i + self.window_size]
            future_data = series.iloc[i + self.window_size : i + self.window_size + self.horizon_size]
            
            state_key = self.format_state(state_data)
            score = future_data.sum()
            
            records.append({'state': state_key, 'score': score})

        # Tạo DataFrame và tính toán thống kê
        df = pd.DataFrame(records)
        self.knowledge_base = df.groupby('state')['score'].agg(['mean', 'count']).reset_index()
        self.knowledge_base.columns = ['state', 'avg_score', 'occurrence_count']

    def get_score_by_state(self, current_state):
        """
        Nhận vào một trạng thái hiện tại và trả về điểm số dự báo tương lai.
        """
        state_key = self.format_state(current_state)
        
        # Truy vấn kết quả từ knowledge_base
        match = self.knowledge_base[self.knowledge_base['state'] == state_key]
        
        if not match.empty:
            return {
                "state": list(state_key),
                "avg_future_score": float(match['avg_score'].iloc[0]),
                "confidence_count": int(match['occurrence_count'].iloc[0])
            }
        
        #tra ve cac gia tri mac dinh neu khong tim thay
        return {
            "state": list(state_key),
            "avg_future_score": 0.0,
            "confidence_count": 0
        }
        
        # return {"error": "Trạng thái này chưa từng xuất hiện trong dữ liệu huấn luyện."}

    def export_to_json(self):
        """Xuất toàn bộ dữ liệu phân tích ra định dạng JSON."""
        output = []
        for _, row in self.knowledge_base.iterrows():
            output.append({
                "state": list(row['state']),
                "avg_future_score": round(row['avg_score'], 4),
                "occurrences": int(row['occurrence_count'])
            })
        return json.dumps(output, ensure_ascii=False, indent=4)


# raw_data = [1, 1, -1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1, 1, -1]
# analyzer = StateScoreAnalyzer(window_size=3, horizon_size=1)
# analyzer.fit(raw_data)

# # 1. Tra cứu thử một trạng thái
# current_observation = [1, 1, -1]
# prediction = analyzer.get_score_by_state(current_observation)
# print(f"Dự báo cho trạng thái {current_observation}:")
# print(prediction)
