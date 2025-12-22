function drawChartLong(localData, localStartIndex, matchDataLocal, predictedDataLocal, bestIndex, long_chart, trend) {
    const x_indices = localData.map((_, i) => localStartIndex + i);

    const option1 = {
        title: { text: `${bestIndex} | ${trend}` },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                const globalIndex = x_indices[params[0].dataIndex];
                let str = `Index: <b>${globalIndex}</b><br/>`;
                params.forEach(item => {
                    if (item.value !== null && item.value !== undefined && item.value !== '-') {
                        str += `<span style="color:${item.color}">●</span> ${item.seriesName}: <b>${parseFloat(item.value).toFixed(2)}</b><br/>`;
                    }
                });
                return str;
            }
        },
        xAxis: {
            type: 'category',
            data: x_indices, 
            name: 'X'
        },
        yAxis: { type: 'value', name: 'Giá trị' },
        series: [
            {
                name: 'Ngữ cảnh (Quá khứ)',
                type: 'line',
                // Sửa: Chỉ truyền mảng giá trị Y khi X là category
                data: localData,
                itemStyle: { color: 'gray' },
                lineStyle: { width: 1.5 },
                showSymbol: false,
                z: 1
            },
            {
                name: 'Đoạn Khớp Tốt nhất',
                type: 'line',
                // Dữ liệu phải là mảng giá trị Y, sử dụng '-' cho khoảng trống
                // Cần đảm bảo `matchDataLocal` chỉ là mảng giá trị Y (chứ không phải [[x,y],...])
                // Nếu backend trả về [[x,y],...] thì cần chuyển đổi ở frontend
                data: matchDataLocal.map(item => item === '-' ? '-' : item[1]),
                itemStyle: { color: 'red' },
                lineStyle: { width: 3 },
                showSymbol: true,
                symbolSize: 6,
                z: 3
            },
            {
                name: '10 Điểm Tương lai',
                type: 'line',
                // Tương tự, chuyển đổi thành mảng giá trị Y
                data: predictedDataLocal.map(item => item === '-' ? '-' : item[1]),
                itemStyle: { color: 'green' },
                lineStyle: { type: 'dotted', width: 3 },
                showSymbol: true,
                symbolSize: 6,
                z: 2
            }
        ]
    };
    long_chart.setOption(option1, true);
}
function drawChartShort(S_centered, W_centered, max_score, best_index, chart_short) {
    // Biểu đồ 2: So sánh Hình dạng (Đã trừ Trung bình)
    const sData = S_centered.map((value, index) => [index, value]);
    const wData = W_centered.map((value, index) => [index, value]);

    const option2 = {
        title: { text: `${max_score} | ${best_index}` },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'value', name: 'X' },
        yAxis: { type: 'value', name: 'Giá trị (Trừ Trung bình)' },
        series: [
            {
                name: 'Hình dạng Mẫu Short',
                type: 'line',
                data: sData,
                itemStyle: { color: 'green' },
                lineStyle: { type: 'dashed', width: 2 },
                showSymbol: false
            },
            {
                name: 'Hình dạng Cửa sổ Khớp',
                type: 'line',
                data: wData,
                itemStyle: { color: 'red' },
                lineStyle: { width: 2 },
                showSymbol: true,
                symbolSize: 4
            }
        ]
    };
    chart_short.setOption(option2);
}

function drawLineChart(dataArray, chartDom, modelName, stat_score) {
    if (!Array.isArray(dataArray)) {
        console.error("dataArray phải là một mảng!");
        return;
    }
    const chart = echarts.init(chartDom);
    const option = {
        title: {
            text: `${modelName}: ${stat_score}`
        },
        tooltip: {
            trigger: 'axis'
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
                data: dataArray
            }
        ]
    };
    chart.setOption(option);
}
function calculateAndPlot(data) {

    for (let i = 0; i < numOfModel; i++) {
        drawLineChart(
            data[i].history_fix_cumsum, 
            DOM_hsFixs[i],
            data[i].modelName,
            data[i].stat_score
        )
        drawChartLong(
            data[i].local_data, 
            data[i].local_start_index, 
            data[i].match_data_local, 
            data[i].predicted_data_local, 
            data[i].best_index, 
            chart_longs[i],
            data[i].trend
        );
        // drawChartShort(
        //     data[i].S_centered,
        //     data[i].W_centered,
        //     data[i].max_score.toFixed(4),
        //     data[i].best_index,
        //     chart_shorts[i]
        // );
    }
}

var chart_longs = [];
var chart_shorts = [];
for(let i=0; i<numOfModel; i++){
    chart_longs.push(echarts.init(document.getElementById(`chart_long_${i}`)));
    chart_shorts.push(echarts.init(document.getElementById(`chart_short_${i}`)));
}
const DOM_hsFixs = document.getElementsByClassName('DOM_hsFix');
const DOM_predicts = document.getElementsByClassName('DOM_predict');
const DOM_values = document.getElementsByClassName('DOM_value');


