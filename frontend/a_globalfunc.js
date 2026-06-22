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
    while (chatBox.children.length > 3) {
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

function getBgColor(value, rangeNumber) {
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
        g = Math.round(255 * (1 - t) + 100 * t);
        b = Math.round(255 * (1 - t));
    }

    return `rgb(${r}, ${g}, ${b})`;
}

function getTextColor(value) {
    return value < 0 ? "#fff" : "#000";
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


    if (thiTruong === "↑") {
      t.profit = 0.97*t.matchBuy - t.matchSell;
    } else {
      t.profit = 0.97*t.matchSell-t.matchBuy;
    }

    (isPlay ? mgs_As_gold += t.profit:null)

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

  const rangeNumber = Math.max( Math.abs(max), Math.abs(min));

  [...this.tbody.children].forEach((tr, i) => {
    const p = rows[i].profit;
    tr.style.setProperty('background-color', getBgColor(p, rangeNumber), 'important');
    tr.style.setProperty('color', getTextColor(p), 'important');
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

    this.updateColors()

  }
};


const formatNumber = (amount, locale = 'vi-VN') => {
  return new Intl.NumberFormat(locale, {
    style: 'decimal',
    minimumFractionDigits: 0, // Số chữ số thập phân tối thiểu
    maximumFractionDigits: 0  // Số chữ số thập phân tối đa
  }).format(amount/1000);
};

var mgs_As_gold = 0;




  document.addEventListener("DOMContentLoaded", () => {
    
    // ==========================================
    // KHỐI 1: XỬ LÝ NÚT X (ẨN/HIỆN CHUNG)
    // ==========================================
    const closeBtnDivs = document.querySelectorAll('.has-close-btn');
    closeBtnDivs.forEach(div => {
      // Tự động tạo nút X
      const closeBtn = document.createElement('span');
      closeBtn.className = 'global-close-btn';
      closeBtn.innerHTML = '';
      div.appendChild(closeBtn);

      // Click nút X để toggle ẩn/hiện
      closeBtn.addEventListener('click', (event) => {
        event.stopPropagation(); // Ngăn chặn sự kiện lan ra ngoài
        div.classList.toggle('content-blinded');
      });
    });


    // ==========================================
    // KHỐI 2: XỬ LÝ KÉO THẢ ĐỘC LẬP (.is-draggable)
    // ==========================================
    const draggableDivs = document.querySelectorAll('.is-draggable');
    draggableDivs.forEach(div => {
      let isDragging = false;
      let offsetX, offsetY;

      const startDrag = (e) => {
        // NẾU CLICK TRÚNG NÚT X THÌ HỦY LỆNH KÉO (Quan trọng để không bị xung đột)
        if (e.target.classList.contains('global-close-btn')) return;

        isDragging = true;

        const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
        const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;

        const rect = div.getBoundingClientRect();
        offsetX = clientX - rect.left;
        offsetY = clientY - rect.top;

        // Chuyển vị trí sang fixed để di chuyển tự do trên màn hình
        div.style.position = 'fixed';
        div.style.margin = '0';
        div.style.left = `${rect.left}px`;
        div.style.top = `${rect.top}px`;
      };

      const doDrag = (e) => {
        if (!isDragging) return;
        
        const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
        const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;

        let newLeft = clientX - offsetX;
        let newTop = clientY - offsetY;

        // Giới hạn trong viền màn hình
        if (newLeft < 0) newLeft = 0;
        if (newTop < 0) newTop = 0;
        if (newLeft + div.offsetWidth > window.innerWidth) newLeft = window.innerWidth - div.offsetWidth;
        if (newTop + div.offsetHeight > window.innerHeight) newTop = window.innerHeight - div.offsetHeight;

        div.style.left = `${newLeft}px`;
        div.style.top = `${newTop}px`;
      };

      const stopDrag = () => {
        isDragging = false;
      };

      // Đăng ký sự kiện Máy tính (Mouse)
      div.addEventListener('mousedown', startDrag);
      document.addEventListener('mousemove', doDrag);
      document.addEventListener('mouseup', stopDrag);

      // Đăng ký sự kiện Điện thoại (Touch)
      div.addEventListener('touchstart', startDrag, { passive: true });
      document.addEventListener('touchmove', doDrag, { passive: false });
      document.addEventListener('touchend', stopDrag);
    });

  });
