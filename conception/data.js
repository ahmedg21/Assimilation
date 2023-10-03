$(document).ready(function () {
    table = $('#air').DataTable({
        buttons: [
            'csv', 'excel', 'pdf', 'print'
        ],
        ajax: 'http://196.1.100.231/inc/test.php?tab=all',
        columns: [
            //{ data: 'id' },
            { data: 'pm10' },
            { data: 'pm25' },
            { data: 'pm01' },
            { data: 'temperature' },
            { data: 'humidity' },
            { data: 'event' },
        ],
        order: [[5, 'desc']]

    });

    $.ajax("http://196.1.100.231/inc/test.php?global=all", {
        success: function (data) {
            console.log(data)
            $('#v01').text(data[0].pm01 + " µg/m³");
            $('#v25').text(data[0].pm25 + " µg/m³");
            $('#v10').text(data[0].pm10 + " µg/m³");
            $('#temp').text(data[0].temperature + "°C");
            $('#hum').text(data[0].humidity + "%");
            $('#date').text(data[0].event);
        }
    });
    setInterval(() => {
        $.ajax("http://196.1.100.231/inc/test.php?global=all", {
            success: function (data) {
                console.log(data)
                $('#v01').text(data[0].pm01 + " µg/m³");
                $('#v25').text(data[0].pm25 + " µg/m³");
                $('#v10').text(data[0].pm10 + " µg/m³");
                $('#temp').text(data[0].temperature + "°C");
                $('#hum').text(data[0].humidity + "%");
                $('#date').text(data[0].event);
            }
        });
    }, 50000);
});

var table, seriesOptions = [],
    seriesCounter = 0,
    names = ['PM01', 'PM10', 'PM25'],
    points = [], dd = new Date(),
    init_day = 0, frequence = 20 * 1000, sInt;//instance setInterval
var chart_pm;

/**
 * Create the chart when all data is loaded
 * @return {undefined}
 */
function createStockChart() {

    Highcharts.stockChart('stock', {

        rangeSelector: {
            selected: 4
        },

        yAxis: {
            labels: {
                formatter: function () {
                    return (this.value > 0 ? ' + ' : '') + this.value + 'µg/m³';
                }
            },
            plotLines: [{
                value: 0,
                width: 2,
                color: 'silver'
            }]
        },

        plotOptions: {
            series: {
                compare: 'value',
                showInNavigator: true
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle'
        },

        tooltip: {
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y} µg/m³</b> ',// ({point.change}%)<br/>',
            valueDecimals: 2,
            split: true
        },

        series: seriesOptions
    });
}

function createOtherChart(id, name, data, unite) {
    Highcharts.stockChart(id, {

        rangeSelector: {
            selected: 4
        },

        yAxis: {
            labels: {
                formatter: function () {
                    return (this.value > 0 ? ' + ' : '') + this.value + unite;
                }
            },
            plotLines: [{
                value: 0,
                width: 2,
                color: 'silver'
            }]
        },

        plotOptions: {
            series: {
                compare: 'value',
                showInNavigator: true
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle'
        },

        tooltip: {
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y} ' + unite + '</b> ',// ({point.change}%)<br/>',
            valueDecimals: 2,
            split: true
        },

        series: [{
            name: name,
            data: data
        }]
    });
}

function stock(data, nam, i) {
    seriesOptions[i] = {
        name: nam,
        data: data
    };

    // As we're loading the data asynchronously, we don't know what order it
    // will arrive. So we keep a counter and create the chart when all the data>
    seriesCounter += 1;

    if (seriesCounter === names.length) {
        createStockChart();
    }
}


function loadDataFromServer() {
    Highcharts.getJSON(
        'http://196.1.100.231/inc/test.php?type=pm01',
        (data) => {

            stock(data, 'pm01', 0);
            createOtherChart('pm01', "PM1.0", data, 'µg/m³');

        }
    );
    Highcharts.getJSON(
        'http://196.1.100.231/inc/test.php?type=pm25',
        (data) => {
            stock(data, 'pm25', 1);
            createOtherChart('pm25', "PM2.5", data, 'µg/m³')
        }
    );
    Highcharts.getJSON(
        'http://196.1.100.231/inc/test.php?type=pm10',
        (data) => {
            stock(data, 'pm10', 2);
            createOtherChart('pm10', "PM10", data, 'µg/m³')
        }
    );
    Highcharts.getJSON(
        'http://196.1.100.231/inc/test.php?type=temperature',
        (data) => {
            createOtherChart('temperature', "Temperature", data, '°C')
        }
    );
    Highcharts.getJSON(
        'http://196.1.100.231/inc/test.php?type=humidity',
        (data) => {
            createOtherChart('humidity', "Humidite", data, '%')
        }
    );
}


loadDataFromServer();
setInterval(() => {
    loadDataFromServer();
    table.ajax.reload();
}, 5 * 60 * 1000);





