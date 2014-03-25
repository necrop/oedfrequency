/*global $, d3 */
'use strict';

var chart_container,
	d3_chart_container,
	canvas,
	x_scale,
	y_scale,
	key_container,
	datapoint_details,
	raw_smoothed_toggle,
	frequency_values_displayed = 'smoothed';

var palette = ['#0099CC', '#00FF00', '#AA0078', '#FF6600',
	'#663300', '#177F75', '#2C6700',
	'#0099CC', '#00FF00', '#AA0078', '#FF6600',
	'#663300', '#177F75', '#2C6700',
	'#0099CC', '#00FF00', '#AA0078', '#FF6600',
	'#663300', '#177F75', '#2C6700'];


function initializeChart(series_list, chart_type) {
	chart_container = $('#frequencyChartContainer');
	d3_chart_container = d3.select('#frequencyChartContainer');
	datapoint_details = $('#datapointDetails');
	key_container = $('#keyContainer');
	raw_smoothed_toggle = $('#toggleValues');
	drawChartBackground(series_list);
	for (var i = 0; i < series_list.length; i += 1) {
		plotSeries(series_list[i]);
	}
	populateKey(series_list);
	if (chart_type === 'lemma') {
		setToggleListener();
	}
}


function drawChartBackground(series_list) {
	var max_frequency = findHighestValue(series_list);
	var canvas_width = chart_container.innerWidth();
	var canvas_height = canvas_width * 0.5;
	var y_padding = canvas_height * 0.1;
	var x_padding = canvas_width * 0.05;

	// x-axis scale
	x_scale = d3.scale.linear()
		.domain([1750, 2010])
		.range([x_padding, canvas_width]);

	// y-axis scale
	y_scale = d3.scale.linear()
		.domain([0, max_frequency * 1.2])
		.range([canvas_height - y_padding, 0]);

	// Create the SVG element (as a child of the #frequencyChartContainer div)
	canvas = d3_chart_container.append('svg')
		.attr('width', canvas_width)
		.attr('height', canvas_height)
		.attr('overflow', 'hidden');

	// Add a white rectangle the same size as the SVG element, for the background
	canvas.append('rect')
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
	canvas.append('g')
		.attr('class', 'frequencyAxis')
		.attr('transform', 'translate(0,' + (canvas_height - y_padding) + ')')
		.call(x_axis);

	var y_axis = d3.svg.axis()
		.scale(y_scale)
		.orient('left');
	canvas.append('g')
		.attr('class', 'frequencyAxis')
		.attr('transform', 'translate(' + x_padding + ', 0)')
		.call(y_axis);
}


function plotSeries(series) {

	var classname = 'fseries-' + series.count;
	var radius = series.radius;
	var circle_color;
	if (series.count === 0) {
		circle_color = 'red';
	} else {
		circle_color = palette[series.count - 1];
	}

	// Draw line
	var line = d3.svg.line()
		.x(function(d) { return x_scale(d[0]); })
		.y(function(d) { return y_scale(d[1]); });
	canvas.append('path')
		.attr('d', line(series.series))
		.attr('class', 'frequencyPath ' + classname);

	// Draw circles
	var circles = canvas.selectAll('circle.' + classname)
		.data(series.series);
	circles.enter().append('circle')
		.attr('class', 'frequencyCircle ' + classname)
		.attr('cx', function (d) { return x_scale(d[0]); })
		.attr('cy', function (d) { return y_scale(d[1]); })
		.attr('r', radius)
		.style('fill', circle_color);

	// Listeners for mouseover events on datapoints in the chart
	circles
		.on('mouseover', function (d) {
			showDatapointDetails(d, series.label, d3.event);
			highlightPath(series.count);
		})
		.on('mouseout', function () {
			hideDatapointDetails();
			restorePath(series.count);
		});
}


function populateKey(series_list) {
	var keyblock = '<span>Key:</span>';
	for (var i = 0; i < series_list.length; i += 1) {
		var series = series_list[i];
		var border;
		if (series.count === 0) {
			border = 'red';
		} else {
			border = palette[series.count - 1];
		}
		var span = '<span class="activeKey" series="' + series.count + '" style="border-color: ' + border + '">' + series.label + '</span>';
		keyblock += span;
	}
	key_container.html(keyblock);

	// set listeners
	$('span.activeKey').mouseover(function() {
		var series_num = $(this).attr('series');
		highlightPath(series_num);
	})
	.mouseout(function() {
		var series_num = $(this).attr('series');
		restorePath(series_num);
	});
}


function highlightPath(series_num) {
	$('path.fseries-' + series_num).css('stroke', 'red').css('stroke-width', 4);
}

function restorePath(series_num) {
	$('path.fseries-' + series_num).css('stroke', 'gray').css('stroke-width', 1);
}



//----------------------------------------------------------
// Show/hide the pop-up with details of a given data point
//----------------------------------------------------------

function showDatapointDetails(d, label, event) {
	var value_shown;
	if (frequency_values_displayed == 'raw') {
		value_shown = d[2];
	} else {
		value_shown = d[1];
	}
	// Populate the pop-up
	datapoint_details.find('h3').text(label);
	datapoint_details.find('div').text(d[0] + ': ' + value_shown + ' per million (' + frequency_values_displayed + ' value)');
	// Reposition the pop-up
	datapoint_details.css('left', (event.pageX) + 'px');
	datapoint_details.css('top', (event.pageY) + 'px');
	datapoint_details.css('display', 'block');
}

function hideDatapointDetails() {
	datapoint_details.css('display', 'none');
}




function findHighestValue(series_list) {
	// Find the highest value in each series...
	var tops = [];
	for (var i = 0; i < series_list.length; i += 1) {
		var max = d3.max(series_list[i].series, function(d) { return d[1]; });
		tops.push(max);
	}
	// ...Now find the highest value out of those
	return d3.max(tops);
}


//----------------------------------------------------------
// Switch between raw and smoothed values (main frequency chart only)
// - comparison charts don't have a toggle button
//----------------------------------------------------------

function setToggleListener() {
	raw_smoothed_toggle.click( function(event) {
		$(this).text('show ' + frequency_values_displayed + ' values');
		if (frequency_values_displayed == 'smoothed') {
			transitionToRaw();
			frequency_values_displayed = 'raw';
		} else {
			transitionToSmoothed();
			frequency_values_displayed = 'smoothed';
		}
		event.preventDefault();
	})
}

function transitionToRaw() {
	var circles = canvas.selectAll('.frequencyCircle');
	circles.transition()
		.attr('cy', function(d) { return y_scale(d[2]); })
		.duration(750);
}

function transitionToSmoothed() {
	var circles = canvas.selectAll('.frequencyCircle');
	circles.transition()
		.attr('cy', function(d) { return y_scale(d[1]); })
		.duration(750);
}
