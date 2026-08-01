
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


function khoiTaoBang(data, parent = document.getElementById("DOM_dashboard")) {
  if (!parent || parent.innerHTML.trim() !== "") return;

  const headText = `
    <div class="card shadow-sm has-close-btn">
      <div class="table-responsive">
        <table id="Trading_Dashboard" class="table table-sm table-borderless align-middle mb-0 text-center">
          <thead>
            <tr>
              <th class="text-start ps-3">Model Name</th>
              <th>Predict</th>
              <th>Bet</th>
              <th>Money</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="tableBody">`;

  let mainText = "";
  data.forEach((d) => {
    mainText += `
      <tr>
        <td class="fw-bold text-start ps-3">${d.name || "-"}</td>
        <td class="fw-bold">-</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
      </tr>`;
  });

  parent.innerHTML = headText + mainText + `</tbody></table></div></div>`;
}

function khoiTaoMap(data, parent = document.getElementById("DOM_map")) {
  if (!parent || parent.innerHTML.trim() !== "") return;

  let text = `<div class="row g-2">`;
  let baseChartCount = 0;

  data.forEach((e) => {
    if (e.is_main) {
      text += `
        <div class="col-12 mb-3">
          <div class="main-trading-card p-3 bg-dark text-white rounded shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom border-secondary">
                <h5 class="mb-0 fw-bold text-warning">📊 BIỂU ĐỒ TRADING TỔNG</h5>
            </div>
            <!-- Chỉ để lại duy nhất Canvas Biểu đồ -->
            <div id="main-chart-dom" style="width: 100%; height: 360px;"></div>
          </div>
        </div>`;
    } else {
      text += `<div class="col-12 col-md-6"><div class="card h-100 bg-dark border-secondary"><div id="hsFix_base_${baseChartCount}" class="chart-box w-100" style="height: 180px;"></div></div></div>`;
      baseChartCount++;
    }
  });
  parent.innerHTML = text + `</div>`;
}


function capNhatBang(data, table = document.getElementById("DOM_dashboard")) {
  if (!table) return;
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  const rows = tbody.getElementsByTagName('tr');

  data.forEach((d, i) => {
    const row = rows[i];
    if (!row) return;

    row.cells[0].innerText = d.name || "-";

    let predictText = "HOLD";
    let predictClass = "text-muted";

    if (d.predict === 1) {
      predictText = "BUY";
      predictClass = "text-primary fw-bold";
    } else if (d.predict === 2) {
      predictText = "SELL";
      predictClass = "text-danger fw-bold";
    }

    row.cells[1].innerText = predictText;
    row.cells[1].className = predictClass;
    row.cells[2].innerText = d.bet !== undefined ? d.bet : "-";
    row.cells[3].innerText = d.money !== undefined ? d.money : "-";
    row.cells[4].innerText = d.status ? "Betting" : "Waiting";
  });
}

function capNhatMap(data) {
  let baseChartIdx = 0;
  data.forEach((d) => {
    if (d.is_main === true) {
      drawBaseChart(
        document.getElementById("main-chart-dom"),
        d.history,
        d.name
      )
      return;
    }
    const baseDom = document.getElementById(`hsFix_base_${baseChartIdx}`);
    if (baseDom && typeof drawBaseChart === 'function') {
      drawBaseChart(baseDom, d.history, d.name);
    }
    baseChartIdx++;
  });
}










