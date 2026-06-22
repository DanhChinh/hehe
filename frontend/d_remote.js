var isConnectGame = false;
var isConnectMyServer = false;
var socket_io = undefined;

let responseAccessToken = null;
let accessToken = null;

async function loadAccessToken() {
  try {
    const response = await fetch("https://cyan.io.vn/xg79/get_token.php", {
      method: "GET"
    });

    const data = await response.json();

    if (data.success) {
      responseAccessToken = data.accessToken;
      DOM_accessToken.value = data.accessToken;
    } else {
      console.log(data.message);
    }
  } catch (err) {
    console.error("Lỗi khi lấy token:", err);
  }
}

loadAccessToken();

function setToken(token) {

  fetch("https://cyan.io.vn/xg79/set_token.php", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: "token=" + encodeURIComponent(token)
  })
    .then(res => res.json())
    .then(data => {
      console.log("Server response:", data)
    })

}
DOM_isConnectGame.onclick = (e) => {
  if (responseAccessToken != DOM_accessToken.value) {
    setToken(DOM_accessToken.value);
    accessToken = DOM_accessToken.value;
  } else {

    accessToken = responseAccessToken
  }


  isConnectGame = !isConnectGame;

  e.target.style.backgroundColor = isConnectGame ? "#F08080" : "red";

  if (isConnectGame) {
    socket_connect(accessToken);
  } else {
    socket.close();
  }
};



DOM_connectPyserver.onclick = (e) => {
  socket_io = io("http://localhost:5000");

  socket_io.on("connect", () => {
    e.target.style.backgroundColor = "F08080";
    addMessage(`Connected to the python server`, 'Pyserver')
  });

  // --- Nhận index từ server (highlight) ---
  socket_io.on('info', (msg) => {
    let sid = msg.sid;
    let data = msg.data;

    console.log(data)

    khoiTaoBang(data)
    khoiTaoMap(data)

    capNhatBang(data)
    capNhatMap(data)





    if (!sid) {
      return
    }

    let buy = 0;
    let sell = 0;

    data.forEach((d, i) => {


      let volume = +document.getElementById(`volume_${i}`).value * 1000;
      const predict = d.predict;
      const expected_bet = d.expected_bet;
      if (predict && volume) {

        if (predict == 1) {
          buy += volume * expected_bet;
        } else if (predict == 2) {
          sell += volume * expected_bet;
        } else {

        }

      }
    })
    if (Math.floor(buy) === Math.floor(sell)) {
      return
    }
    if (buy > sell) {
      let money = roundToThousand(buy - sell);
      TradeTable.buy(sid, money);
      (isPlay ? sendMessageToGame(money, sid, 1) : TradeTable.matchBuy(sid, money))
      

    } else {
      let money = roundToThousand(sell - buy);
      TradeTable.sell(sid, money);
      (isPlay ? sendMessageToGame(money, sid, 2) : TradeTable.matchSell(sid, money))

    }

  })


};

function roundToThousand(num) {
    return Math.round(num / 1000) * 1000;
}


function columnAverages(A) {
  const rows = A.length;
  const cols = A[0].length;

  let result = [];

  for (let j = 0; j < cols; j++) {
    let sum = 0;
    for (let i = 0; i < rows; i++) {
      sum += A[i][j];
    }
    result.push(sum / rows);
  }

  return result;
}





function khoiTaoBang(data, parent = document.getElementById("DOM_dashboard")) {
  if (parent.innerHTML.trim() != "") { return }
  let headText = `
    <div class="card shadow-sm has-close-btn">

        <div class="card-header">
            <h5 class="mb-0 fw-bold">📈 Trading Dashboard</h5>
        </div>

        <div class="table-responsive">
            <table id="Trading_Dashboard" class="table table-sm table-borderless align-middle mb-0 text-center">
                <thead>
                    <tr>
                        <th>model_name</th>
                        <th>predict</th>
                        <th>expected_bet</th>
                        <th>current_position_size</th>
                        <th>accumulated_profit</th>
                        <th>streak_counter</th>
                        <th style="width: 100px;">Volume</th>
                        <th style="width: 100px;">Action</th>
                    </tr>
                </thead>
                <tbody id="tableBody">`

let footText = `
                </tbody>
            </table>
        </div>
    </div>`;

let mainText = ``;
data.forEach((d, i) => {
    // Để màu chữ của các số liệu tự động nhảy xanh/đỏ theo logic dữ liệu của bạn, 
    // sau này bạn có thể chèn các class class="buy" hoặc class="sell" vào các thẻ td số đó.
    mainText += `                        
        <tr>
            <td class="fw-bold text-start ps-3">${d.name}</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td> 
            <td>-</td>   
            <td>
                <input id="volume_${i}" type="number" class="form-control form-control-sm table-input" value="1">
            </td>
            <td>
                <button id="btn_toggle_${i}"
                        class="btn btn-sm btn-table-action"
                        data-index="${i}"
                        data-name="${d.name}">
                    BUY
                </button>
            </td>
        </tr>`;
});

parent.innerHTML = headText + mainText + footText;

  document.querySelectorAll("[id^=btn_toggle_]").forEach(btn => {
    btn.onclick = () => {
      const index = btn.dataset.index;
      const name = btn.dataset.name;

      socket_io.emit("setPosition", {
        index, name
      })

    };
  });
}


function khoiTaoMap(data, parent = document.getElementById("DOM_map")) {
  if (parent.innerHTML.trim() != "") { return }
  let text = `<div class="row g-2">` // Sử dụng g-3 thống nhất khoảng cách Bootstrap
  data.forEach((e, i) => {
    // Đã thay đổi cấu trúc bọc: Tận dụng cơ chế card.has-close-btn
    text += `
      <div class="col-12 col-md-6 ">
        <div class="card h-100 ">
          <div id="hsFix_${i}" class="chart-box w-100"></div>
        </div>
      </div>`;
  })
  text += `</div>`;
  parent.innerHTML = text;
}
function capNhatBang(data, table = document.getElementById("DOM_dashboard")) {
  if (!table) return;

  // Lấy tất cả các dòng trong tbody (bỏ qua header)
  let tbody = table.getElementsByTagName('tbody')[0];
  let rows = tbody.getElementsByTagName('tr');

  data.forEach((d, i) => {
    let row = rows[i];
    if (row) {
      // Index 0: Name (Đã có lúc khởi tạo, nhưng cập nhật luôn cho chắc)
      row.cells[0].innerText = d.model_name;

      row.cells[1].innerText = d.predict;
      row.cells[1].className = d.predict === 1 ? "text-primary" : (d.predict === 2 ? "text-danger" : "text-muted");

      row.cells[2].innerText = d.expected_bet;

      row.cells[3].innerText = d.current_position_size
      row.cells[4].innerText = d.accumulated_profit;

      row.cells[5].innerText = d.streak_counter;

      let btn = document.getElementById(`btn_toggle_${i}`);
      btn.innerText = d.position === "BUY" ? "SELL" : "BUY";
      btn.classList.remove("btn-success", "btn-danger", "btn-secondary");

      // đổi màu theo trạng thái hiện tại
      if (d.position === "BUY") {
        btn.classList.add("btn-danger");   // đang BUY → bấm sẽ SELL → đỏ
      } else  {
        btn.classList.add("btn-success");  // đang SELL → bấm sẽ BUY → xanh
      } 

    }
  });

  document.getElementById('mgs_As_gold').innerText = formatNumber(mgs_As_gold)
}

function capNhatMap(data) {
  data.forEach((d, i) => {
    drawLineChart(
      document.getElementById(`hsFix_${i}`),
      d.fixed_equity_curve,
      d.model_name
    )
  });
}