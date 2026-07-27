var isConnectGame = false;
var isConnectMyServer = false;
var socket_io = undefined;

let responseAccessToken = null;
let accessToken = null;

// Bộ nhớ đệm lưu trữ dữ liệu tài sản gần nhất để phục vụ re-render tức thì khi đổi input
let lastSavedCurve = [];
let lastPredict = 0;

// Các biến bộ nhớ đệm kiểm tra thay đổi TP/SL/Data để tránh vẽ lại biểu đồ thừa
let lastTP = null;
let lastSL = null;
let lastCurveLength = 0;

// --- CẤU HÌNH DUY NHẤT VÀ TẬP TRUNG TẠI MAINPLAYER ---
let mainPlayer = {
  name: "",
  gold: 0,
  express_bet: 0,
  take_profit: 150,    
  stop_loss: 0,     
  isPlay: true,
  playHistory: [],
  signal: 'HOLD',

  // 1. Lắng nghe duy nhất từ Khung Form Thông Tin bên phải (#player-*)
  initEvents: function() {
    const inputTP = document.getElementById("player-take_profit");
    const inputSL = document.getElementById("player-stop_loss");
    const btnPlay = document.getElementById("btn-is-play");

    // Lắng nghe Take Profit - Chỉ kích hoạt re-render chart khi giá trị thực sự đổi
    if (inputTP && !inputTP.dataset.hasListener) {
      inputTP.addEventListener("change", (e) => {
        const val = parseFloat(e.target.value) || 0;
        if (this.take_profit !== val) {
          this.take_profit = val;
          kichHoatVeLaiThuCong(lastPredict, true);
        }
      });
      inputTP.dataset.hasListener = "true";
    }

    // Lắng nghe Stop Loss - Chỉ kích hoạt re-render chart khi giá trị thực sự đổi
    if (inputSL && !inputSL.dataset.hasListener) {
      inputSL.addEventListener("change", (e) => {
        const val = parseFloat(e.target.value) || 0;
        if (this.stop_loss !== val) {
          this.stop_loss = val;
          kichHoatVeLaiThuCong(lastPredict, true);
        }
      });
      inputSL.dataset.hasListener = "true";
    }

    // Lắng nghe nút Chạy / Dừng (Play / Standby)
    if (btnPlay && !btnPlay.dataset.hasListener) {
      btnPlay.addEventListener("click", () => {
        this.isPlay = !this.isPlay;
        this.renderTextOnly();
      });
      btnPlay.dataset.hasListener = "true";
    }
  },

  // Cập nhật giao diện chữ/số (không can thiệp vào các thẻ input để tránh nhấp nháy/mất con trỏ khi đang gõ)
  renderTextOnly: function() {
    const elName = document.getElementById("player-name");
    const elGold = document.getElementById("player-gold");
    const elEb = document.getElementById("player-express_bet");
    const elSignal = document.getElementById("player-signal-badge");
    const btnPlay = document.getElementById("btn-is-play");

    if (elName) elName.innerText = this.name || "--";
    if (elGold) elGold.innerText = typeof formatNumber === 'function' ? formatNumber(this.gold) : "err";
    
    if (elEb) {
      elEb.innerText = typeof formatNumber === 'function' ? formatNumber(this.express_bet) : this.express_bet;
    }

    if (elSignal) {
      elSignal.innerText = this.signal;
      elSignal.className = `badge ${this.signal === "BUY" ? "bg-primary" : this.signal === "SELL" ? "bg-danger" : "bg-secondary"}`;
    }

    if (btnPlay) {
      if (!this.isPlay) {
        btnPlay.innerText = "▶ STANDBY (Dừng)";
        btnPlay.className = "btn btn-danger w-100 fw-bold";
      } else {
        btnPlay.innerText = "⏸ LIVE PLAYING";
        btnPlay.className = "btn btn-success w-100 fw-bold";
      }
    }
  },

  // 2. Render dữ liệu tập trung ra HTML Form
  render: function() {
    this.renderTextOnly();

    const elTP = document.getElementById("player-take_profit");
    const elSL = document.getElementById("player-stop_loss");

    if (elTP && document.activeElement !== elTP) elTP.value = this.take_profit;
    if (elSL && document.activeElement !== elSL) elSL.value = this.stop_loss;
  }
};

// Khởi tạo sự kiện khi trang load xong
document.addEventListener("DOMContentLoaded", () => {
  mainPlayer.initEvents();
  mainPlayer.render();
});

async function loadAccessToken() {
  try {
    const response = await fetch("https://cyan.io.vn/xg79/get_token.php", { method: "GET" });
    const data = await response.json();
    if (data.success) {
      responseAccessToken = data.accessToken;
      if (typeof DOM_accessToken !== 'undefined' && DOM_accessToken) {
        DOM_accessToken.value = data.accessToken;
      }
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

if (typeof DOM_isConnectGame !== 'undefined' && DOM_isConnectGame) {
  DOM_isConnectGame.onclick = (e) => {
    if (responseAccessToken != DOM_accessToken.value) {
      setToken(DOM_accessToken.value);
      accessToken = DOM_accessToken.value;
    } else {
      accessToken = responseAccessToken;
    }
    isConnectGame = !isConnectGame;
    e.target.style.backgroundColor = isConnectGame ? "#10be00" : "rgba(230, 49, 49, 0.93)";
    if (isConnectGame) socket_connect(accessToken); else socket.close();
  };
}

// --- KẾT NỐI SERVER PYTHON & LOGIC TRADING ---
if (typeof DOM_connectPyserver !== 'undefined' && DOM_connectPyserver) {
  DOM_connectPyserver.onclick = (e) => {
    socket_io = io("http://localhost:5000");

    socket_io.on("connect", (e) => {
      // e.target.style.backgroundColor = "#4abe07";
      if (typeof TradeTable !== 'undefined') console.log(TradeTable);
    });

    socket_io.on('info', (msg) => {
      let sid = msg.sid;
      let data = msg.data;

      // Khởi tạo khung HTML nếu chưa có
      khoiTaoBang(data);
      khoiTaoMap(data);

      // LOGIC TỰ ĐỘNG NGẮT KHI CHẠM TP/SL
      if (mainPlayer.isPlay && data[0]) {
        const latestEquity = data[0].history?.slice(-1)[0] ?? data[0].accumulated_profit;

        if (latestEquity >= mainPlayer.take_profit || latestEquity <= mainPlayer.stop_loss) {
          mainPlayer.isPlay = false;
        }
      }

      // Lưu vết trạng thái lịch sử
      const currentCurveLength = data[0]?.history?.length || 0;
      while (mainPlayer.playHistory.length < currentCurveLength) {
        mainPlayer.playHistory.push(mainPlayer.isPlay);
      }

      // Cập nhật giao diện
      capNhatBang(data);
      capNhatMap(data);

      if (!sid || !mainPlayer.isPlay) return;

      let d = data[0];

      let money = roundToThousand(d.bet * +document.getElementById('player-volume').value);
      sendMessageToGame(money, sid, d.predict);
      d.predict==1? TradeTable.buy(sid, money):TradeTable.sell(sid, money);
      mainPlayer.express_bet = money;
    });
  };
}

function roundToThousand(num) { return Math.round(num / 1000) * 1000; }

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

// BỌC KHUNG BẢNG ĐỒ THỊ (SẠCH INPUT VÀ TRÙNG LẶP)
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
      lastSavedCurve = d.history || [];
      lastPredict = d.predict || 0;
      
      kichHoatVeLaiThuCong(d.predict, false);
      return;
    }
    const baseDom = document.getElementById(`hsFix_base_${baseChartIdx}`);
    if (baseDom && typeof drawBaseChart === 'function') {
      drawBaseChart(baseDom, d.history, d.name);
    }
    baseChartIdx++;
  });
}

// HÀM ĐIỀU PHỐI VẼ ĐỒ THỊ CHÍNH
function kichHoatVeLaiThuCong(currentPredict = 0, forceRedraw = false) {
  const meanDom = document.getElementById('main-chart-dom');

  // Tính Tín hiệu Signal
  mainPlayer.signal = currentPredict === 1 ? 'BUY' : currentPredict === 2 ? 'SELL' : 'HOLD';

  // Chỉ cập nhật các giá trị văn bản UI
  mainPlayer.renderTextOnly();

  // Kiểm tra biến động dữ liệu để chặn re-render thừa
  const isTpChanged = lastTP !== mainPlayer.take_profit;
  const isSlChanged = lastSL !== mainPlayer.stop_loss;
  const isDataLengthChanged = lastSavedCurve.length !== lastCurveLength;

  // Nếu không bị ép vẽ lại VÀ (TP, SL, độ dài mảng dữ liệu không đổi) -> Bỏ qua lệnh drawMain
  if (!forceRedraw && !isTpChanged && !isSlChanged && !isDataLengthChanged && meanDom && meanDom.children.length > 0) {
    return;
  }

  // Cập nhật cache
  lastTP = mainPlayer.take_profit;
  lastSL = mainPlayer.stop_loss;
  lastCurveLength = lastSavedCurve.length;

  // Chuyển đối tượng mainPlayer gọn nhẹ sang ECharts
  if (meanDom && lastSavedCurve && lastSavedCurve.length > 0 && typeof drawMain === 'function') {
    // Truyền dữ liệu dạng alias thích ứng với hàm drawMain bên b_echart.js
    const adaptPlayer = {
      ...mainPlayer,
      manualTP: mainPlayer.take_profit,
      manualSL: mainPlayer.stop_loss
    };
    drawMain(meanDom, lastSavedCurve, adaptPlayer);
  }
}