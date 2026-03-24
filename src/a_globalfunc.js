function getTimeHHMM() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}


function addMessage(content = "...", from = "Player") {
    const chatBox = document.getElementById('chat-container');
    const msgDiv = document.createElement('div');
    // msgDiv.className = `chat-message ${from}`;
    msgDiv.innerHTML = `          
        <li class="list-group-item d-flex justify-content-between">
            <div>
              <p class="mb-0 text-muted small"><strong>[${getTimeHHMM()} ${from}] </strong> ${content}</p>
            </div>
          </li>`
    chatBox.appendChild(msgDiv);

    // 👇 Giới hạn chỉ giữ lại 20 tin nhắn mới nhất
    while (chatBox.children.length > 5) {
        chatBox.removeChild(chatBox.firstChild);
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}


function setBarValue(value){
    value = Math.round(100*value/60, 0)
    const bar = document.querySelector('.progress-bar');
    bar.style.width = `${value}%`;
    bar.setAttribute('aria-valuenow', value);
    // bar.textContent = `${value}%`;
}





function lerpColor(c1, c2, t) {
  const a = c1.match(/\w\w/g).map(x => parseInt(x, 16));
  const b = c2.match(/\w\w/g).map(x => parseInt(x, 16));
  const c = a.map((v, i) => Math.round(v + (b[i] - v) * t));
  return "#" + c.map(x => x.toString(16).padStart(2, "0")).join("");
}
function gradientByMinMax(value, min, max) {
  // tất cả bằng nhau → trắng
  if (min === max) return "#ffffff";

  // điểm giữa (0)
  if (value === 0) return "#ffffff";

  // ---- LÃI (0 → max): xanh nhạt → xanh đậm
  if (value > 0) {
    const t = value / max; // 0 → 1
    return lerpColor("#E6F1D8", "#5BBD2B", t);
  }

  // ---- LỖ (min → 0): đỏ đậm → đỏ nhạt
  const t = value / min; // 0 → 1
  return lerpColor("#FCDAD5", "#E54646", t);
}


const TradeTable = {
  maxRows: 25,
  data: {},
  tbody: document.querySelector("#tradeTable tbody"),
  total:0,

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
    console.log('matchBuy',id, qty)
    if (!this.data[id]) return;
    this.data[id].matchBuy = qty;
    this.render();
  },

  // 🔵 Khớp bán
  matchSell(id, qty) {
    console.log('matchSell',id, qty)
    if (!this.data[id]) return;
    this.data[id].matchSell = qty;
    this.render();
  },

  // ⚫ Đóng phiên – tự tính lãi/lỗ
  close(id, thiTruong) {
    if (!this.data[id]) return;
    const t = this.data[id];
    t.market = thiTruong;

    /*
      Quy ước:
      - Net = khớp mua - khớp bán
      - Market lên:
          net > 0 => lãi
          net < 0 => lỗ
      - Market xuống: ngược lại
    */


    if (thiTruong === "len") {
      t.profit = 0.97*t.matchBuy - t.matchSell;
    } else {
      t.profit = 0.97*t.matchSell-t.matchBuy;
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
        market: "",
        profit: 0,
        total:0
      };
    }
  },
 updateColors() {
  const rows = Object.values(this.data).slice(-this.maxRows);
  if (!rows.length) return;

  const profits = rows.map(r => r.profit);
  const max = Math.max(...profits);
  const min = Math.min(...profits);

  [...this.tbody.children].forEach((tr, i) => {
    const p = rows[i].profit;
    const color = gradientByMinMax(p, min, max);

    // tô cột lãi
    tr.cells[6].style.backgroundColor = color;
    tr.cells[6].style.color = "#000";

    // nếu muốn tô cả dòng
    tr.style.backgroundColor = color;
  });
}
,

  // 🖌 Render bảng
  render() {
    this.tbody.innerHTML = "";

    Object.values(this.data)
      .slice(-this.maxRows)

      //style="color:${t.profit >= 0 ? 'green' : 'red'}"
      .forEach(t => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${t.id}</td>
          <td>${formatNumber(t.buy)}</td>
          <td>${formatNumber(t.matchBuy)}</td>
          <td>${formatNumber(t.sell)}</td>
          <td>${formatNumber(t.matchSell)}</td>
          <td>${t.market}</td>
          <td >${formatNumber(t.profit)}</td>
          <td >${formatNumber(t.total)}</td>
        `;
        this.tbody.appendChild(tr);
      });

    // document.getElementById("totalProfit").textContent = this.total;
    this.updateColors()
  }
};


const formatNumber = (amount, locale = 'vi-VN') => {
  return new Intl.NumberFormat(locale, {
    style: 'decimal',
    minimumFractionDigits: 0, // Số chữ số thập phân tối thiểu
    maximumFractionDigits: 2  // Số chữ số thập phân tối đa
  }).format(amount);
};