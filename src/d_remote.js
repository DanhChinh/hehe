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

    let parent = document.getElementById('DOM_map');
    if (parent.innerHTML.trim() === "") {
      data.forEach((e, i) => {
        parent.innerHTML += `
        <div class="container my-3">
  <div class="row g-3 align-items-stretch">
    
    <!-- Left info -->
    <div class="col-md-2">
      <div class="border rounded p-2 h-100">

        <!-- Name -->
        <div class="d-flex justify-content-between mb-2">
          <span class="fw-semibold">Name:</span>
          <span id="DOM_name_${i}">${e.name}</span>
        </div>

        <!-- Predict -->
        <div class="d-flex justify-content-between mb-2">
          <span class="fw-semibold">Predict:</span>
          <span id="DOM_predict_${i}" class="text-primary"></span>
        </div>

        <!-- Signal -->
        <div class="d-flex justify-content-between mb-2">
          <span class="fw-semibold">Signal:</span>
          <span id="DOM_signal_${i}" class="text-success"></span>
        </div>

        <!-- Value -->
        <div class="d-flex justify-content-between align-items-center">
          <span class="fw-semibold">Value:</span>
          <input 
            id="DOM_value_${i}" 
            type="text" 
            class="form-control form-control-sm w-50"
            placeholder="Enter"
          />
        </div>

      </div>
    </div>

    <!-- Middle -->
    <div class="col-md-6">
      <div id="hsFix_${i}" class="border rounded chart-box"></div>
    </div>

    <!-- Right chart -->
    <div class="col-md-4">
      <div id="chart_long_${i}" class="border rounded chart-box"></div>
    </div>

  </div>
</div>
        `
      })
    }

    data.forEach((d, i) => {
      let best_match = d.best_match
      drawLineChart(
        document.getElementById(`hsFix_${i}`),
        best_match.history_fix_cumsum
      )
      drawChartLong(
        document.getElementById(`chart_long_${i}`),
        best_match.local_data,
        best_match.local_start_index,
        best_match.match_data_local,
        best_match.predicted_data_local,
        best_match.best_index,
        best_match.trend
      );
    });

    if (!sid) {
      return
    }

    let buy = 0;
    let sell = 0;

    data.forEach((d, i) => {
      // let name = d.name;
      let predict_fix = d.predict_fix;
      let signal = d.signal;
      document.getElementById(`DOM_predict_${i}`).innerText= predict_fix;
      document.getElementById(`DOM_signal_${i}`).innerText= signal;

      let value = +document.getElementById(`DOM_value_${i}`).value * 1000;
      if (predict_fix && signal && value) {

        if (predict_fix == 1) {
          buy += value
        } else if (predict_fix == 2) {
          sell += value
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
      // sendMessageToGame(buy-sell, msg.sid, 1)

    } else {
      TradeTable.sell(msg.sid, sell - buy);
      TradeTable.matchSell(msg.sid, sell - buy)
      // sendMessageToGame(sell-buy, msg.sid, 2)

    }

  })


};




