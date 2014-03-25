/*global $, d3, compareseries */

var ratio_details;


//===============================================================
// Functions to run once the page has loaded
//===============================================================

$(document).ready( function() {
	drawCompareChart();
	drawRatioChart();

	ratio_details = $('#ratioDetails');
});


//===============================================================
// Comparison chart
//===============================================================

function drawCompareChart() {
	var series_list = [];
	for (var i = 0; i < compareseries.length; i += 1) {
		var s = {
			count: i + 1,
			label: compareseries[i].label,
			series: compareseries[i].series,
			radius: 4
		}
		series_list.push(s);
	}
	drawGenericChart(series_list, 'comparison');
}


//===============================================================
// Ratio chart
//===============================================================

function drawRatioChart() {
	var max_y_value = d3.max(ratioseries, function(d) { return d[1]; })
	var response = drawChartBackground('#ratioChartContainer', 0.2, max_y_value);
	var ratio_canvas = response[0];
	var x_scale = response[1];
	var y_scale = response[2];

	var line = d3.svg.line()
		.x(function(d) { return x_scale(d[0]); })
		.y(function(d) { return y_scale(d[1]); });

	// Draw line showing ratio=1
	if (max_y_value < 20) {
		var unity_series = [[1750, 1], [2010, 1]];
		ratio_canvas.append('path')
			.attr('d', line(unity_series))
			.attr('class', 'unityPath');
	}

	// Draw line for data series
	ratio_canvas.append('path')
		.attr('d', line(ratioseries))
		.attr('class', 'ratioPath');

	// Draw circles
	var circles = ratio_canvas.selectAll('ratioCircle')
		.data(ratioseries);
	circles.enter().append('circle')
		.attr('class', 'ratioCircle')
		.attr('cx', function (d) { return x_scale(d[0]); })
		.attr('cy', function (d) { return y_scale(d[1]); })
		.attr('r', 4);

	// Listeners for mouseover events on datapoints in the chart
	circles
		.on('mouseover', function (d) {
			showRatioDetails(d, d3.event);
		})
		.on('mouseout', function () {
			hideRatioDetails();
		});
}


function showRatioDetails(d, event) {
	ratio_details.find('h3').text(d[0]);
	ratio_details.find('span').text(d[1]);
	// Reposition the pop-up
	ratio_details.css('left', (event.pageX) + 'px');
	ratio_details.css('top', (event.pageY) + 'px');
	ratio_details.css('display', 'block');
}

function hideRatioDetails() {
	ratio_details.css('display', 'none');
}

