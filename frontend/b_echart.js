// ==========================================
// 1. BIẾN TOÀN CỤC & QUẢN LÝ DANH SÁCH BIỂU ĐỒ
// ==========================================
let chartInstances = []; // Lưu danh sách các cặp biểu đồ đã tạo

// Hàm hỗ trợ tạo cấu trúc HTML chứa 2 biểu đồ cho mỗi phần tử trong mảng
function ensureChartContainers(count) {
    const wrapper = document.querySelector('.charts-wrapper');
    if (!wrapper) return;

    // Lấy hiện tại có bao nhiêu cặp, nếu thiếu thì sinh thêm HTML
    const currentCards = wrapper.querySelectorAll('.chart-pair-group');
    
    if (currentCards.length < count) {
        for (let i = currentCards.length; i < count; i++) {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'chart-pair-group';
            groupDiv.style.marginBottom = '40px';
            groupDiv.style.borderBottom = '1px solid rgba(200, 200, 200, 0.2)';
            groupDiv.style.paddingBottom = '20px';

            groupDiv.innerHTML = `
<div class="d-flex justify-content-between align-items-center mb-3">
    <h3 class="text-dark mb-0">Phần tử dữ liệu #${i + 1}</h3>
    <button type="button" class="btn btn-sm btn-outline-danger px-2 py-0 fw-bold" onclick="toggleCharts(${i})">&times;</button>
</div>

<div id="chartsWrapper_${i}" class="row g-4">
    <div class="col-md-6">
        <div class="card h-100 p-3 shadow-sm">
            <h2 class="chart-title" style="font-size: 14px;">Cumulative Line Chart</h2>
            <div class="chart-container position-relative" style="height: 250px;">
                <canvas id="gameChart_${i}"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card h-100 p-3 shadow-sm">
            <h2 class="chart-title" style="font-size: 14px;">Volatility Chart</h2>
            <div class="chart-container position-relative" style="height: 250px;">
                <canvas id="rawScoreChart_${i}"></canvas>
            </div>
        </div>
    </div>
</div>


            `;
            wrapper.appendChild(groupDiv);
        }
    }
}

// ==========================================
// 2. HÀM KHỞI TẠO HOẶC CẬP NHẬT THEO MẢNG DỮ LIỆU
// ==========================================
function renderMultipleCharts(dataArray) {
    if (!Array.isArray(dataArray) || dataArray.length === 0) return;

    // Đảm bảo giao diện HTML có đủ số lượng canvas tương ứng với kích thước mảng
    ensureChartContainers(dataArray.length);

    // Duyệt qua từng phần tử trong mảng dữ liệu trả về từ server
    dataArray.forEach((item, index) => {
        const historyTm = item.history_tm || [];
        const historyMm = item.history_mm || [];
        
        const labels = historyTm.map((_, i) => i + 1);
        
        // Tính toán 2-sigma cho biểu đồ cumulative (history_tm)
        let upper2Sigma = [];
        let lower2Sigma = [];
        historyTm.forEach((_, i) => {
            let n = i + 1;
            let sigma = Math.sqrt(n);
            upper2Sigma.push(+(2 * sigma).toFixed(2));
            lower2Sigma.push(-(2 * sigma).toFixed(2));
        });

        // Kiểm tra xem cặp biểu đồ thứ `index` đã được khởi tạo instance chưa
        if (!chartInstances[index]) {
            // --- KHỞI TẠO MỚI CHO CẶP THỨ INDEX ---
            const ctx1 = document.getElementById(`gameChart_${index}`).getContext('2d');
            const ctx2 = document.getElementById(`rawScoreChart_${index}`).getContext('2d');

            const tmChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Cumsum', data: historyTm, borderColor: 'rgb(59, 130, 246)', borderWidth: 2, fill: true, backgroundColor: 'rgba(59, 130, 246, 0.08)', tension: 0.3 },
                        { label: '+2σ', data: upper2Sigma, borderColor: 'rgba(34, 197, 94, 0.8)', borderWidth: 1.5, pointRadius: 0, fill: false },
                        { label: '-2σ', data: lower2Sigma, borderColor: 'rgba(239, 68, 68, 0.8)', borderWidth: 1.5, pointRadius: 0, fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });

            const mmChart = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'mm',
                        data: historyMm,
                        borderColor: 'rgb(168, 85, 247)',
                        borderWidth: 2,
                        fill: true,
                        backgroundColor: 'rgba(168, 85, 247, 0.1)',
                        tension: 0.3
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });

            // Lưu instance lại để lần sau chỉ update thay vì tạo mới
            chartInstances[index] = { tmChart, mmChart };

        } else {
            // --- CẬP NHẬT DỮ LIỆU CHO CẶP ĐÃ TỒN TẠI ---
            const { tmChart, mmChart } = chartInstances[index];

            // Cập nhật Biểu đồ TM
            tmChart.data.labels = labels;
            tmChart.data.datasets[0].data = historyTm;
            tmChart.data.datasets[1].data = upper2Sigma;
            tmChart.data.datasets[2].data = lower2Sigma;
            tmChart.update();

            // Cập nhật Biểu đồ MM
            mmChart.data.labels = labels;
            mmChart.data.datasets[0].data = historyMm;
            mmChart.update();
        }
    });
}


function toggleCharts(index) {
        const wrapper = document.getElementById(`chartsWrapper_${index}`);
        if (wrapper.style.display === 'none') {
            wrapper.style.display = 'flex'; // Hoặc '' nếu dùng row mặc định của Bootstrap
        } else {
            wrapper.style.display = 'none';
        }
    }