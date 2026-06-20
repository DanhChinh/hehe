const main_text = `
    <div class="row g-4">

        <!-- ================= MESSAGES ================= -->
        <div class="col-lg-3">
            <div class="card shadow-sm" style="height:160px">
                <div class="card-header fw-bold">
                    💬 Tin nhắn mới
                </div>

                <ul class="list-group list-group-flush" id="chat-container">

                    <div class="card-footer text-center">
                        <a href="#" class="text-decoration-none">Xem tất cả</a>
                    </div>
            </div>
                            <div class="card-body">
                                <canvas id="candleChart" height="120"></canvas>
                            </div>

                            <div class="progress col-md-12" style="height: 3px; margin:10px; width: 97%">
                                <div class="progress-bar bg-success" role="progressbar" aria-valuenow="" aria-valuemin="0"
                                    aria-valuemax="55"></div>
                            </div>

            
            <div class="my-3">                
              <button type="button" id="toggleBtn" class="btn btn-outline-secondary ">
              Testing
              </button>
              <button type="button" id="toggleBtnShow" class="btn btn-outline-secondary">
              Hidden
              </button>
              <button id="mgs_As_gold"  class="btn btn btn-light">
              0
              </button>

            </div>
            <table border="1" width="100%" id="tradeTable" >
            <thead>
            <tr>
            <th>Id</th>
            <th>Buy</th>
            <th>Match</th>
            <th>Sell</th>
            <th>Match</th>
            <th>Market</th>
            <th>Sessionp</th>
            <th>Netp</th>
            </tr>
            </thead>
            <tbody></tbody>
            </table>

            
            


        </div>




        <!-- ================= CHARTS ================= -->
        <div class="col-lg-9">
                <div class="col-md-12">
                    <div class="card shadow-sm">
                        <div class="card-header fw-bold">
                            📈 Lưu lượng mô hình
                        </div>

                        <div class="card-body container" id="DOM_dashboard"></div>
                        <div class="card-body container" id="DOM_map"></div>
                    </div>
                </div>
        </div>
    </div>

`

document.getElementsByTagName('main')[0].innerHTML = main_text;











function buildCandles(arr) {
  if (arr.length === 0) return [];

  const candles = [];
  let current = arr[0];
  let count = 1;

  for (let i = 1; i < arr.length; i++) {
    if (arr[i] === current) {
      count++;
    } else {
      candles.push({
        type: current === 1 ? 'up' : 'down',
        length: count
      });
      current = arr[i];
      count = 1;
    }
  }

  candles.push({
    type: current === 1 ? 'up' : 'down',
    length: count
  });

  return candles;
}

// Chart
let candleChart;
let _Candle = [];

function drawCandleChart(dataArr) {
  const candles = buildCandles(dataArr);
  const candlesSlice = candles.slice(-10);

  const labels = candlesSlice.map((_, i) => `${i + 1}`);
  const values = candlesSlice.map(c => c.length);
  const colors = candlesSlice.map(c =>
    c.type === 'up' ? '#212121' : '#a29bfe'
  );

  // 🚀 TỐI ƯU: Nếu chart đã tồn tại, chỉ cập nhật data và render lại
  if (candleChart) {
    candleChart.data.labels = labels;
    candleChart.data.datasets[0].data = values;
    candleChart.data.datasets[0].backgroundColor = colors;
    
    // 'none' giúp cập nhật ngay lập tức, không tốn CPU chạy hiệu ứng co giãn (animation)
    candleChart.update('none'); 
    return;
  }

  // Khởi tạo lần đầu tiên nếu chưa có chart
  candleChart = new Chart(
    document.getElementById('candleChart'),
    {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Candlestick Strength',
            data: values,
            backgroundColor: colors,
            borderRadius: 4,
            categoryPercentage: 1.0,
            barPercentage: 1.0
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { display: false }
          },
          y: {
            beginAtZero: true,
            grid: { color: '#eee' }
          }
        }
      }
    }
  );
}

function addCandleValue(v) {
  _Candle.push(v);
  drawCandleChart(_Candle);
}

// init
drawCandleChart(_Candle);





var isPlay = false;
var isShow = true;

const btn = document.getElementById("toggleBtn");
const btnShow = document.getElementById("toggleBtnShow");
const tradeTable = document.getElementById("tradeTable");

btn.onclick = () => {
  isPlay = !isPlay;
  btn.classList.toggle("btn-outline-success");
  btn.innerText= isPlay ? "Playing" : "Testing";
};

btnShow.onclick = () => {
  isShow = !isShow;
  tradeTable.classList.toggle("to_left");
  btnShow.innerText = isShow ? "Hidden" : "Show";
}