const main_text = `
    <div class="row g-4">

    <div class="col-lg-3 d-flex flex-column gap-2">
        
        <div class="card shadow-sm has-close-btn" style="min-height: 160px;">
            <div class="card-header fw-bold">
                💬 Tin nhắn mới
            </div>
            <ul class="list-group list-group-flush flex-grow-1" id="chat-container">
                </ul>
            <div class="card-footer text-center">
                <a href="#" class="text-decoration-none">Xem tất cả</a>
            </div>
        </div>

        <div class="card has-close-btn p-2">
            <div class="card-body p-0">
                <canvas id="candleChart" height="120"></canvas>
            </div>
            <div class="progress w-100" style="height: 4px;">
                <div class="progress-bar bg-success" role="progressbar" style="width: 75%;" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        </div>


        <div class="card p-3 has-close-btn">
            <div class="d-flex justify-content-between align-items-center w-100">
                <button type="button" id="toggleBtn" class="btn btn-sm btn-outline-secondary px-3">
                    Testing
                </button>
                <button id="mgs_As_gold" class="btn btn-sm btn-warning fw-bold text-dark px-3">
                    0
                </button>
            </div>
        </div>

        <div class="card has-close-btn p-0"> 
            <div class="table-responsive">
                <table id="tradeTable" class="table table-sm table-borderless m-0">
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
                    <tbody>
                        </tbody>
                </table>
            </div>
        </div>

        <div class="dont_touch_parent">
            <div class="dont_touch border-loop is-draggable bg_red">
                <span>DYOR</span>
            </div>
            <div class="dont_touch border-loop is-draggable bg_blue">
                <span>Volatile</span>
            </div>
        </div>

    </div>


    <div class="col-lg-9">
        <div class="container-fluid p-0 mb-3" id="DOM_dashboard"></div>
        <div class="container-fluid p-0" id="DOM_map"></div>
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


const btn = document.getElementById("toggleBtn");
btn.onclick = () => {
  isPlay = !isPlay;
  btn.classList.toggle("btn-outline-success");
  btn.innerText= isPlay ? "Playing" : "Testing";
};

