var isConnectGame = false;
var isConnectMyServer = false;
var socket_io = undefined;

let responseAccessToken = null;
let accessToken = null;

// Bộ nhớ đệm lưu trữ dữ liệu tài sản gần nhất để phục vụ re-render tức thì khi đổi input
let lastSavedCurve = [];
let lastPredict = 0;

// --- CẤU HÌNH TRẠNG THÁI KHỞI TẠO MẶC ĐỊNH ---
let meanTradingState = {
  isPlay: false,
  playHistory: [],
  mgs_As_gold: 0
};

async function loadAccessToken() {
  try {
    const response = await fetch("https://cyan.io.vn/xg79/get_token.php", { method: "GET" });
    const data = await response.json();
    if (data.success) {
      responseAccessToken = data.accessToken;
      DOM_accessToken.value = data.accessToken;
    }
  } catch (err) {
    console.error("Lỗi khi lấy token:", err);
  }
}
loadAccessToken();

function setToken(token) {
  fetch("https://cyan.io.vn/xg79/set_token.php", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "token=" + encodeURIComponent(token)
  });
}

DOM_isConnectGame.onclick = (e) => {
  if (responseAccessToken != DOM_accessToken.value) {
    setToken(DOM_accessToken.value);
    accessToken = DOM_accessToken.value;
  } else {
    accessToken = responseAccessToken;
  }
  isConnectGame = !isConnectGame;
  e.target.style.backgroundColor = isConnectGame ? "#F08080" : "red";
  if (isConnectGame) socket_connect(accessToken); else socket.close();
};

// --- KẾT NỐI SERVER PYTHON & LOGIC TRADING OBJ_MEAN ---
DOM_connectPyserver.onclick = (e) => {
  socket_io = io("http://localhost:5000");

  socket_io.on("connect", () => {
    e.target.style.backgroundColor = "F08080";
  });

  socket_io.on('info', (msg) => {
    let sid = msg.sid;
    let data = msg.data;
    console.log()
    console.log(sid)
    console.log(data)

    // Khởi tạo giao diện (Chỉ vẽ khung HTML nếu chưa tồn tại)
    khoiTaoBang(data);
    khoiTaoMap(data);

    // Đọc trạng thái nút bấm isPlay trực tiếp từ Switch trên giao diện
    const meanPlayCheckbox = document.getElementById("mean-is-play");
    if (meanPlayCheckbox) {
      meanTradingState.isPlay = meanPlayCheckbox.checked;
    }

    // --- LOGIC TỰ ĐỘNG NGẮT (CHECK VA CHẠM KHI CÓ DỮ LIỆU MỚI TỪ PYTHON) ---
    if (meanTradingState.isPlay && data[0]) {
      const tpPrice = parseFloat(document.getElementById("manual-tp")?.value) || 999999;
      const slPrice = parseFloat(document.getElementById("manual-sl")?.value) || -999999;
      const latestEquity = data[0].fixed_equity_curve?.slice(-1)[0] ?? data[0].accumulated_profit;

      if (latestEquity >= tpPrice || latestEquity <= slPrice) {
        meanTradingState.isPlay = false;
        if (meanPlayCheckbox) meanPlayCheckbox.checked = false;

        const label = document.getElementById("mean-is-play-label");
        if (label) {
          label.innerText = "OFF (Chạm Mốc Thủ Công)";
          label.className = "form-check-label fw-bold text-danger";
        }
      }
    }

    // Đồng bộ mảng lịch sử trạng thái chạy phục vụ ECharts chẻ đoạn màu
    const currentCurveLength = data[0]?.fixed_equity_curve?.length || 0;
    while (meanTradingState.playHistory.length < currentCurveLength) {
      meanTradingState.playHistory.push(meanTradingState.isPlay);
    }

    // Cập nhật dữ liệu lên bảng và kích hoạt luồng vẽ lại toàn bộ đồ thị
    capNhatBang(data);
    capNhatMap(data);

    if (!sid || !meanTradingState.isPlay) return;

    // --- LOGIC TÍNH TOÁN KHỐI LƯỢNG VÀ ĐẨY LỆNH VÀO GAME ---
    let buy = 0;
    let sell = 0;
    let globalVolElement = document.getElementById("global-volume");
    let volume = globalVolElement ? (+globalVolElement.value * 1000) : 1000;

    data.forEach((d) => {
      if (d.is_main) return;
      if (d.predict == 1) buy += volume * d.expected_bet;
      else if (d.predict == 2) sell += volume * d.expected_bet;
    });

    if (Math.floor(buy) === Math.floor(sell)) return;

    if (buy > sell) {
      let money = roundToThousand(buy - sell);
      TradeTable.buy(sid, money);
      sendMessageToGame(money, sid, 1);
    } else {
      let money = roundToThousand(sell - buy);
      TradeTable.sell(sid, money);
      sendMessageToGame(money, sid, 2);
    }
  });
};

function roundToThousand(num) { return Math.round(num / 1000) * 1000; }

function khoiTaoBang(data, parent = document.getElementById("DOM_dashboard")) {
  if (parent.innerHTML.trim() != "") return;
  let headText = `<div class="card shadow-sm has-close-btn"><div class="table-responsive"><table id="Trading_Dashboard" class="table table-sm table-borderless align-middle mb-0 text-center"><thead><tr><th>model_name</th><th>predict</th><th>expected_bet</th><th>current_position_size</th><th>accumulated_profit</th><th>streak_counter</th><th style="width: 150px;">Role Status</th></tr></thead><tbody id="tableBody">`;
  let mainText = "";
  data.forEach((d) => {
    if (d.is_main) {
      mainText += `<tr class="table-active border-bottom border-secondary table-warning"><td class="fw-bold text-start ps-3 text-dark">⭐ MEAN</td><td id="mean-predict" class="fw-bold">-</td><td>-</td><td>-</td><td id="mean-profit" class="fw-bold">-</td><td>-</td><td><span class="badge bg-danger">LIVE ACCOUNT</span></td></tr>`;
    } else {
      mainText += `<tr><td class="fw-bold text-start ps-3 text-muted">${d.model_name}</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td><span class="badge bg-secondary">CALCULATOR</span></td></tr>`;
    }
  });
  parent.innerHTML = headText + mainText + "</tbody></table></div></div>";
}

function khoiTaoMap(data, parent = document.getElementById("DOM_map")) {
  if (parent.innerHTML.trim() != "") return;
  let text = `<div class="row g-2">`;
  let baseChartCount = 0;

  data.forEach((e) => {
    if (e.is_main) {
      text += `
        <div class="col-12 mb-3">
          <div class="main-trading-card p-3 bg-dark text-white rounded">
            <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
                <h4 class="mb-0 fw-bold text-warning">📊 BIỂU ĐỒ TRADING TỔNG</h4>
                <div class="controls d-flex align-items-center gap-2 flex-wrap">
                    <label class="mb-0 text-warning small fw-bold">As: <span id="mgs_As_gold">0</span> </label>
                    <label class="mb-0 text-info small fw-bold">Vol: <input type="number" id="global-volume" value="1" min="1" class="form-control form-control-sm d-inline-block bg-secondary text-white border-0 text-center" style="width: 55px;"></label>
                    <label class="mb-0 text-success small fw-bold">Mốc TP: <input type="number" id="manual-tp" value="15" class="form-control form-control-sm d-inline-block bg-secondary text-white border-0 text-center" style="width: 85px;"></label>
                    <label class="mb-0 text-danger small fw-bold">Mốc SL: <input type="number" id="manual-sl" value="-15" class="form-control form-control-sm d-inline-block bg-secondary text-white border-0 text-center" style="width: 85px;"></label>
                    <div class="form-check form-switch mb-0 ms-2">
                        <input class="form-check-input" type="checkbox" id="mean-is-play">
                        <label class="form-check-label fw-bold text-danger" id="mean-is-play-label" for="mean-is-play">OFF (Standby)</label>
                    </div>
                </div>
            </div>
            <div id="main-chart-dom" style="width: 100%; height: 350px;"></div>
          </div>
        </div>`;
    } else {
      text += `<div class="col-12 col-md-6"><div class="card h-100 bg-dark border-secondary"><div id="hsFix_base_${baseChartCount}" class="chart-box w-100" style="height: 180px;"></div></div></div>`;
      baseChartCount++;
    }
  });
  parent.innerHTML = text + `</div>`;

  // LẮNG NGHE SỰ KIỆN GÕ PHÍM / THAY ĐỔI CÔNG TẮC ĐỂ RE-RENDER ĐỒ THỊ TỨC THỜI (REALTIME)
  setTimeout(() => {
    const liveInputs = ['manual-tp', 'manual-sl', 'mean-is-play', 'global-volume'];
    liveInputs.forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        element.addEventListener(element.type === 'checkbox' ? 'change' : 'input', () => {
          const meanPlayCheckbox = document.getElementById("mean-is-play");
          if (meanPlayCheckbox) {
            meanTradingState.isPlay = meanPlayCheckbox.checked;
          }
          if (lastSavedCurve && lastSavedCurve.length > 0) {
            kichHoatVeLaiThuCong(lastPredict);
          }
        });
      }
    });
  }, 400);
}

function capNhatBang(data, table = document.getElementById("DOM_dashboard")) {
  if (!table) return;
  let tbody = table.getElementsByTagName('tbody')[0];
  let rows = tbody.getElementsByTagName('tr');

  data.forEach((d, i) => {
    let row = rows[i]; if (!row) return;
    if (d.is_main) {
      document.getElementById("mean-predict").innerText = d.predict === 1 ? "BUY" : (d.predict === 2 ? "SELL" : "HOLD");
      document.getElementById("mean-predict").className = d.predict === 1 ? "text-primary fw-bold" : (d.predict === 2 ? "text-danger" : "text-muted");
      document.getElementById("mean-profit").innerText = d.accumulated_profit;
    } else {
      row.cells[0].innerText = d.model_name;
      row.cells[1].innerText = d.predict || "-";
      row.cells[1].className = d.predict === 1 ? "text-primary fw-bold" : (d.predict === 2 ? "text-danger" : "text-muted");
      row.cells[2].innerText = d.expected_bet;
      row.cells[3].innerText = d.current_position_size;
      row.cells[4].innerText = d.accumulated_profit;
      row.cells[5].innerText = d.streak_counter;
    }
  });
}

function capNhatMap(data) {
  let baseChartIdx = 0;
  data.forEach((d) => {
    if (d.is_main === true) {
      lastSavedCurve = d.fixed_equity_curve; // Ghi nhận mảng đồ thị mới từ socket phục vụ render
      lastPredict = d.predict;               // Ghi nhận tín hiệu mới
      kichHoatVeLaiThuCong(d.predict);       // KÍCH HOẠT LUỒNG VẼ ĐỒ THỊ CHÍNH
      return;
    }
    const baseDom = document.getElementById(`hsFix_base_${baseChartIdx}`);
    if (baseDom) {
      drawBaseChart(baseDom, d.fixed_equity_curve, d.model_name);
    }
    baseChartIdx++;
  });
}

// HÀM ĐIỀU PHỐI BIẾN ĐỘNG TRỰC TIẾP TRÊN GIAO DIỆN SANG CHARTS.JS
function kichHoatVeLaiThuCong(currentPredict = 0) {
  const meanDom = document.getElementById('main-chart-dom');
  if (!meanDom || !lastSavedCurve || lastSavedCurve.length === 0) return;

  const isPlayChecked = meanTradingState.isPlay;
  const tpVal = parseFloat(document.getElementById('manual-tp')?.value);
  const slVal = parseFloat(document.getElementById('manual-sl')?.value);

  const label = document.getElementById("mean-is-play-label");
  if (label) {
    label.innerText = isPlayChecked ? "ON (Live Order)" : "OFF (Standby)";
    label.className = isPlayChecked ? "form-check-label fw-bold text-success" : "form-check-label fw-bold text-danger";
  }

  let tradingParams = {
    isPlay: isPlayChecked,
    manualTP: isNaN(tpVal) ? null : tpVal,
    manualSL: isNaN(slVal) ? null : slVal,
    signal: currentPredict === 1 ? 'BUY' : currentPredict === 2 ? 'SELL' : 'HOLD',
    playHistory: meanTradingState.playHistory
  };

  // Đẩy tham số sang hàm cấu hình của ECharts
  drawMain(meanDom, lastSavedCurve, tradingParams);
}