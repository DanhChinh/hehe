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
                result.push('-'); 
                continue;
            }
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += data[i - j];
            }
            result.push(parseFloat((sum / period).toFixed(2)));
        }
        return result;
    };

    let chart = echarts.getInstanceByDom(chartDom);
    if (!chart) {
        chart = echarts.init(chartDom);
    }

    const maData = calculateMA(dataArray, maPeriod);

    const option = {
        // Cấu hình màu chữ tổng thể của biểu đồ tiệp với theme Dark Mode
        textStyle: {
            color: '#9ca3af',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        },
        title: { 
            text: modelName,
            textStyle: { color: '#40c714', fontSize: 14, fontWeight: '600' },
            top: 10,
            left: 15
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: '#1f2937', // Nền tooltip tối đồng bộ
            borderColor: '#374151',
            textStyle: { color: '#f1f5f9' },
            axisPointer: { lineStyle: { color: '#4b5563', type: 'dashed' } }
        },
        legend: {
            data: ['Value', `MA${maPeriod}`],
            textStyle: { color: '#9ca3af' },
            top: 10,
            right: 40 // Tránh đè lên nút vát góc ở đỉnh phải card
        },
        grid: {
            left: '4%',
            right: '4%',
            bottom: '5%',
            top: '65',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: dataArray.map((_, i) => i),
            axisLine: { lineStyle: { color: '#1f2937' } }, // Đường trục x chìm
            axisLabel: { color: '#9ca3af' }
        },
        yAxis: {
            type: 'value',
            scale: true, // Tự động căn chỉnh khoảng giá trị Y cho sát dữ liệu
            axisLabel: { color: '#9ca3af' },
            splitLine: { lineStyle: { color: '#1f2937' } } // Đường lưới ngang mịn ẩn nhẹ
        },
        series: [
            {
                name: 'Value',
                type: 'line',
                data: dataArray,
                smooth: 0.2, 
                symbol: 'none',
                lineStyle: { width: 2, color: '#38bdf8', opacity: 0.8 }, // Đường giá xanh Neon chủ đạo
                areaStyle: {
                    // Đổ bóng vùng gradient mịn phía dưới đường giá
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(56, 189, 248, 0.2)' },
                        { offset: 1, color: 'rgba(56, 189, 248, 0)' }
                    ])
                }
            },
            {
                name: `MA${maPeriod}`,
                type: 'line',
                data: maData,
                smooth: 0.2,
                symbol: 'none', 
                lineStyle: { width: 1.5, color: '#f59e0b' } // Đường MA cam vàng tài chính rõ ràng
            }
        ]
    };
    chart.setOption(option);
}

