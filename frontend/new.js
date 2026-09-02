class PlayerManager {
  constructor() {
    this._name = "___";
    this._gold = 0;
    this._bet = 0;
    this._tp = 10000000;
    this._sl = 0;
    this._isPlay = false;
    this._playHistory = [];
    this._signal = "HOLD";
    this._isReverse = false;
  }

  getProperty(prop) {
    return this[prop];
  }

  setProperty(prop, value) {
    console.log(`player.setProperty[${prop}]: ${value}`)
    if (this[prop] !== value) {
      this[prop] = value;
      this.updateUI(prop);
    }
  }

  updateUI(prop) {
    const value = this[prop];
    document.querySelectorAll(`[data-prop="${prop}"]`).forEach((el) => {
      if (el.tagName === "INPUT" && el.type === "checkbox") {
        el.checked = value;
      } else if (el.tagName === "INPUT") {
        el.value = value;
      } else if (prop === "_playHistory") {
        el.innerHTML =
          value.length > 0 ? value.join("<br>") : "Chưa có lịch sử";
      } else if (prop === "_signal") {
        el.innerText = value;
        el.style.backgroundColor =
          value === "BUY"
            ? "#26a69a"
            : value === "SELL"
              ? "#ef5350"
              : "#2962ff";
      } else {
        if (isNumeric(value)) {
          el.innerText = formatNumber(value)
        }
        else {
          el.innerText = value;

        }
      }
    });
  }
}

class SystemManager {
  constructor() {
    this._token = null;
    this._isGameConnected = false;
    this._isPythonConnected = false;
    this._responseCount = 0;
    this._messages = "";
    this.socket = undefined;
    this.socket_io = undefined;
    this.counter_send = 0;
    this.reconnectCount = 0;
    this._history = "";
    this.sendInterval = undefined;
    // this.sid = undefined;
  }

  getProperty(prop) {
    return this[prop];
  }

  setProperty(prop, value) {
    if(prop!="_responseCount"){console.log(`system.setProperty[${prop}]: ${value}`)}

    if (this[prop] !== value) {
      this[prop] = value;
      this.updateUI(prop);
    }
  }

  updateUI(prop) {
    const value = this[prop];
    document.querySelectorAll(`[data-prop="${prop}"]`).forEach((el) => {
      if (el.tagName === "INPUT" && el.type === "checkbox") {
        el.checked = value;
      } else if (el.tagName === "INPUT") {
        el.value = value;
      } else if (prop === "_messages") {
        el.innerText = value? value : "Chưa có tin nhắn";
      } else {
        el.innerText = value;
      }
    });
  }
}
var initRecord = (
  sid = undefined,
  progress = [],
  d1 = undefined,
  d2 = undefined,
  d3 = undefined,
) => {
  return { sid, progress, d1, d2, d3 };
};
var record = initRecord();

var player = new PlayerManager();
var system = new SystemManager();

var managers = [player, system];

loadAccessToken().then((token) => {
  if (token) {
    system._token = token;
    system.updateUI("_token");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-prop]").forEach((el) => {
    const propName = el.getAttribute("data-prop");
    const manager = managers.find((m) => m.hasOwnProperty(propName));
    if (!manager) return;

    const value = manager.getProperty(propName);

    if (el.tagName === "INPUT" && el.type === "checkbox") {
      el.checked = value;
    } else if (el.tagName === "INPUT") {
      el.value = value;
    } else if (propName === "_playHistory" || propName === "_messages") {
      el.innerHTML =
        value.length > 0
          ? value.join("<br>")
          : propName === "_playHistory"
            ? "Chưa có lịch sử"
            : "Chưa có tin nhắn";
      if (propName === "_messages") el.scrollTop = el.scrollHeight;
    } else if (propName === "_signal") {
      el.innerText = value;
      el.style.backgroundColor =
        value === "BUY" ? "#26a69a" : value === "SELL" ? "#ef5350" : "#2962ff";
    } else {
      el.innerText = value;
    }
  });
});

function handleInputChange(input) {
  const propName = input.getAttribute("data-prop");
  const manager = managers.find((m) => m.hasOwnProperty(propName));
  const smallEl = input.parentElement.querySelector("small");
  if (manager) {
    const val = input.type === "number" ? Number(input.value) : input.value;
    manager.setProperty(propName, val);
  }
  if (smallEl) {
    smallEl.innerText = formatNumber(input.value);
  }
}

function simulateIncomingMessage(msgText) {
  system.setProperty(
    "_responseCount",
    system.getProperty("_responseCount") + 1,
  );
  const currentMessages = system.getProperty("_messages");
  system.setProperty("_messages", [
    ...currentMessages,
    `[${new Date().toLocaleTimeString()}] ${msgText}`,
  ]);
}

function handleToggleChange(checkbox) {
  const propName = checkbox.getAttribute("data-prop");
  const manager = managers.find((m) => m.hasOwnProperty(propName));
  if (!manager) return;
  const isChecked = checkbox.checked;

  if (propName === "_isPythonConnected") handlePythonConnected(isChecked);
  if (propName === "_isGameConnected") handleGameConnected(isChecked);
  if (propName === "_isReverse"){
    player.setProperty("_isReverse", isChecked);
    system.socket_io.emit("toggle_reverse", { isReverse: isChecked });
  }
  if (propName === "_isPlay"){
    player.setProperty("_isPlay", isChecked);
    system.socket_io.emit("toggle_play", { isPlay: isChecked });
  }
}
function handleGameConnected(isChecked) {
  if (!isChecked) {
    //
    return;
  }
  system.socket = new WebSocket(MESSAGE_WS.url);

  system.socket.onopen = function (event) {
    if (Swal.isVisible()) {
        Swal.close();
    }
    let token = system.getProperty("_token");
    system.setProperty("reconnectCount", 0);
    system.socket.send(JSON.stringify(MESSAGE_WS.login(token)));
    system.setProperty("_messages", `socket.send: ${token}}`);
  };

  system.socket.onmessage = async function (event) {
    let mgs = JSON.parse(event.data)[1];

    if (typeof mgs === "object") {
      //betting
      if (mgs.cmd === 15007) {
        system.setProperty("_responseCount", record.progress.length);

        record.progress.push(JSON.parse(JSON.stringify(mgs.bs)));

        if (record.progress.length === 30) {
          system.socket_io.emit("predict", {
            sid: record.sid,
            progress: JSON.stringify(record.progress),
          });
        }
        return;
      }
      //ending
      if (mgs.cmd === 15006) {
        record.sid = mgs.sid;
        record.d1 = mgs.d1;
        record.d2 = mgs.d2;
        record.d3 = mgs.d3;
        insertDatabase(JSON.parse(JSON.stringify(record)));
        let rs = mgs.d1 + mgs.d2 + mgs.d3 > 10 ? 1 : 2;
        TradeTable.close(record.sid, rs);
        player.setProperty("_bet", 0);

        system.setProperty("_history", system.getProperty("_history") + rs);
        system.socket_io.emit("check", {
          sid: record.sid,
          rs: rs,
        });

        return;
      }
      //start
      if (mgs.cmd === 15005) {
        record = initRecord();
        record.sid = mgs.sid;
        return;
      }
      //sended
      if (mgs.cmd === 15002) {
        mgs.bs.forEach((element) => {
          if (element.eid == 1) {
            TradeTable.matchBuy(record.sid, element.b);
          } else {
            TradeTable.matchSell(record.sid, element.b);
          }
        });
        return;
      }

      if (mgs.cmd === 100) {
        player.setProperty("_name", mgs.dn);
        player.setProperty("_gold", mgs.As.gold);
        system.setProperty("_isGameConnected", true);
        return;
      }
    } else {
      if (mgs === true) {
        system.socket.send(JSON.stringify(MESSAGE_WS.info));
        system.setProperty("_messages", "JSON.stringify(MESSAGE_WS.info)");
        setTimeout(() => {
          system.sendInterval = setInterval(() => {
            system.socket.send(
              JSON.stringify(MESSAGE_WS.result(system.counter_send)),
            );
            system.counter_send++;
          }, 5000);
        }, 5000);
      }
    }
  };

  system.socket.onclose = function (event) {
    system.setProperty("_messages", "socket.onclose");
    system.setProperty("_isGameConnected", false);
    Swal.fire({
        icon: 'error',
        title: 'Mất Kết Nối Server!',
        text: 'Đang thử kết nối lại...',
        showConfirmButton: true, // Ẩn nút OK để tự động xử lý
        allowOutsideClick: false   // Không cho tắt khi bấm ra ngoài
    });
    clearInterval(system.sendInterval);
    if (system.reconnectCount >= 2) {
      alert("Đã vượt quá số lần reconnect cho phép");
      return;
    }

    system.reconnectCount++;
    setTimeout(() => {
      system.counter_send = 0;
      system.socket_connect();
    }, 1000);
  };

  system.socket.onerror = function (error) {
    console.error("Lỗi WebSocket:", error);
  };
}

function handlePythonConnected(isChecked) {
  if (!isChecked) {
    system.socket_io.close();
    return;
  }
  if (!system.socket_io) {
    system.socket_io = io("http://localhost:5000");

    system.socket_io.on("connect", () => {
      system.setProperty("_isPythonConnected", true);
    });

    system.socket_io.on("info", (msg) => {
      let sid = msg.sid;
      let data = msg.data;
      console.log(data)

      // LOGIC TỰ ĐỘNG NGẮT KHI CHẠM TP/SL
      if (player._isPlay) {

        const TP = player.getProperty("_tp");
        const SL = player.getProperty("_sl");
        const gold = player.getProperty("_gold");

        if (gold >= TP || gold <= SL) {
          player.setProperty("_isPlay", false);
        }
      }


      // updateChart(data.history_tm);
      // updateRawScoreChart(data.history_mm);
      renderMultipleCharts(data);

      //kiem tra dieu kien de gui lenh mua ban

      if (!sid || !player.getProperty("_isPlay") || !data.predict){
        player.setProperty("_signal", 'HOLD');
        return;
      }
      player.setProperty("_signal", data.predict == 1 ? "BUY" : "SELL");

      //end

      let money = roundToThousand(
        data.bet * +document.getElementById("_volume").value,
      );

      sendMessageToGame(money, sid, data.predict);
      data.predict == 1
        ? TradeTable.buy(sid, money)
        : TradeTable.sell(sid, money);
      player.setProperty("_bet", money);
    });

    system.socket_io.on("disconnect", () => {
      system.setProperty("_isPythonConnected", false);
    });
  }
}

