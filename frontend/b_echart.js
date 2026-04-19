function drawLineChart(chartDom, dataArray, modelName, maPeriod = 5) {
    if (!Array.isArray(dataArray)) {
        console.error("dataArray phải là một mảng!");
        return;
    }

    // Hàm tính toán Moving Average
    const calculateMA = (data, period) => {
        let result = [];
        for (let i = 0; i < data.length; i++) {
            if (i < period - 1) {
                result.push('-'); // Chưa đủ dữ liệu để tính MA
                continue;
            }
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += data[i - j];
            }
            result.push((sum / period).toFixed(2));
        }
        return result;
    };

    let chart = echarts.getInstanceByDom(chartDom);
    if (!chart) {
        chart = echarts.init(chartDom);
    }

    const maData = calculateMA(dataArray, maPeriod);

    const option = {
        title: { text: modelName },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['Value', `MA${maPeriod}`] // Thêm chú thích
        },
        xAxis: {
            type: 'category',
            data: dataArray.map((_, i) => i)
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
                name: 'Value',
                type: 'line',
                data: dataArray,
                smooth: true, // Làm mượt đường giá
                lineStyle: { opacity: 0.5 }
            },
            {
                name: `MA${maPeriod}`,
                type: 'line',
                data: maData,
                smooth: true,
                symbol: 'none', // Ẩn các điểm tròn trên đường MA
                lineStyle: {
                    width: 2,
                    color: '#ff7f50' // Màu cam đặc trưng cho MA
                }
            }
        ]
    };
    chart.setOption(option);
}
