import numpy as np

# =========================
# 1. Đánh giá 1 phiên (cumsum)
# =========================
def session_metrics(cumsum):
    y = np.array(cumsum, dtype=float)

    # Gain: lãi cuối kỳ
    gain = y[-1] - y[0]

    # Trend: độ dốc xu hướng
    if len(y) > 1:
        x = np.arange(len(y))
        trend = np.polyfit(x, y, 1)[0]
    else:
        trend = 0.0

    # Drawdown: sụt giảm lớn nhất
    peak = np.maximum.accumulate(y)
    drawdown = np.max(peak - y)

    # Stability: độ ổn định bước tăng
    diff = np.diff(y)
    std = np.std(diff) if len(diff) > 0 else 0.0
    stability = 1.0 / (std + 1e-6)

    return gain, trend, drawdown, stability


# =========================
# 2. Gộp nhiều phiên → 1 model
# =========================
def model_metrics(sessions):
    metrics = [session_metrics(s) for s in sessions]

    return {
        "gain": np.mean([m[0] for m in metrics]),
        "trend": np.mean([m[1] for m in metrics]),
        "drawdown": np.mean([m[2] for m in metrics]),
        "stability": np.mean([m[3] for m in metrics]),
    }


# =========================
# 3. Tính SCORE & xếp hạng
# =========================
def rank_models(models):
    stats = {name: model_metrics(sessions)
             for name, sessions in models.items()}

    keys = ["gain", "trend", "drawdown", "stability"]

    # Normalize theo toàn bộ model
    for k in keys:
        values = np.array([m[k] for m in stats.values()])
        min_v, max_v = values.min(), values.max()

        for m in stats.values():
            m[k + "_norm"] = (
                (m[k] - min_v) / (max_v - min_v + 1e-6)
            )

    # Final SCORE
    for m in stats.values():
        m["score"] = (
            0.4 * m["gain_norm"] +
            0.3 * m["trend_norm"] +
            0.2 * m["stability_norm"] -
            0.3 * m["drawdown_norm"]
        )

    # Sort giảm dần theo score
    ranking = sorted(
        stats.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )

    return ranking


# =========================
# 4. MAIN – chạy thử
# =========================
if __name__ == "__main__":
    models = {
        "Random Forest": [
            [0,1,2,3,2,1,2,3,2,1,2],
            [0,1,0,-1,-2,-1]
        ],
        "K-Nearest Neighbors": [
            [0,1,2,3,2,1,2,3,4,5,6],
            [0,1,0,-1,-2,-1]
        ]
    }

    ranking = rank_models(models)

    print("=== MODEL RANKING (DESC) ===")
    for i, (name, stat) in enumerate(ranking, 1):
        print(f"{i}. {name}")
        print(f"   SCORE     : {stat['score']:.4f}")
        print(f"   Gain      : {stat['gain']:.4f}")
        print(f"   Trend     : {stat['trend']:.4f}")
        print(f"   Drawdown  : {stat['drawdown']:.4f}")
        print(f"   Stability : {stat['stability']:.4f}")
        print()
