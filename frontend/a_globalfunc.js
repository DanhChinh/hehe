function getTimeHHMM() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

function isNumeric(str) {
  if (typeof str !== 'string' && typeof str !== 'number') return false;
  return !isNaN(str) && !isNaN(parseFloat(str));
}
function getColors(value, rangeNumber) {
  value = Math.max(-rangeNumber, Math.min(rangeNumber, value));

  let r, g, b;

  if (value < 0) {
    // Đen -> Trắng
    const t = (value + rangeNumber) / rangeNumber;
    r = Math.round(255 * t);
    g = Math.round(255 * t);
    b = Math.round(255 * t);
  } else {
    // Trắng -> Xanh lá đậm (#006400)
    const t = value / rangeNumber;
    r = Math.round(255 * (1 - t));
    g = Math.round(255 * (1 - t) + 100 * t); // 100 ứng với 64 trong hệ Hex (0x64 = 100)
    b = Math.round(255 * (1 - t));
  }

  const bgColor = `rgb(${r}, ${g}, ${b})`;

  // Sử dụng công thức chuẩn HSP để tính độ sáng trực quan của màu sắc
  const brightness = Math.sqrt(
    0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b),
  );

  // Nếu độ sáng > 127.5 là nền sáng -> chữ đen, ngược lại nền tối -> chữ trắng
  const textColor = brightness > 127.5 ? "rgb(0, 0, 0)" : "rgb(255, 255, 255)";

  return { bgColor, textColor };
}

const TradeTable = {
  maxRows: 10,
  data: {},
  tbody: document.querySelector("#tradeTable tbody"),
  total: 0,

  // 🟢 MUA (cộng dồn)
  buy(id, qty) {
    this.init(id);
    this.data[id].buy += qty;
    this.render();
  },
  sell(id, qty) {
    this.init(id);
    this.data[id].sell += qty;
    this.render();
  },

  // 🔵 Khớp mua
  matchBuy(id, qty) {
    if (!this.data[id]) return;
    this.data[id].matchBuy = qty;

    this.render();
  },

  // 🔵 Khớp bán
  matchSell(id, qty) {
    if (!this.data[id]) return;
    this.data[id].matchSell = qty;

    this.render();
  },

  // ⚫ Đóng phiên – tự tính lãi/lỗ
  close(id, thiTruong) {
    if (!this.data[id]) return;
    const t = this.data[id];
    t.market = thiTruong;

    if (thiTruong === 1) {
      t.profit = 0.97 * t.matchBuy - t.matchSell;
    } else {
      t.profit = 0.97 * t.matchSell - t.matchBuy;
    }


    if(player.getProperty("_isPlay")) {
      player.setProperty(
        "_gold",
        player.getProperty("_gold")+t.profit
      )
    }


    this.total += t.profit;
    t.total = this.total;
    this.render();
  },

  // 🧱 Khởi tạo phiên
  init(id) {
    if (!this.data[id] && id) {
      this.data[id] = {
        id,
        buy: 0,
        sell: 0,
        matchBuy: 0,
        matchSell: 0,
        market: 1.5,
        profit: 0,
        total: 0,
      };
    }
  },
  updateColors() {
    const rows = Object.values(this.data).slice(-this.maxRows);
    if (!rows.length) return;

    const profits = rows.map((r) => r.profit);
    const max = Math.max(...profits);
    const min = Math.min(...profits);

    const rangeNumber = Math.max(Math.abs(max), Math.abs(min));

    [...this.tbody.children].forEach((tr, i) => {
      const p = rows[i].profit;
      const { bgColor, textColor } = getColors(p, rangeNumber);
      tr.style.setProperty("background-color", bgColor, "important");
      tr.style.setProperty("color", textColor, "important");
      tr.style.setProperty("--bs-table-color", textColor, "important");
    });
  },
  // 🖌 Render bảng
  render() {
    this.tbody.innerHTML = "";

    Object.values(this.data)
      .slice(-this.maxRows)
      .forEach((t) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${t.id}</td>
          <td>${formatNumber(t.buy)}</td>
          <td>${formatNumber(t.matchBuy)}</td>
          <td>${formatNumber(t.sell)}</td>
          <td>${formatNumber(t.matchSell)}</td>
          <td>${t.market}</td>
          <td>${formatNumber(t.profit)}</td>
          <td>${formatNumber(t.total)}</td>
        `;
        this.tbody.appendChild(tr);
      });

    this.updateColors();
  },
};

// const formatNumber = (amount, locale = "vi-VN") => {
//   return new Intl.NumberFormat(locale, {
//     style: "decimal",
//     minimumFractionDigits: 0, // Số chữ số thập phân tối thiểu
//     maximumFractionDigits: 1, // Số chữ số thập phân tối đa
//   }).format(amount);
// };

function formatNumber(value) {
    return new Intl.NumberFormat('en-US', {
        notation: 'compact',
        compactDisplay: 'short',
        maximumFractionDigits: 1 // Giữ lại tối đa 1 chữ số thập phân nếu cần (ví dụ: 1.5M)
    }).format(value);
}
async function loadAccessToken() {
  try {
    const response = await fetch("https://cyan.io.vn/xg79/get_token.php", {
      method: "GET",
    });
    const data = await response.json();
    if (data.success) {
      return data.accessToken;
    }
  } catch (err) {
    console.error("Lỗi khi lấy token:", err);
  }
  return null;
}

function setToken(token) {
  fetch("https://cyan.io.vn/xg79/set_token.php", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "token=" + encodeURIComponent(token),
  });
}

var MESSAGE_WS = {
  url: "wss://mynisketgw.hytsocesk.com/websocket",
  login: (accessToken) => [
    1,
    "MiniGame2",
    "",
    "",
    { agentId: "1", accessToken: accessToken, reconnect: false },
  ],

  info: ["6", "MiniGame2", "taixiu_live_gateway_plugin", { cmd: 15000 }],
  result: (counter) => ["7", "MiniGame2", "1", counter],
  bet: (b, sid, eid) => [
    "6",
    "MiniGame2",
    "taixiu_live_gateway_plugin",
    { cmd: 15002, b: b, sid: sid, aid: 1, eid: eid },
  ],
};

function sendMessageToGame(b, sid, eid) {
  if (!b || !sid || !eid) return;

  let message = JSON.stringify(MESSAGE_WS.bet(b, sid, eid));
  system.setProperty("_messages", `${sid}: ${formatNumber(b)}->${eid}`);
  system.socket.send(message);
}

function insertDatabase(record) {
  if (record.progress.length === 0) return;
  let data = new FormData();
  data.append("sid", record.sid);
  data.append("progress", JSON.stringify(record.progress));
  data.append("d1", record.d1);
  data.append("d2", record.d2);
  data.append("d3", record.d3);
  axios
    .post("https://cyan.io.vn/xg79/post_data.php", data)
    .then((response) => {
      if (response.data.success) {
        system.setProperty("_messages", `Saved successfully: ${record.sid} ${record.progress.length}`)
      } else {
        console.error("Lỗi: " + response.data.message);
      }
      // console.groupEnd()
    })
    .catch((error) => {
      console.error("Lỗi kết nối:", error);
    });
}

function roundToThousand(num) { return Math.round(num / 1000) * 1000; }





