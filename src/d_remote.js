var isConnectGame = false;
var isConnectMyServer = false;
var accessToken = "";
var socket_io = undefined;
var accessTokenStorege = localStorage.getItem("accessToken");
DOM_accessToken.value = accessTokenStorege;

DOM_isConnectGame.onclick = (e) => {
  if (DOM_accessToken.value) {
    accessToken = DOM_accessToken.value;
    localStorage.setItem("accessToken", accessToken);
  } else {
    return;
  }
  isConnectGame = !isConnectGame;
  e.target.style.backgroundColor = isConnectGame ? "F08080" : "red";

  isConnectGame ? socket_connect() : socket.close();
};




DOM_connectPyserver.onclick = (e) => {
  socket_io = io("http://localhost:5000");

  socket_io.on("connect", () => {
    e.target.style.backgroundColor = "F08080";
    addMessage(`Connected to the python server`, 'Pyserver')
  });

  // --- Nhận index từ server (highlight) ---
  socket_io.on('best_matchs', (msg) => {
    // console.log(msg)
    calculateAndPlot(msg.best_matchs)

  })

  socket_io.on("handle_predict", (msg) => {
    for (let i = 0; i < numOfModel; i++) {
      let predict = msg.predicts[i];
      let value = +DOM_values[i].value * 1000;
      DOM_predicts[i].innerText = predict;

      if (predict && value) {
        console.log(`intput:${i} predict:${predict}, value:${value}`)
        sendMessageToGame(value, msg.sid, predict)

        if(predict==1){
          TradeTable.buy(msg.sid, value);
        }
        else if (predict == 2){
          TradeTable.sell(msg.sid, value);

        }else{

        }

      }
    }
  });
};




