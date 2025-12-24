const main_text = `
  <div class="row g-4">

    <!-- ================= MESSAGES ================= -->
    <div class="col-lg-4">
      <div class="card shadow-sm"  style="height:400px"  >
        <div class="card-header fw-bold">
          💬 Tin nhắn mới
        </div>

        <ul class="list-group list-group-flush" id="chat-container">

        <div class="card-footer text-center">
          <a href="#" class="text-decoration-none">Xem tất cả</a>
        </div>
      </div>

          <div class="progress col-md-12" style="height: 3px; margin:10px; width: 97%">
      <div class="progress-bar bg-success" role="progressbar" aria-valuenow="" aria-valuemin="0" aria-valuemax="55"></div>
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

    <!-- Doanh thu -->
    <div class="col-lg-6">
        <div class="card shadow-sm">
        <div class="card-header fw-bold">
            💰 Doanh thu theo tháng
        </div>
        <div class="card-body">
            <canvas id="revenueChart" height="120"></canvas>
        </div>
        </div>
    </div>

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
        <div class="row">
      <div class="DOM_hsFix  col-6" id="hsFix_${i}"></div>
      <div class="chart_long col-4" id="chart_long_${i}"></div>
      <div class="col-2">
        <div class="DOM_predict" id="predict_${i}"></div>
        <input class="DOM_value" type="text" value="" />
      </div>
    </div>
    </div>`
}




// ====== BIỂU ĐỒ DOANH THU (LINE) ======
new Chart(document.getElementById('revenueChart'), {
  type: 'line',
  data: {
    labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
    datasets: [{
      label: 'Doanh thu (triệu VND)',
      data: [120, 150, 180, 210, 260, 300],
      borderWidth: 2,
      tension: 0.4,
      fill: false
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true }
    }
  }
});

// ====== BIỂU ĐỒ NGƯỜI DÙNG (BAR) ======
new Chart(document.getElementById('userChart'), {
  type: 'bar',
  data: {
    labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
    datasets: [{
      label: 'Người dùng mới',
      data: [12, 18, 15, 22, 30, 25, 40]
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true }
    }
  }
});

