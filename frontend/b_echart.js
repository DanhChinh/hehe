// --- 1. BIẾN TOÀN CỤC CỦA 2 BIỂU ĐỒ ---
let gameChart = null;       // Biểu đồ Cumsum (Đoạn mã của bạn)
let rawScoreChart = null;   // Biểu đồ điểm từng ván (Đoạn mã mới)

// --- CÁC HÀM HỖ TRỢ TOÁN HỌC ---
function getLabels(arr) {
    return arr.map((_, index) => index + 1);
}

function getSigmaThresholds(cumulativeArr) {
    let upper2Sigma = [];
    let lower2Sigma = [];

    cumulativeArr.forEach((_, index) => {
        let n = index + 1;
        let sigma = Math.sqrt(n);
        upper2Sigma.push(+(2 * sigma).toFixed(2));
        lower2Sigma.push(-(2 * sigma).toFixed(2));
    });

    return { upper2Sigma, lower2Sigma };
}



// ==========================================
// 2. BIỂU ĐỒ 1: TỔNG CỘNG DỒN & 2-SIGMA (CỦA BẠN)
// ==========================================
function initChart() {
    const ctx = document.getElementById('gameChart').getContext('2d');

    gameChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Điểm cộng dồn (Cumsum)',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.1
                },
                {
                    label: 'Ngưỡng trên (+2σ)',
                    data: [],
                    borderColor: 'rgba(34, 197, 94, 0.8)',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: 'Ngưỡng dưới (-2σ)',
                    data: [],
                    borderColor: 'rgba(239, 68, 68, 0.8)',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMin: -8,
                    suggestedMax: 8,
                    grid: { color: 'rgba(200, 200, 200, 0.2)' }
                },
                x: { grid: { display: false } }
            }
        }
    });
}

function updateChart(cumulativeData) {
    if (!gameChart) return;

    const thresholds = getSigmaThresholds(cumulativeData);

    gameChart.data.labels = getLabels(cumulativeData);
    gameChart.data.datasets[0].data = cumulativeData;
    gameChart.data.datasets[1].data = thresholds.upper2Sigma;
    gameChart.data.datasets[2].data = thresholds.lower2Sigma;

    gameChart.update();
}

// ==========================================
// 3. BIỂU ĐỒ 2: ĐIỂM TỪNG VÁN (VIẾT MỚI HỖ TRỢ)
// ==========================================
function initRawScoreChart() {
    const ctx = document.getElementById('rawScoreChart').getContext('2d');

    rawScoreChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Điểm ván này',
                data: [],
                borderColor: 'rgb(168, 85, 247)',
                backgroundColor: 'rgba(168, 85, 247, 0.15)',
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: 'rgb(168, 85, 247)',
                tension: 0.2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    grid: { color: 'rgba(200, 200, 200, 0.2)' }
                },
                x: { grid: { display: false } }
            }
        }
    });
}

function updateRawScoreChart(rawScores) {
    if (!rawScoreChart) return;

    rawScoreChart.data.labels = getLabels(rawScores);
    rawScoreChart.data.datasets[0].data = rawScores;

    rawScoreChart.update();
}

// ==========================================
// 4. KHỞI TẠO VÀ VẼ DỮ LIỆU
// ==========================================
window.addEventListener('DOMContentLoaded', () => {
    // Khởi tạo cả 2 biểu đồ
    initChart();
    initRawScoreChart();
});