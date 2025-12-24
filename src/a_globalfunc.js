function getTimeHHMM() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}


function addMessage(content = "...", from = "player") {
    const chatBox = document.getElementById('chat-container');
    const msgDiv = document.createElement('div');
    // msgDiv.className = `chat-message ${from}`;
    msgDiv.innerHTML = `          
        <li class="list-group-item d-flex justify-content-between">
            <div>
            ${getTimeHHMM()}
              <strong>${from}</strong>
              <p class="mb-0 text-muted small">${content}</p>
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







const TradeTable = {
  maxRows: 10,
  data: {},
  tbody: document.querySelector("#tradeTable tbody"),

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
    const net = t.matchBuy - t.matchSell;

    if (thiTruong === "len") {
      t.profit = net;
    } else {
      t.profit = -net;
    }

    this.render();
  },

  // 🧱 Khởi tạo phiên
  init(id) {
    if (!this.data[id]) {
        if(!id){id=0}
      this.data[id] = {
        id,
        buy: 0,
        sell: 0,
        matchBuy: 0,
        matchSell: 0,
        market: "",
        profit: 0
      };
    }
  },
  updateColors() {
  const rows = Object.values(this.data);
  if (rows.length === 0) return;

  const profits = rows.map(t => t.profit);
  const max = Math.max(...profits);
  const min = Math.min(...profits);

  [...this.tbody.children].forEach((tr, i) => {
    const p = rows[i].profit;
    let color = "#ccc"; // mặc định (hòa)

    if (p === 0) color = "#999";
    else if (p === max && p > 0) color = "#b400ff";        // trần
    else if (p === min && p < 0) color = "#0066ff";        // sàn
    else if (p > 0) {
      color = p > max * 0.7 ? "#008000" : "#00aa00";       // lãi mạnh / nhẹ
    } else {
      color = p < min * 0.7 ? "#8b0000" : "#ff3333";       // lỗ mạnh / nhẹ
    }

    // áp dụng cho cột lãi
    tr.cells[6].style.color = color;

    // nếu muốn tô cả dòng (bỏ comment)
    tr.style.backgroundColor = color + "20";
  });
},

  // 🖌 Render bảng
  render() {
    this.tbody.innerHTML = "";
    let total = 0;

    Object.values(this.data)
      .slice(-this.maxRows)
      .forEach(t => {
        total += t.profit;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${t.id}</td>
          <td>${t.buy}</td>
          <td>${t.matchBuy}</td>
          <td>${t.sell}</td>
          <td>${t.matchSell}</td>
          <td>${t.market}</td>
          <td style="color:${t.profit >= 0 ? 'green' : 'red'}">
            ${t.profit}
          </td>
        `;
        this.tbody.appendChild(tr);
      });

    document.getElementById("totalProfit").textContent = total;
    this.updateColors()
  }
};




// TradeTable.buy(1, 'mua', 2);
// TradeTable.buy(2, 'ban', 1);

// setTimeout(() => {
//   TradeTable.onMatch(1, 100);
//   TradeTable.onMatch(2, 120);
// }, 500);

// setTimeout(() => {
//   TradeTable.close(1, 'len');
//   TradeTable.close(2, 'xuong');
// }, 3000);


// {
//   "bs": [
//     {
//       "eid": 1,
//       "bc": 490,
//       "b": 1000,
//       "v": 206784100
//     }
//   ],
//   "cmd": 15002
// }