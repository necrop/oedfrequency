/*global $, d3, compareseries */

var ratio_canvas,
	ratio_details;


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
	initializeChart(series_list, 'comparison');
}


//===============================================================
// Ratio chart
//===============================================================

function drawRatioChart() {

	var canvas_width = $('#ratioChartContainer').innerWidth();
	var canvas_height = canvas_width * 0.2;
	var y_padding = canvas_height * 0.1;
	var x_padding = canvas_width * 0.05;

	// x-axis scale
	var x_scale = d3.scale.linear()
		.domain([1750, 2010])
		.range([x_padding, canvas_width]);

	// y-axis scale
	var max_y_value = d3.max(ratioseries, function(d) { return d[1]; })
	var y_scale = d3.scale.linear()
		.domain([0, max_y_value * 1.1])
		.range([canvas_height - y_padding, 0]);

	// Create the SVG element (as a child of the #rankChartContainer div)
	ratio_canvas = d3.select('#ratioChartContainer').append('svg')
		.attr('width', canvas_width)
		.attr('height', canvas_height)
		.attr('overflow', 'hidden');

	// Add a white rectangle the same size as the SVG element, for the background
	ratio_canvas.append('rect')
		.attr('x', 0)
		.attr('y', 0)
		.attr('width', canvas_width)
		.attr('height', canvas_height)
		.attr('class', 'chartBackground');

	// Draw axes
	var format_as_year = d3.format('d');
	var x_axis = d3.svg.axis()
		.scale(x_scale)
		.orient('bottom');
	x_axis.tickFormat(format_as_year);
	ratio_canvas.append('g')
		.attr('class', 'frequencyAxis')
		.attr('transform', 'translate(0,' + (canvas_height - y_padding) + ')')
		.call(x_axis);

	var y_axis = d3.svg.axis()
		.scale(y_scale)
		.orient('left');
	ratio_canvas.append('g')
		.attr('class', 'frequencyAxis')
		.attr('transform', 'translate(' + x_padding + ', 0)')
		.call(y_axis);

	// Draw line
	var line = d3.svg.line()
		.x(function(d) { return x_scale(d[0]); })
		.y(function(d) { return y_scale(d[1]); });
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

