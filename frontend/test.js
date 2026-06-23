// Trạng thái cấu hình lưu trữ cục bộ của hệ thống Mean trên Frontend
let meanTradingState = {
    isPlay: localStorage.getItem('mean_isPlay') !== 'false', // Mặc định là true nếu chưa set
    equityHistory: [] // Lưu lại đường cong tài sản thực tế của tài khoản trade tổng
};

// 1. HÀM VẼ BIỂU ĐỒ RIÊNG CHO ĐỐI TƯỢNG TRADING TỔNG (drawMain)
function drawMain(chartDom, dataArray, tradingParams) {
    let chart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
    
    const { isPlay, signal, finalVolume, currentProfit } = tradingParams;

    // Tính toán các mốc Take Profit / Stop Loss dựa trên Vốn hiện tại và Volume vào lệnh
    const markLinesData = [];
    if (isPlay && signal !== 'HOLD') {
        const entryPrice = currentProfit;
        // Giả lập biên mục tiêu Chốt lời = Vốn hiện tại + 3 lần Volume; Cắt lỗ = Vốn hiện tại - 2 lần Volume
        const tpPrice = currentPrice + (finalVolume * 3);
        const slPrice = currentPrice - (finalVolume * 2);

        markLinesData.push(
            { yAxis: entryPrice, name: 'Entry', lineStyle: { color: '#38bdf8', type: 'solid' }, label: { formatter: 'Entry: {c}' } },
            { yAxis: tpPrice, name: 'TP', lineStyle: { color: '#22c55e', type: 'dashed' }, label: { formatter: 'TP: {c}' } },
            { yAxis: slPrice, name: 'SL', lineStyle: { color: '#ef4444', type: 'dashed' }, label: { formatter: 'SL: {c}' } }
        );
    }

    let statusColor = isPlay ? (signal === 'BUY' ? '#22c55e' : signal === 'SELL' ? '#ef4444' : '#9ca3af') : '#dc2626';
    let statusText = isPlay ? `Hệ thống: RUNNING  |  Lệnh: ${signal}  |  Khối lượng vào: ${finalVolume}` : `Hệ thống: STOPPED (Đứng ngoài thị trường)`;

    const option = {
        title: {
            text: "Đường Cong Hiệu Suất Tài Khoản Tổng",
            subtext: statusText,
            textStyle: { color: '#f3f4f6', fontSize: 16 },
            subtextStyle: { color: statusColor, fontSize: 12, fontWeight: 'bold' },
            top: 5, left: 10
        },
        tooltip: { trigger: 'axis', backgroundColor: '#1f2937', borderColor: '#374151' },
        grid: { left: '4%', right: '12%', bottom: '5%', top: '70', containLabel: true },
        xAxis: { type: 'category', data: dataArray.map((_, i) => i), axisLine: { lineStyle: { color: '#374151' } } },
        yAxis: { type: 'value', scale: true, splitLine: { lineStyle: { color: '#1f2937' } } },
        series: [{
            name: 'Vốn Tổng', type: 'line', data: dataArray, smooth: 0.2, symbol: 'none',
            lineStyle: { width: 3, color: '#a855f7' }, // Màu Tím hoàng gia đại diện cho tài khoản Tổng
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(168, 85, 247, 0.2)' },
                    { offset: 1, color: 'rgba(168, 85, 247, 0)' }
                ])
            },
            markLine: { symbol: ['none', 'none'], data: markLinesData }
        }]
    };
    chart.setOption(option);
}

// 2. HÀM VẼ BIỂU ĐỒ ĐƠN GIẢN CHO CÁC MODEL BASE (Chỉ phục vụ tính toán)
function drawBaseChart(chartDom, dataArray, modelName) {
    let chart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
    const option = {
        title: { text: `${modelName} (Nền tảng tính toán)`, textStyle: { color: '#9ca3af', fontSize: 12 }, top: 5, left: 5 },
        grid: { left: '3%', right: '3%', bottom: '3%', top: '40', containLabel: true },
        xAxis: { type: 'category', data: dataArray.map((_, i) => i), axisLabel: { show: false } },
        yAxis: { type: 'value', scale: true, splitLine: { lineStyle: { color: '#1f2937' } } },
        series: [{ data: dataArray, type: 'line', smooth: 0.1, symbol: 'none', lineStyle: { color: '#4b5563', width: 1.5 } }] // Đường xám chìm
    };
    chart.setOption(option);
}

// 3. HÀM XỬ LÝ ĐIỀU PHỐI VÀ TÍNH TOÁN LOGIC TRADING CHÍNH (Core Loop)
async function updateDashboard() {
    const response = await fetch('/api/get-all-info');
    const allData = await response.json();

    // Tách dòng Mean ra riêng và mảng các model cơ sở ra riêng
    const objMeanRaw = allData.find(item => item.is_main === true);
    const baseModels = allData.filter(item => item.is_main === false);

    // Thu thập cấu hình đầu vào từ UI Frontend
    const volumeInput = parseFloat(document.getElementById('global-volume').value) || 0;
    const isPlayChecked = document.getElementById('mean-is-play').checked;
    meanTradingState.isPlay = isPlayChecked;
    localStorage.setItem('mean_isPlay', isPlayChecked);

    // --- BẮT ĐẦU LOGIC QUYẾT ĐỊNH TRADING CỦA OBJ_MEAN TRÊN FRONTEND ---
    let buyVotes = 0;
    let sellVotes = 0;

    baseModels.forEach(model => {
        // Chỉ lấy phiếu bầu từ các mô hình nền tảng đang ở trạng thái BẬT (position_enabled === true)
        if (model.position_enabled && model.predict !== null) {
            // Trọng số = predict x expected_bet x Volume_Input
            const weight = model.expected_bet * volumeInput;
            
            if (model.predict === 1) buyVotes += weight;  // Tín hiệu BUY
            if (model.predict === 2) sellVotes += weight; // Tín hiệu SELL
        }
    });

    // Ra quyết định dựa trên tỷ lệ phiếu bầu bên nào lớn hơn
    let finalDecision = 'HOLD';
    let finalVolume = 0;

    if (meanTradingState.isPlay) { // Quy tắc 3: Nếu false -> đứng ngoài, nếu true -> đi lệnh theo tính toán
        if (buyVotes > sellVotes) {
            finalDecision = 'BUY';
            finalVolume = parseFloat((buyVotes - sellVotes).toFixed(2)); // Khối lượng ròng sau khi triệt tiêu bù trừ
        } else if (sellVotes > buyVotes) {
            finalDecision = 'SELL';
            finalVolume = parseFloat((sellVotes - buyVotes).toFixed(2));
        }
    }
    // ------------------------------------------------------------------

    // Vẽ biểu đồ chính cho obj_mean thông qua hàm drawMain
    const mainChartDom = document.getElementById('main-chart-dom');
    const tradingParams = {
        isPlay: meanTradingState.isPlay,
        signal: finalDecision,
        finalVolume: finalVolume,
        currentProfit: objMeanRaw.accumulated_profit
    };
    drawMain(mainChartDom, objMeanRaw.fixed_equity_curve, tradingParams);

    // Render danh sách các Model Base phục vụ tính toán xuống phía dưới
    const baseContainer = document.getElementById('base-models-container');
    baseContainer.innerHTML = ''; // Clear cũ

    baseModels.forEach(model => {
        const cardHtml = `
            <div class="base-model-card ${model.position_enabled ? 'active' : 'disabled'}">
                <div class="card-mini-header">
                    <span>${model.model_name}</span>
                    <button onclick="toggleBaseModel(${model.original_index})">
                        ${model.position_enabled ? '⏸ Pause Weight' : '▶ Active Weight'}
                    </button>
                </div>
                <div class="model-stats">Predict: ${model.predict || 'None'} | Bet: ${model.expected_bet}</div>
                <div id="base-chart-${model.original_index}" style="width: 100%; height: 130px;"></div>
            </div>
        `;
        baseContainer.insertAdjacentHTML('beforeend', cardHtml);
        
        // Vẽ đồ thị thô chìm cho model base
        const dom = document.getElementById(`base-chart-${model.original_index}`);
        drawBaseChart(dom, model.fixed_equity_curve, model.model_name);
    });
}

// Hàm gạt nút Toggle kích hoạt trọng số của từng model base
async function toggleBaseModel(originalIndex) {
    await fetch(`/api/set-position?index=${originalIndex}`, { method: 'POST' });
    updateDashboard(); // Cập nhật lại giao diện và tính toán lại tỷ lệ lệnh tức thì
}

// Hàm gạt nút tắt toàn cục của tài khoản tổng Mean
function toggleMeanTrading() {
    updateDashboard();
}

// Khởi tạo chạy đồng bộ lần đầu tiên khi load trang
document.getElementById('mean-is-play').checked = meanTradingState.isPlay;
updateDashboard();