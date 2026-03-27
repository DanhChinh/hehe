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
                            
            
            <table border="1" width="100%" id="tradeTable">
            <thead>
            <tr>
            <th>Mã</th>
            <th>Mua</th>
            <th>Khớp</th>
            <th>Bán</th>
            <th>Khớp</th>
            <th>Thị trường</th>
            <th>Lãi</th>
            <th>Tổng</th>
            </tr>
            </thead>
            <tbody></tbody>
            </table>
            


        </div>




        <!-- ================= CHARTS ================= -->
        <div class="col-lg-9">
                <div class="col-12" id="meanmodel" style="height: 350px;"></div>


                <div class="col-md-12">
                    <div class="card shadow-sm">
                        <div class="card-header fw-bold">
                            📈 Thống kê truy cập
                        </div>
                        <div class="card-body container" id="DOM_map">
                        </div>
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
Chart
let candleChart;
let _Candle = [];

function drawCandleChart(dataArr) {
  const candles = buildCandles(dataArr);

  const candlesSlice = candles.slice(-10);

  const labels = candlesSlice.map((_, i) => `${i + 1}`);

  // ✅ TẤT CẢ GIÁ TRỊ DƯƠNG
  const values = candlesSlice.map(c => c.length);

  const colors = candlesSlice.map(c =>
    c.type === 'up' ? '#212121' : '#a29bfe'
  );

  if (candleChart) candleChart.destroy();

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

            // optional styling
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
            grid: {
              display: false
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: '#eee'
            }
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