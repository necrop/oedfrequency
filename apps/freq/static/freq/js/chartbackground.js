/*global $, d3 */
'use strict';


function drawChartBackground(container_id, y_ratio, max_frequency) {
	var chart_container = $(container_id);
	var d3_chart_container = d3.select(container_id);

	var canvas_width = chart_container.innerWidth();
	var canvas_height = canvas_width * y_ratio;
	var y_padding = canvas_height * 0.1;
	var x_padding = canvas_width * 0.05;

	// x-axis scale
	var x_scale = d3.scale.linear()
		.domain([1750, 2010])
		.range([x_padding, canvas_width]);

	// y-axis scale
	var y_scale = d3.scale.linear()
		.domain([0, max_frequency * 1.2])
		.range([canvas_height - y_padding, 0]);

	// Create the SVG element (as a child of the #frequencyChartContainer div)
	var canvas = d3_chart_container.append('svg')
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

	return [canvas, x_scale, y_scale];
}
