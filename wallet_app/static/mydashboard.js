// Palette de couleurs utilisée par tous les graphiques
var colors = ["#1D507A", "#2F6999", "#66A0D1", "#8FC0E9", "#4682B4"];

d3.json('/api/wallet', display_wallet_nvd3_graph);

function display_wallet_nvd3_graph(data) {
    if (data["status"] == "ok") {
        var wallet = data["data"];
        var stockData = [];
        console.log('wallet =\n', wallet)

        // Convertir les dates au format correct pour NVD3
        wallet["dates"] = wallet["dates"].map(function(date) {
            return new Date(date);
        });

        var closeData = wallet["valuation"].map(function(close, index) {
            return [wallet["dates"][index], close];
        });

        stockData.push({
            key: "wallet valuation",
            values: closeData
        });
        
        // Obtenir la valeur maximale de toutes les données
        var maxValue = d3.max(stockData, function(d) {
            return d3.max(d.values, function(v) {
                return v[1];
            });
        });

        // Ajouter le décalage (10%)
        var yMax = maxValue * 1.1;

        nv.addGraph(function() {
            var chart = nv.models.lineWithFocusChart()
                .x(function(d) {
                    return d[0];
                })
                .y(function(d) {
                    return d[1];
                })
                .yDomain([0, yMax])
                .height(270)
                .color(colors);

            chart.brushExtent([new Date(wallet["dates"][0]), new Date(wallet["dates"][0] + 24 * 3600 * 1000)]);

            chart.xAxis
                .showMaxMin(false)
                .tickFormat(function(d) {
                    return d3.time.format('%d/%m/%y')(new Date(d));
                });

            chart.x2Axis
                .showMaxMin(false)
                .tickFormat(function(d) {
                    return d3.time.format('%d/%m/%y')(new Date(d));
                });

            chart.yAxis
                .showMaxMin(false)
                .axisLabel('Close Price')
                .tickFormat(d3.format('.2f'))
                .domain([0, yMax]);  // Définir le domaine de l'axe y

            chart.y2Axis
                .showMaxMin(false)
                .ticks(false);

            d3.select('#wallet svg')
                .datum(stockData)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    }
}

d3.json('/api/stock', display_stock_nvd3_graph);

function display_stock_nvd3_graph(data) {
    if (data["status"] == "ok") {
        console.log('data["data"] =\n', data["data"])
        var asset = data["data"];
        var stockData = [];

        // Convertir les dates au format correct pour NVD3
        asset["dates"] = asset["dates"].map(function(date) {
            return new Date(date);
        });

        var closeData = asset["closes"].map(function(close, index) {
            return [asset["dates"][index], close];
        });

        stockData.push({
            key: asset["short_name"],
            values: closeData
        });

        // Obtenir la valeur maximale de toutes les données
        var maxValue = d3.max(stockData, function(d) {
            return d3.max(d.values, function(v) {
                return v[1];
            });
        });

        // Ajouter le décalage (10%)
        var yMax = maxValue * 1.1;

        nv.addGraph(function() {
            var chart = nv.models.lineChart()
                .x(function(d) {
                    return d[0];
                })
                .y(function(d) {
                    return d[1];
                })
                .yDomain([0, yMax])
                .height(270)
                .color(colors);

            chart.xAxis
                .showMaxMin(false)
                .tickFormat(function(d) {
                    return d3.time.format('%d/%m/%y')(new Date(d));
                });

            chart.yAxis
                .showMaxMin(false)
                .axisLabel('Close Price')
                .tickFormat(d3.format('.2f'))
                .domain([0, yMax]);  // Définir le domaine de l'axe y

            d3.select('#stock svg')
                .datum(stockData)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    }
}
