/**
 * HÀM VẼ ĐỒ THỊ CHÍNH (OBJ_MEAN) - Hỗ trợ chẻ màu đoạn và vẽ TP/SL cố định
 */
function drawMain(chartDom, dataArray, player) {
  if (!chartDom || !dataArray || dataArray.length === 0) return;

  let chart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom, "dark");
  const { isPlay, manualTP, manualSL, playHistory } = player;

  // Phân đoạn màu sắc đường vẽ theo lịch sử
  let piecesData = [];
  if (playHistory && playHistory.length > 0) {
    let startIdx = 0;
    let currentStatus = playHistory[0];

    for (let i = 1; i < playHistory.length; i++) {
      if (playHistory[i] !== currentStatus) {
        piecesData.push({
          gt: startIdx,
          lte: i,
          color: currentStatus ? "#a855f7" : "#4b5563"
        });
        startIdx = i;
        currentStatus = playHistory[i];
      }
    }
    piecesData.push({ gt: startIdx, lte: playHistory.length, color: currentStatus ? "#a855f7" : "#4b5563" });
  }

  // Đường gạch đứt TP / SL
  const markLinesData = [];
  const tpColor = isPlay ? "#22c55e" : "rgba(34, 197, 94, 0.4)";
  const slColor = isPlay ? "#ef4444" : "rgba(239, 68, 68, 0.4)";

  if (manualTP !== undefined && manualTP !== null && !isNaN(manualTP)) {
    markLinesData.push({
      yAxis: manualTP,
      name: "TP",
      lineStyle: { color: tpColor, type: "dashed", width: isPlay ? 2 : 1 },
      label: { formatter: `TP: {c}`, position: "end", color: tpColor, backgroundColor: "#18181b", padding: [2, 4], borderRadius: 3 }
    });
  }

  if (manualSL !== undefined && manualSL !== null && !isNaN(manualSL)) {
    markLinesData.push({
      yAxis: manualSL,
      name: "SL",
      lineStyle: { color: slColor, type: "dashed", width: isPlay ? 2 : 1 },
      label: { formatter: `SL: {c}`, position: "end", color: slColor, backgroundColor: "#18181b", padding: [2, 4], borderRadius: 3 }
    });
  }

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: "#1f2937",
      borderColor: "#374151",
      textStyle: { color: "#fff" }
    },
    grid: { left: "3%", right: "12%", bottom: "5%", top: "20", containLabel: true },
    xAxis: {
      type: "category",
      data: dataArray.map((_, i) => i),
      axisLine: { lineStyle: { color: "#374151" } }
    },
    yAxis: {
      type: "value",
      scale: true,
      splitLine: { lineStyle: { color: "#1f2937" } }
    },
    visualMap: {
      show: false,
      type: "piecewise",
      dimension: 0,
      pieces: piecesData.length > 0 ? piecesData : [{ gt: 0, color: "#4b5563" }]
    },
    series: [
      {
        name: "Vốn Tổng",
        type: "line",
        data: dataArray,
        smooth: 0.1,
        symbol: "none",
        lineStyle: { width: 3 },
        markLine: { symbol: ["none", "none"], data: markLinesData }
      }
    ]
  };

  chart.setOption(option, true);
}

/**
 * HÀM VẼ ĐỒ THỊ PHỤ (MODEL BASE CHÌM)
 */
function drawBaseChart(chartDom, dataArray, modelName) {
    if (!chartDom || !dataArray || dataArray.length === 0) return;
    let chart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
    const option = {
        title: { text: `${modelName}`, textStyle: { color: '#9ca3af', fontSize: 11 }, top: 5, left: 10 },
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