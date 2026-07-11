/**
 * HÀM VẼ ĐỒ THỊ CHÍNH (OBJ_MEAN) - Hỗ trợ chẻ màu đoạn và vẽ TP/SL cố định
 */
function drawMain(chartDom, dataArray, tradingParams) {
    if (!chartDom || !dataArray || dataArray.length === 0) return;
    
    let chart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
    const { isPlay, signal, manualTP, manualSL, playHistory } = tradingParams;

    // 1. Thuật toán phân đoạn màu sắc dựa theo mảng lịch sử playHistory
    let piecesData = [];
    if (playHistory && playHistory.length > 0) {
        let startIdx = 0;
        let currentStatus = playHistory[0];

        for (let i = 1; i < playHistory.length; i++) {
            if (playHistory[i] !== currentStatus) {
                piecesData.push({
                    gt: startIdx,
                    lte: i,
                    color: currentStatus ? '#a855f7' : '#4b5563' // True -> Tím, False -> Xám
                });
                startIdx = i;
                currentStatus = playHistory[i];
            }
        }
        piecesData.push({ gt: startIdx, lte: playHistory.length, color: currentStatus ? '#a855f7' : '#4b5563' });
    }

    // 2. Thiết lập đường biên TP/SL cố định (Cấu hình màu sắc tương phản rõ nét)
    const markLinesData = [];
    const tpColor = isPlay ? '#22c55e' : 'rgba(34, 197, 94, 0.4)';  // Xanh lá đậm / Xanh lá mờ
    const slColor = isPlay ? '#ef4444' : 'rgba(239, 68, 68, 0.4)';   // Đỏ đậm / Đỏ mờ
    const suffix = isPlay ? '(LIVE)' : '(PREVIEW)';

    if (manualTP !== undefined && manualTP !== null && !isNaN(manualTP)) {
        markLinesData.push({ 
            yAxis: manualTP, 
            name: 'TP', 
            lineStyle: { color: tpColor, type: 'dashed', width: isPlay ? 2 : 1.2 }, 
            label: { formatter: `TP ${suffix}: {c}`, position: 'end', color: tpColor, backgroundColor: '#1e1e24', padding: [2, 4], borderRadius: 3 } 
        });
    }

    if (manualSL !== undefined && manualSL !== null && !isNaN(manualSL)) {
        markLinesData.push({ 
            yAxis: manualSL, 
            name: 'SL', 
            lineStyle: { color: slColor, type: 'dashed', width: isPlay ? 2 : 1.2 }, 
            label: { formatter: `SL ${suffix}: {c}`, position: 'end', color: slColor, backgroundColor: '#1e1e24', padding: [2, 4], borderRadius: 3 } 
        });
    }

    let statusColor = isPlay ? (signal === 'BUY' ? '#22c55e' : signal === 'SELL' ? '#ef4444' : '#9ca3af') : '#ef4444';
    let statusText = isPlay ? `Hệ thống: LIVE RUNNING | Mục tiêu TP: ${manualTP} | Rủi ro SL: ${manualSL}` : `Hệ thống: STANDBY SHUTDOWN (Dừng đẩy lệnh)`;

    const option = {
        title: {
            text: "ĐƯỜNG CONG TÀI SẢN TỔNG HỆ THỐNG (OBJ_MEAN)",
            subtext: statusText,
            textStyle: { color: '#f3f4f6', fontSize: 14 },
            subtextStyle: { color: statusColor, fontSize: 12, fontWeight: 'bold' },
            top: 5, left: 10
        },
        tooltip: { trigger: 'axis', backgroundColor: '#1f2937', borderColor: '#374151', textStyle: { color: '#fff' } },
        grid: { left: '4%', right: '18%', bottom: '5%', top: '70', containLabel: true },
        xAxis: { type: 'category', data: dataArray.map((_, i) => i), axisLine: { lineStyle: { color: '#374151' } } },
        yAxis: { 
            type: 'value', 
            scale: true, // Tự động co dãn biên độ theo dữ liệu tài sản thực tế xung quanh mốc nhỏ (~15)
            splitLine: { lineStyle: { color: '#1f2937' } } 
        },
        visualMap: {
            show: false,
            type: 'piecewise',
            dimension: 0, 
            pieces: piecesData.length > 0 ? piecesData : [{ gt: 0, color: '#4b5563' }] 
        },
        series: [{
            name: 'Vốn Tổng', type: 'line', data: dataArray, smooth: 0.1, symbol: 'none',
            lineStyle: { width: 3 }, 
            markLine: { symbol: ['none', 'none'], data: markLinesData }
        }]
    };
    chart.setOption(option);
    if (!chartDom.dataset.resizeAttached) {
        window.addEventListener('resize', () => chart.resize());
        chartDom.dataset.resizeAttached = "true"; // Đánh dấu tránh trùng lặp sự kiện
    }
}

/**
 * HÀM VẼ ĐỒ THỊ PHỤ (MODEL BASE CHÌM)
 */
function drawBaseChart(chartDom, dataArray, modelName) {
    if (!chartDom || !dataArray || dataArray.length === 0) return;
    let chart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
    const option = {
        title: { text: `${modelName} (Nền tảng tính toán)`, textStyle: { color: '#9ca3af', fontSize: 11 }, top: 5, left: 10 },
        grid: { left: '4%', right: '4%', bottom: '5%', top: '40', containLabel: true },
        xAxis: { type: 'category', data: dataArray.map((_, i) => i), axisLabel: { show: false } },
        yAxis: { type: 'value', scale: true, splitLine: { lineStyle: { color: '#1f2937' } } },
        series: [{ data: dataArray, type: 'line', smooth: 0.1, symbol: 'none', lineStyle: { color: '#4b5563', width: 1.2 } }]
    };
    chart.setOption(option);
    if (!chartDom.dataset.resizeAttached) {
        window.addEventListener('resize', () => chart.resize());
        chartDom.dataset.resizeAttached = "true";
    }
}