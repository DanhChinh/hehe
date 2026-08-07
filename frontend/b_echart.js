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
                    label: 'Cumsum',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.08)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: 'rgb(59, 130, 246)'
                },
                {
                    label: '+2σ',
                    data: [],
                    borderColor: 'rgba(34, 197, 94, 0.8)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false,
                    tension: 0
                },
                {
                    label: '-2σ',
                    data: [],
                    borderColor: 'rgba(239, 68, 68, 0.8)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false,
                    tension: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 8,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.9)',
                    titleFont: { size: 13, weight: 'bold' },
                    bodyFont: { size: 12 },
                    padding: 10,
                    cornerRadius: 6
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMin: -8,
                    suggestedMax: 8,
                    grid: { 
                        color: (context) => {
                            return context.tick.value === 0 ? 'rgba(156, 163, 175, 0.6)' : 'rgba(200, 200, 200, 0.15)';
                        },
                        lineWidth: (context) => context.tick.value === 0 ? 2 : 1
                    },
                    ticks: {
                        callback: function(value) {
                            return value > 0 ? '+' + value : value;
                        }
                    }
                },
                x: { 
                    grid: { display: false },
                    ticks: {
                        maxTicksLimit: 15,
                        autoSkip: true
                    }
                }
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
                label: 'mm',
                data: [],
                borderColor: 'rgb(168, 85, 247)',
                borderWidth: 3,
                tension: 0.3,
                fill: true,
                backgroundColor: function(context) {
                    const chart = context.chart;
                    const {ctx, chartArea} = chart;
                    if (!chartArea) return null;
                    
                    const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                    gradient.addColorStop(0, 'rgba(168, 85, 247, 0.4)');
                    gradient.addColorStop(1, 'rgba(168, 85, 247, 0.01)');
                    return gradient;
                },
                pointRadius: 3,
                pointBackgroundColor: 'rgb(168, 85, 247)',
                pointBorderColor: '#fff',
                pointBorderWidth: 1.5,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(168, 85, 247)',
                pointHoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'nearest',
                intersect: false,
                axis: 'x'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 6,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                    titleFont: { size: 13, weight: 'bold' },
                    bodyFont: { size: 12 },
                    padding: 10,
                    cornerRadius: 6,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) {
                                label += context.parsed.y + ' mm';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    grid: { 
                        color: 'rgba(200, 200, 200, 0.15)',
                        drawBorder: false
                    },
                    ticks: {
                        font: { size: 11 },
                        padding: 8,
                        callback: function(value) {
                            return value + ' mm';
                        }
                    }
                },
                x: { 
                    grid: { display: false },
                    ticks: {
                        font: { size: 11 },
                        padding: 8,
                        maxTicksLimit: 12,
                        autoSkip: true
                    }
                }
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