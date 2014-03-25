/*global $, d3, lemma, main_series, types_series, rankdata, rankorder, mod_frequency */
'use strict';

var rank_canvas,
	rank_details,
	min_rank_frequency = 0.0001;

var rank_data = rankdata();
var rank_total = d3.max(rank_data, function(d) { return d[0]; });



//===============================================================
// Functions to run once the page has loaded
//===============================================================

$(document).ready( function() {
	rank_details = $('#rankDetails');
	drawFrequencyChart();
	drawRankChart();
});


//===============================================================
// Frequency chart
//===============================================================

function drawFrequencyChart() {
	var series_list = [];
	for (var i = 0; i < types_series.length; i += 1) {
		var s = {
			count: i + 1,
			label: types_series[i].label,
			radius: 3,
			series: types_series[i].series
		}
		series_list.push(s);
	}
	var main = {
		count: 0,
		label: lemma + ' (total)',
		radius: 5,
		series: main_series
	}
	series_list.push(main);
	drawGenericChart(series_list, 'lemma');
}



//===============================================================
// Rank chart
//===============================================================

function drawRankChart() {
	var zeroless_rank_data = [];
	for (var i = 0; i < rank_data.length; i += 1) {
		var d = rank_data[i];
		if (d[1] >= min_rank_frequency) {
			zeroless_rank_data.push(d);
		}
	}

	var canvas_width = $('#rankChartContainer').innerWidth();
	var canvas_height = canvas_width * 0.3;
	var y_padding = canvas_height * 0.1;
	var x_padding = canvas_width * 0.05;

	// x-axis scale
	var max_x_value = d3.max(rank_data, function(d) { return d[0]; })
	var x_scale = d3.scale.linear()
		.domain([0, max_x_value])
		.range([x_padding, canvas_width]);

	// y-axis scale
	var max_y_value = d3.max(rank_data, function(d) { return d[1]; })
	var y_scale = d3.scale.log()
		.domain([min_rank_frequency, max_y_value])
		.range([canvas_height - y_padding, 0]);

	// Create the SVG element (as a child of the #rankChartContainer div)
	rank_canvas = d3.select('#rankChartContainer').append('svg')
		.attr('width', canvas_width)
		.attr('height', canvas_height)
		.attr('overflow', 'hidden');

	// Add a white rectangle the same size as the SVG element, for the background
	rank_canvas.append('rect')
		.attr('x', 0)
		.attr('y', 0)
		.attr('width', canvas_width)
		.attr('height', canvas_height)
		.attr('class', 'chartBackground');

	// Draw axes
	var x_axis = d3.svg.axis()
		.scale(x_scale)
		.orient('bottom');
	rank_canvas.append('g')
		.attr('class', 'frequencyAxis')
		.attr('transform', 'translate(0,' + (canvas_height - y_padding) + ')')
		.call(x_axis);

	// Draw circles
	var circles = rank_canvas.selectAll('rankDot')
		.data(zeroless_rank_data);
	circles.enter().append('circle')
		.attr('class', 'rankDot')
		.attr('cx', function (d) { return x_scale(d[0]); })
		.attr('cy', function (d) { return y_scale(d[1]); })
		.attr('r', 2);

	// Listeners for mouseover events on datapoints in the chart
	circles
		.on('mouseover', function (d) {
			populateRankDetails(d);
			displayRankDetails(d3.event);
		})
		.on('mouseout', function () {
			hideRankDetails();
		});


	if (mod_frequency && mod_frequency >= min_rank_frequency) {
		var main_dot = rank_canvas.append('circle')
			.attr('class', 'rankDotHighlight')
			.attr('cx', x_scale(rankorder))
			.attr('cy', y_scale(mod_frequency))
			.attr('r', 6);

		// Listeners for mouseover events on main dot
		main_dot
			.on('mouseover', function () {
				populateRankDetailsMain();
				displayRankDetails(d3.event);
			})
			.on('mouseout', function () {
				hideRankDetails();
			});
	}
}


function populateRankDetails(d) {
	var percentile = toOrdinal(rankPercentile(d[0], rank_total));
	// Populate the pop-up
	rank_details.find('h3').text('#' + d[0] + ' out of ' + rank_total + ' entries');
	rank_details.find('div').html('<p>' + percentile + ' percentile; modern frequency c. ' + d[1] + ' per million</p><p>Words like <em>' + d[2] + '</em></p>');
}

function populateRankDetailsMain() {
	var percentile = toOrdinal(rankPercentile(rankorder, rank_total));
	// Populate the pop-up
	rank_details.find('h3').text(lemma);
	rank_details.find('div').html('<p>#' + rankorder + ' out of ' + rank_total + ' entries</p><p>' + percentile + ' percentile; modern frequency c. ' + mod_frequency + ' per million</p>');
}

function displayRankDetails(event) {
	// Reposition the pop-up
	rank_details.css('left', (event.pageX) + 'px');
	rank_details.css('top', (event.pageY) + 'px');
	rank_details.css('display', 'block');
}

function hideRankDetails() {
	rank_details.css('display', 'none');
}

function rankPercentile(rank, total) {
	return Math.floor((100 / total) * rank) + 1;
}

function toOrdinal(num) {
    var numStr = num.toString(),
        last = numStr.slice(-1),
        ord = '';
    switch (last) {
        case '1':
            ord = numStr.slice(-2) === '11' ? 'th' : 'st';
            break;
        case '2':
            ord = numStr.slice(-2) === '12' ? 'th' : 'nd';
            break;
        case '3':
            ord = numStr.slice(-2) === '13' ? 'th' : 'rd';
            break;
        default:
            ord = 'th';
            break;
    }
    return num.toString() + ord;
}