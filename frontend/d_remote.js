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
      // const position = d.position;
      const is_good = d.is_good;
      const confidence = d.confidence;
      if (is_good && volume) {

        if (predict == 1) {
          buy += volume * confidence;
        } else if (predict == 2) {
          sell += volume * confidence;
        } else {

        }

      }
    })
    if (buy == sell) {
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
                            <th>Predict</th>
                            <th>Good</th>
                            <th>Confidence</th>
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
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td>
                                <input id="volume_${i}" type="number" class="form-control form-control-sm text-center" value = "1">
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

      row.cells[1].innerText = d.predict;
      row.cells[1].className = d.predict === 1 ? "text-primary" : (d.predict === 2 ? "text-danger" : "text-muted");

      row.cells[2].innerText = d.is_good ? "GOOD" : "BAD";
      row.cells[2].className = d.is_good ? "text-success fw-bold" : "text-danger fw-bold";

      row.cells[3].innerText = (d.confidence * 100).toFixed(1) + "%";
      row.cells[3].className = d.confidence >= 0.8 ? "text-success fw-bold" : (d.confidence >= 0.5 ? "text-warning fw-bold" : "text-danger fw-bold");

      row.cells[4].innerText = d.position;
      row.cells[4].className = d.position === "BUY" ? "text-primary fw-semibold" : (d.position === "SELL" ? "text-danger fw-semibold" : "text-muted fw-semibold");

      row.cells[5].innerText = d.stop_loss;
      row.cells[6].innerText = d.price;
      row.cells[7].innerText = d.take_profit;


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
    drawLineChart(
      document.getElementById(`hsFix_${i}`),
      d.history_cumsum,
      d.name
    )
  });
}