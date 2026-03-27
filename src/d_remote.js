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
      let text = `<div class="row">`
      data.forEach((e, i) => {
        text += `<div class="col-6">
                        <div class="container my-3">
                    <div class="row g-3 align-items-stretch">

                        <!-- Left info -->
                        <div class="col-md-3">
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


                                <!-- Position -->
                                <div class="d-flex justify-content-between mb-2">
                                    <span class="fw-semibold">Position:</span>
                                    <span id="DOM_position_${i}" class="text-success"></span>
                                </div>

                                <!-- take_profit -->
                                <div class="d-flex justify-content-between mb-2">
                                    <span class="fw-semibold">Take profit:</span>
                                    <span id="DOM_take_profit_${i}" class="text-success"></span>
                                </div>

                                <!-- Price -->
                                <div class="d-flex justify-content-between mb-2">
                                    <span class="fw-semibold">Price:</span>
                                    <span id="DOM_price_${i}" class="text-success"></span>
                                </div>

                                <!-- stop_loss -->
                                <div class="d-flex justify-content-between mb-2">
                                    <span class="fw-semibold">Stop loss:</span>
                                    <span id="DOM_stop_loss_${i}" class="text-success"></span>
                                </div>   

                                <!-- Volume -->
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="fw-semibold">Volume:</span>
                                    <input id="DOM_volume_${i}" type="text" class="form-control form-control-sm w-50"
                                       value="" />
                                </div>

                            </div>
                        </div>

                        <!-- Middle -->
                        <div class="col-md-9">
                            <div id="hsFix_${i}" class="border rounded chart-box"></div>
                        </div>
                    </div>
                </div>
              </div>
        
        `
      })
      text += `</div>`;
      parent.innerHTML = text;
    }

    let meanmodel = []

    data.forEach((d, i) => {
      let best_match = d.best_match
      meanmodel.push(best_match.history_fix_cumsum)
      drawLineChart(
        document.getElementById(`hsFix_${i}`),
        best_match.history_fix_cumsum
      )
    });

    meanmodel = columnAverages(meanmodel)
    drawLineChart(
      document.getElementById("meanmodel"),
      meanmodel
    )


    if (!sid) {
      return
    }

    let buy = 0;
    let sell = 0;

    data.forEach((d, i) => {
      
      Object.entries(d).forEach(([k, v]) => {
        const el = document.getElementById(`DOM_${k}_${i}`);
        if (el) el.innerText = v;
      });

      let volume = +document.getElementById(`DOM_volume_${i}`).value *1000;
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
