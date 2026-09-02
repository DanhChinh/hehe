// ==========================================
// 1. BIẾN TOÀN CỤC & QUẢN LÝ DANH SÁCH BIỂU ĐỒ
// ==========================================
let chartInstances = []; // Lưu danh sách các cặp biểu đồ đã tạo

// Hàm hỗ trợ tạo cấu trúc HTML chứa 2 biểu đồ và form điều khiển cho mỗi phần tử trong mảng
function ensureChartContainers(count) {
    const wrapper = document.querySelector('.charts-wrapper');
    if (!wrapper) return;

    // Lấy hiện tại có bao nhiêu cặp, nếu thiếu thì sinh thêm HTML
    const currentCards = wrapper.querySelectorAll('.chart-pair-group');
    
    if (currentCards.length < count) {
        for (let i = currentCards.length; i < count; i++) {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'chart-pair-group mb-4';

            groupDiv.innerHTML = `
<h3 class="text-dark mb-0">Phần tử dữ liệu #${i + 1}</h3>
<div id="chartsWrapper_${i}" class="row g-4 align-items-stretch">
    <div class="col-md-6">
        <div class="card h-100 p-3 shadow-sm">
            <h2 class="chart-title" style="font-size: 14px;">Cumulative Line Chart</h2>
            <div class="chart-container position-relative" style="height: 250px;">
                <canvas id="gameChart_${i}"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100 p-3 shadow-sm">
            <h2 class="chart-title" style="font-size: 14px;">Volatility Chart</h2>
            <div class="chart-container position-relative" style="height: 250px;">
                <canvas id="rawScoreChart_${i}"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-2">
        <div class="card h-100 p-2 shadow-sm d-flex flex-column justify-content-between" style="font-size: 13px;">
            <div>
                <h2 class="chart-title mb-2" style="font-size: 14px;">Settings</h2>
                
                <!-- Inputs: tp, sl, volume -->
                <div class="mb-2">
                    <label class="form-label mb-0" style="font-size: 12px;">TP:</label>
                    <input type="number" class="form-control form-control-sm" onchange="set_property(${i}, 'tp', +this.value)">
                </div>
                <div class="mb-2">
                    <label class="form-label mb-0" style="font-size: 12px;">SL:</label>
                    <input type="number" class="form-control form-control-sm" onchange="set_property(${i}, 'sl', +this.value)">
                </div>
                <div class="mb-2">
                    <label class="form-label mb-0" style="font-size: 12px;">Volume:</label>
                    <input type="number" class="form-control form-control-sm" onchange="set_property(${i}, 'volume', +this.value)">
                </div>

                <!-- Invest Text -->
                <div class="mb-2">
                    <label class="form-label mb-0" style="font-size: 12px;">Invest:</label>
                    <input type="text" class="form-control form-control-sm" onchange="set_property(${i}, 'invest', +this.value)">
                </div>
            </div>

            <!-- Checkboxes / Toggle Buttons: isPlay, isReverse, isShow -->
            <div class="mt-2 pt-2 border-top">
                <div class="form-check form-switch mb-1">
                    <input class="form-check-input" type="checkbox" role="switch" id="isPlay_${i}" onchange="set_property(${i}, 'isPlay', this.checked)">
                    <label class="form-check-label" for="isPlay_${i}" style="font-size: 12px;">Play</label>
                </div>
                <div class="form-check form-switch mb-1">
                    <input class="form-check-input" type="checkbox" role="switch" id="isReverse_${i}" onchange="set_property(${i}, 'isReverse', this.checked)">
                    <label class="form-check-label" for="isReverse_${i}" style="font-size: 12px;">Reverse</label>
                </div>
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" role="switch" id="isShow_${i}" onchange="set_property(${i}, 'isShow', this.checked)">
                    <label class="form-check-label" for="isShow_${i}" style="font-size: 12px;">Show</label>
                </div>
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

    // Đảm bảo giao diện HTML có đủ số lượng canvas và form tương ứng với kích thước mảng
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

        // --- ĐỔ DỮ LIỆU VÀO CÁC FORM CONTROLS ---
        const groupDiv = document.querySelectorAll('.chart-pair-group')[index];
        if (groupDiv) {
            const inputs = groupDiv.querySelectorAll('input');
            // Thứ tự các input trong col-md-2: 
            // 0: tp, 1: sl, 2: volume, 3: invest, 4: isPlay (checkbox), 5: isReverse (checkbox), 6: isShow (checkbox)
            if (inputs.length >= 7) {
                // Kiểm tra activeElement để tránh ghi đè khi người dùng đang nhập liệu dở
                if (document.activeElement !== inputs[0]) inputs[0].value = item.tp ?? '';
                if (document.activeElement !== inputs[1]) inputs[1].value = item.sl ?? '';
                if (document.activeElement !== inputs[2]) inputs[2].value = item.volume ?? '';
                if (document.activeElement !== inputs[3]) inputs[3].value = item.invest ?? '';
                
                inputs[4].checked = !!item.isPlay;
                inputs[5].checked = !!item.isReverse;
                inputs[6].checked = !!item.isShow;
            }
        }

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

// ==========================================
// 3. GỬI SỰ KIỆN LÊN SERVER QUA SOCKET.IO
// ==========================================
function set_property(idx, prop, val) {
    console.log(idx, prop, val)
    system.socket_io.emit("set_property", { idx, prop, val });
}