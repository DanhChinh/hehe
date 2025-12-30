const main_text = `
    <div class="row g-4">

        <!-- ================= MESSAGES ================= -->
        <div class="col-lg-4">
            <div class="card shadow-sm" style="height:260px">
                <div class="card-header fw-bold">
                    💬 Tin nhắn mới
                </div>

                <ul class="list-group list-group-flush" id="chat-container">

                    <div class="card-footer text-center">
                        <a href="#" class="text-decoration-none">Xem tất cả</a>
                    </div>
            </div>

            <div class="progress col-md-12" style="height: 3px; margin:10px; width: 97%">
                <div class="progress-bar bg-success" role="progressbar" aria-valuenow="" aria-valuemin="0"
                    aria-valuemax="55"></div>
            </div>

            <table border="1" width="100%" id="tradeTable">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Mua</th>
                        <th>Khớp</th>
                        <th>Bán</th>
                        <th>Khớp</th>
                        <th>Thị trường</th>
                        <th>Lãi</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>

            <p><b>Lợi nhuận:</b> <span id="totalProfit">0</span></p>


        </div>




        <!-- ================= CHARTS ================= -->
        <div class="col-lg-8">
            <div class="row g-4">

                <div class="row g-4">

                
                <!-- Người dùng -->
                <div class="col-lg-6">
                        <div class="card shadow-sm">
                            <div class="card-header fw-bold">
                                👥 Người dùng mới
                            </div>
                            <div class="card-body">
                            <canvas id="userChart" height="120"></canvas>
                            </div>
                        </div>

                        <div class="card shadow-sm mt-3">
                            <div class="card-header fw-bold">
                            💰 Xu hướng thị trường
                            </div>
                            <div class="card-body">
                                <canvas id="candleChart" height="120"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Doanh thu -->
                    <div class="col-lg-6">
                        <div class="card shadow-sm">
                            <div class="card-header fw-bold">
                                🧭 Tỷ trọng doanh thu theo thời gian
                            </div>
                            <div class="card-body">
                                <canvas id="revenueChart" height="120"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                


                <!-- Line Chart -->
                <div class="col-md-12">
                    <div class="card shadow-sm">
                        <div class="card-header fw-bold">
                            📈 Thống kê truy cập
                        </div>
                        <div class="card-body" id="DOM_map">
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>

`

document.getElementsByTagName('main')[0].innerHTML = main_text;



var numOfModel = 11;
let parent = document.getElementById('DOM_map');
for (let i = 0; i < numOfModel; i++) {
  parent.innerHTML += `
  <div class="container">
  
      <div class="prd_vlu">
        <div class="DOM_predict" id="predict_${i}"></div>
        <input class="DOM_value" type="text" value="" />
      </div>

      <div class="row">
        <div class="DOM_hsFix  col-6" id="hsFix_${i}"></div>
        <div class="chart_long col-6" id="chart_long_${i}"></div>
      </div>
    </div>`
}





// ====== BIỂU ĐỒ NGƯỜI DÙNG (BAR) ======
new Chart(document.getElementById('userChart'), {
  type: 'bar',
  data: {
    labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
    datasets: [{
      label: 'Người dùng mới',
      data: [12, 18, 15, 22, 30, 25, 40],
      backgroundColor: [
  '#4e73df', '#1cc88a', '#36b9cc',
  '#f6c23e', '#e74a3b', '#858796', '#fd7e14'
]


      
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true }
    }
  }
});




const ctx = document.getElementById('revenueChart');
const data = {
  labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
  datasets: [{
    label: 'Doanh thu (triệu VND)',
    data: [120, 150, 180, 210, 260, 300],
    backgroundColor: [
      '#4e73df',
      '#1cc88a',
      '#36b9cc',
      '#f6c23e',
      '#e74a3b',
      '#858796'
    ],
    borderWidth: 1
  }]
};

const polarChart = new Chart(ctx, {
  type: 'polarArea',
  data,
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'right'
      }
    },
    scales: {
      r: {
        ticks: {
          display: false
        }
      }
    }
  },
  plugins: [{
    id: 'centeredLabels',
    afterDraw(chart) {
      const { ctx } = chart;
      const meta = chart.getDatasetMeta(0);
      const dataset = chart.data.datasets[0];

      ctx.save();
      ctx.font = 'bold 12px Arial';
      ctx.fillStyle = '#000';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      meta.data.forEach((arc, index) => {
        const angle = (arc.startAngle + arc.endAngle) / 2;
        const radius = (arc.outerRadius + arc.innerRadius) / 2;

        const x = chart.chartArea.left + chart.chartArea.width / 2
          + Math.cos(angle) * radius;
        const y = chart.chartArea.top + chart.chartArea.height / 2
          + Math.sin(angle) * radius;

        ctx.fillText(dataset.data[index], x, y);
      });

      ctx.restore();
    }
  }]
});


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
let candleChart;

function drawCandleChart(dataArr) {
  const candles = buildCandles(dataArr);
   if (candles.length > 10) {
    candles = candles.slice(-10);
  }

  const labels = candles.map((_, i) => ` ${i + 1}`);
  const values = candles.map(c =>
    c.type === 'up' ? c.length : -c.length
  );
  const colors = candles.map(c =>
    c.type === 'up' ? '#1cc88a' : '#e74a3b'
  );

  if (candleChart) candleChart.destroy();

  candleChart = new Chart(
    document.getElementById('candleChart'),
    {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Candlestick Strength',
          data: values,
          backgroundColor: colors
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    }
  );
}
let _Candle = [];

drawCandleChart(_Candle);

function addCandleValue(v) {
  _Candle.push(v);
  drawCandleChart(_Candle);
}


