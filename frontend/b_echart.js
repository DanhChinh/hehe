// ==========================================
// 1. BIẾN TOÀN CỤC & HÀM HỖ TRỢ GIAO DIỆN
// ==========================================
let chartInstances = []; // Lưu danh sách các cặp biểu đồ đã tạo

/**
 * Hàm cập nhật màu viền Card khi trạng thái isPlay thay đổi
 * @param {number} index - Chỉ số phần tử
 * @param {boolean} isPlay - Trạng thái Play
 */
function updateCardPlayStyle(index, isPlay) {
    const cardElement = document.getElementById(`cardMain_${index}`);
    if (cardElement) {
        if (isPlay) {
            // Bật viền xanh lá đậm + viền 2px + hiệu ứng shadow
            cardElement.classList.add('border', 'border-2', 'border-success', 'shadow');
        } else {
            // Trở về mặc định
            cardElement.classList.remove('border', 'border-2', 'border-success', 'shadow');
        }
    }
}

/**
 * Hàm tạo cấu trúc HTML cho danh sách các phần tử
 * @param {number} count - Số lượng phần tử cần hiển thị
 */
function ensureChartContainers(count) {
    const wrapper = document.querySelector('.charts-wrapper');
    if (!wrapper) return;

    const currentCards = wrapper.querySelectorAll('.chart-pair-group');
    
    if (currentCards.length < count) {
        for (let i = currentCards.length; i < count; i++) {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'chart-pair-group col-12 col-lg-4 mb-3';
            groupDiv.innerHTML = `
                <!-- Thanh tiêu đề & Nút Toggle -->
                <div class="d-flex align-items-center justify-content-between mb-2">
                    <h3 class="text-dark mb-0 fs-6 fw-bold">Phần tử #${i + 1}</h3>
                    <button class="btn btn-sm btn-outline-primary py-0 px-2" type="button" onclick="toggleItemView(${i})" style="font-size: 11px;">
                        <i class="fa-solid fa-right-left me-1"></i> Biểu đồ / Cài đặt
                    </button>
                </div>

                <div id="chartsWrapper_${i}" class="row g-2 align-items-stretch">
                    <!-- Khối 1: Cumulative Line Chart -->
                    <div class="col-12" id="block1_${i}">
                        <!-- ID cardMain_${i} phục vụ việc tô màu viền xanh -->
                        <div id="cardMain_${i}" class="card h-100 p-2 shadow-sm transition-all">
                            <h2 class="chart-title mb-1" style="font-size: 13px;">Cumulative Line Chart</h2>
                            <div class="chart-container position-relative" style="height: 220px;">
                                <canvas id="gameChart_${i}"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Cụm Khối 2 & 3: Volatility Chart & Settings -->
                    <div class="col-12 d-none" id="block2and3_${i}">
                        <div class="row g-2 h-100">
                            <!-- Volatility Chart (9/12) -->
                            <div class="col-9">
                                <div class="card h-100 p-2 shadow-sm">
                                    <h2 class="chart-title mb-1" style="font-size: 13px;">Volatility Chart</h2>
                                    <div class="chart-container position-relative" style="height: 220px;">
                                        <canvas id="rawScoreChart_${i}"></canvas>
                                    </div>
                                </div>
                            </div>

                            <!-- Settings (3/12) -->
                            <div class="col-3">
                                <div class="card h-100 p-2 shadow-sm d-flex flex-column justify-content-between" style="font-size: 11px;">
                                    <div>
                                        <!-- Inputs: tp, sl, volume, invest -->
                                        <div class="mb-1">
                                            <label class="form-label mb-0" style="font-size: 10px;">TP:</label>
                                            <input type="number" id="input_tp_${i}" class="form-control form-control-sm py-0 px-1" style="font-size: 11px;"
                                                onchange="set_property(${i}, 'tp', +this.value)">
                                        </div>
                                        <div class="mb-1">
                                            <label class="form-label mb-0" style="font-size: 10px;">SL:</label>
                                            <input type="number" id="input_sl_${i}" class="form-control form-control-sm py-0 px-1" style="font-size: 11px;"
                                                onchange="set_property(${i}, 'sl', +this.value)">
                                        </div>
                                        <div class="mb-1">
                                            <label class="form-label mb-0" style="font-size: 10px;">Volume:</label>
                                            <input type="number" id="input_volume_${i}" class="form-control form-control-sm py-0 px-1" style="font-size: 11px;"
                                                onchange="set_property(${i}, 'volume', +this.value)">
                                        </div>
                                        <div class="mb-1">
                                            <label class="form-label mb-0" style="font-size: 10px;">Invest:</label>
                                            <input type="text" id="input_invest_${i}" class="form-control form-control-sm py-0 px-1" style="font-size: 11px;"
                                                onchange="set_property(${i}, 'invest', +this.value)">
                                        </div>
                                    </div>

                                    <!-- Checkboxes / Switches -->
                                    <div class="mt-1 pt-1 border-top d-flex flex-column gap-1">
                                        <div class="form-check form-switch mb-0">
                                            <input class="form-check-input" type="checkbox" role="switch" id="isPlay_${i}"
                                                onchange="set_property(${i}, 'isPlay', this.checked)">
                                            <label class="form-check-label" for="isPlay_${i}">Play</label>
                                        </div>
                                        <div class="form-check form-switch mb-0">
                                            <input class="form-check-input" type="checkbox" role="switch" id="isReverse_${i}"
                                                onchange="set_property(${i}, 'isReverse', this.checked)">
                                            <label class="form-check-label" for="isReverse_${i}">Rev</label>
                                        </div>
                                    </div>
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

        // --- ĐỔ DỮ LIỆU VÀO CÁC FORM CONTROLS BẰNG ID ĐỂ TRÁNH NHẦM LẪN ---
        const inputTp = document.getElementById(`input_tp_${index}`);
        const inputSl = document.getElementById(`input_sl_${index}`);
        const inputVol = document.getElementById(`input_volume_${index}`);
        const inputInv = document.getElementById(`input_invest_${index}`);
        const chkPlay = document.getElementById(`isPlay_${index}`);
        const chkReverse = document.getElementById(`isReverse_${index}`);

        if (inputTp && document.activeElement !== inputTp) inputTp.value = item.tp ?? '';
        if (inputSl && document.activeElement !== inputSl) inputSl.value = item.sl ?? '';
        if (inputVol && document.activeElement !== inputVol) inputVol.value = item.volume ?? '';
        if (inputInv && document.activeElement !== inputInv) inputInv.value = item.invest ?? '';
        
        if (chkPlay) chkPlay.checked = !!item.isPlay;
        if (chkReverse) chkReverse.checked = !!item.isReverse;

        // Tô màu viền Card dựa theo giá trị isPlay từ Server đổ xuống
        updateCardPlayStyle(index, !!item.isPlay);

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
    console.log(idx, prop, val);

    // Cập nhật ngay giao diện tô màu viền nếu thao tác thuộc tính 'isPlay' trên UI
    if (prop === 'isPlay') {
        updateCardPlayStyle(idx, val);
    }

    if (system && system.socket_io) {
        system.socket_io.emit("set_property", { idx, prop, val });
    }
}