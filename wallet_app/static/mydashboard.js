// Palette de couleurs utilisée par tous les graphiques
var colors = ['#1D507A', '#2F6999', '#66A0D1', '#8FC0E9', '#4682B4'];

d3.json('/api/wallet/1', display_wallet_nvd3_graph);

function display_wallet_nvd3_graph(datas) {
    if (datas['status'] == 'ok') {
        var wallet = datas['wallet'];
        var stockData = [];

        // Convertir les dates au format correct pour NVD3
        wallet['dates'] = wallet['dates'].map(function(date) {
            return new Date(date);
        });

         // Traitement pour datas['share_value']
         var shareData = datas['share_value'].map(function(share, index) {
            return [wallet['dates'][index], share];
        });
        stockData.push({
            key: 'share value',
            values: shareData
        });
        
        // Traitement pour datas['share_value_2']
        var shareData2 = datas['share_value_2'].map(function(share2, index) {
            return [wallet['dates'][index], share2];
        });
        stockData.push({
            key: 'share value 2',
            values: shareData2
        });

        // Traitement pour datas['twrr_cumulated']
        var shareData2 = datas['twrr_cumulated'].map(function(share2, index) {
            return [wallet['dates'][index], share2];
        });
        stockData.push({
            key: 'twrr',
            values: shareData2
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

            chart.brushExtent([new Date(wallet['dates'][0]), new Date(wallet['dates'][0] + 24 * 3600 * 1000)]);

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


d3.json('/api/wallet/valuation', display_wallet_valuation_nvd3_graph);

function display_wallet_valuation_nvd3_graph(datas) {
    if (datas['status'] == 'ok') {
        var wallet = datas['wallet'];
        var stockData = [];

        // Convertir les dates au format correct pour NVD3
        wallet['dates'] = wallet['dates'].map(function(date) {
            return new Date(date);
        });

        var closeData = wallet['valuations'].map(function(valuation, index) {
            return [wallet['dates'][index], valuation];
        });

        stockData.push({
            key: 'wallet valuation',
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

            chart.brushExtent([new Date(wallet['dates'][0]), new Date(wallet['dates'][0] + 24 * 3600 * 1000)]);

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

            d3.select('#wallet_valuation svg')
                .datum(stockData)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    }
}


d3.json('/api/wallet/share_value', display_wallet_share_value_nvd3_graph);

function display_wallet_share_value_nvd3_graph(datas) {
    if (datas['status'] == 'ok') {
        var wallet = datas['wallet'];
        var stockData = [];

        // Convertir les dates au format correct pour NVD3
        wallet['dates'] = wallet['dates'].map(function(date) {
            return new Date(date);
        });

        var closeData = datas['share_value'].map(function(share_value, index) {
            return [wallet['dates'][index], share_value];
        });

        stockData.push({
            key: 'wallet share_value',
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

            chart.brushExtent([new Date(wallet['dates'][0]), new Date(wallet['dates'][0] + 24 * 3600 * 1000)]);

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

            d3.select('#wallet_share_value svg')
                .datum(stockData)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    }
}


d3.json('/api/wallet/share_value_2', display_wallet_share_value_2_nvd3_graph);

function display_wallet_share_value_2_nvd3_graph(datas) {
    if (datas['status'] == 'ok') {
        var wallet = datas['wallet'];
        var stockData = [];

        // Convertir les dates au format correct pour NVD3
        wallet['dates'] = wallet['dates'].map(function(date) {
            return new Date(date);
        });

        var closeData = datas['share_value_2'].map(function(share_value_2, index) {
            return [wallet['dates'][index], share_value_2];
        });

        stockData.push({
            key: 'wallet share_value_2',
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

            chart.brushExtent([new Date(wallet['dates'][0]), new Date(wallet['dates'][0] + 24 * 3600 * 1000)]);

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

            d3.select('#wallet_share_value_2 svg')
                .datum(stockData)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    }
}


d3.json('/api/wallet/TWRR', display_wallet_twrr_cumulated_nvd3_graph);

function display_wallet_twrr_cumulated_nvd3_graph(datas) {
    if (datas['status'] == 'ok') {
        var stockData = [];

        // Convertir les dates au format correct pour NVD3
        datas['dates'] = datas['dates'].map(function(date) {
            return new Date(date);
        });

        var closeData = datas['twrr_cumulated'].map(function(twrr_cumulated, index) {
            return [datas['dates'][index], twrr_cumulated];
        });

        stockData.push({
            key: 'wallet twr',
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

            chart.brushExtent([new Date(datas['dates'][0]), new Date(datas['dates'][0] + 24 * 3600 * 1000)]);

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

            d3.select('#wallet_twrr svg')
                .datum(stockData)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    }
}


d3.json('/api/stock', display_stock_nvd3_graph);

function display_stock_nvd3_graph(datas) {
    if (datas['status'] == 'ok') {
        var asset = datas['asset'];
        var stockData = [];

        // Convertir les dates au format correct pour NVD3
        asset['dates'] = asset['dates'].map(function(date) {
            return new Date(date);
        });

        var closeData = asset['closes'].map(function(close, index) {
            return [asset['dates'][index], close];
        });

        stockData.push({
            key: asset['short_name'],
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
