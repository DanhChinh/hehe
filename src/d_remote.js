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
    console.log(msg.data)
    // updateTable(msg.data)
    let sid = msg.sid;
    let data = msg.data;

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
      const position = d.position
      if (predict && volume && position) {

        if (predict == 1) {
          buy += volume
        } else if (predict == 2) {
          sell += volume
        } else {

        }

      }
    })
    if (buy == sell) {
      return
    }
    if (buy > sell) {
      TradeTable.buy(msg.sid, buy - sell);
      TradeTable.matchBuy(msg.sid, buy - sell)
      // sendMessageToGame(buy - sell, msg.sid, 1)

    } else {
      TradeTable.sell(msg.sid, sell - buy);
      TradeTable.matchSell(msg.sid, sell - buy)
      // sendMessageToGame(sell - buy, msg.sid, 2)

    }

  })


};




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
  let headText = `    <div class="container mt-4">
        <div class="card shadow-sm">

            <!-- Header -->
            <div class="card-header bg-dark text-white">
                <h5 class="mb-0">Trading Dashboard</h5>
            </div>

            <!-- Table -->
            <div class="table-responsive">
                <table id="Trading_Dashboard" class="table table-bordered table-hover align-middle mb-0 text-center">

                    <thead class="table-light">
                        <tr>
                            <th>Name</th>
                            <th>Trend</th>
                            <th>Position</th>
                            <th>Stop Loss</th>
                            <th>Price</th>
                            <th>Take Profit</th>
                            <th>Volume</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody id="tableBody">
                        <!-- Row mẫu -->`

  let footText = `</tbody>

                </table>
            </div>

        </div>
    </div>`
  let mainText = ``
  data.forEach((d, i) => {

    mainText += `                        
                        <tr>
                            <td>${d.name}</td>
                            <td class="text-primary"></td>
                            <td class="text-success fw-bold"></td>
                            <td></td>
                            <td class="fw-semibold"></td>
                            <td></td>
                            <td>
                                <input id="volume_${i}" type="number" class="form-control form-control-sm text-center" >
                            </td>
                            <td>
                              <button id="btn_toggle_${i}"
                                class="btn btn-sm btn-success"
                                data-index="${i}"
                                    data-name="${d.name}">
                              BUY
                            </button>
                          </td>
                        </tr>`

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
  let text = `<div class="row">`
  data.forEach((e, i) => {
    text += `<div class="col-6">
    <div id="hsFix_${i}" class="border rounded chart-box"></div>
              </div>
        
        `
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
      row.cells[0].innerText = d.name;

      // Index 1: Predict (1 = BUY, 2 = SELL, khác = WAIT)
      // let predictText = d.predict === 1 ? "BUY" : (d.predict === 2 ? "SELL" : "WAIT");
      row.cells[1].innerText = d.predict;
      row.cells[1].className = d.predict === 1 ? "text-primary" : (d.predict === 2 ? "text-danger" : "text-muted");

      // Index 2: Position
      row.cells[2].innerText = d.position;
      // Đổi màu theo trạng thái Position
      if (d.position === "BUY") row.cells[2].className = "text-success fw-bold";
      else if (d.position === "SELL") row.cells[2].className = "text-danger fw-bold";
      else row.cells[2].className = "text-secondary fw-bold";

      // Index 3: Stop Loss
      row.cells[3].innerText = d.stop_loss;

      // Index 4: Price
      row.cells[4].innerText = d.price;

      // Index 5: Take Profit
      row.cells[5].innerText = d.take_profit;

      // Index 6: Volume (Input - KHÔNG cập nhật giá trị từ data vào đây để tránh đè lên người dùng)
      // Nếu bạn muốn cập nhật volume LẦN ĐẦU TIÊN thì dùng:
      // let volInput = document.getElementById(`volume_${i}`);
      // if (volInput && volInput.value === "") volInput.value = d.volume;


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
}

function capNhatMap(data) {
  data.forEach((d, i) => {
    let best_match = d.best_match
    drawLineChart(
      document.getElementById(`hsFix_${i}`),
      best_match.history_fix_cumsum,
      d.name
    )
  });
}