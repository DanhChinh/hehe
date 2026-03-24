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
    data.forEach(d => {
      let best_matchs = d.best_matchs
    drawLineChart(

    )      continue
      
    });
    // calculateAndPlot(msg.best_matchs)

  })

  socket_io.on("handle_predict", (msg) => {

    // sendMessageToGame(value, msg.sid, predict)
    let buy = 0;
    let sell = 0;
    for (let i = 0; i < numOfModel; i++) {
      let predict = msg.predicts[i];
      let signal = msg.signals[i]
      let value = +DOM_values[i].value * 1000;
      if(!signal){
        return;
      }
      console.log(signal)
      DOM_predicts[i].innerText = predict;
      if (predict == 1) {
        buy += value
      }
      else if (predict == 2) {
        sell += value

      } else {

      }
      
    }

    if(buy == sell){
      return
    }
    if (buy > sell){
      TradeTable.buy(msg.sid, buy- sell);
      TradeTable.matchBuy(msg.sid, buy- sell)
    // sendMessageToGame(buy-sell, msg.sid, 1)

    }else{
            TradeTable.sell(msg.sid, sell-buy);
      TradeTable.matchSell(msg.sid, sell-buy)
    // sendMessageToGame(sell-buy, msg.sid, 2)

    }
  });
};




