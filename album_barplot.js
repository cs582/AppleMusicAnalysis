var maxNumberOfSongs = 10;

var svgWidth = 300,
    svgHeight = 300,
    barPadding = 5;

var barHeight = (svgHeight / maxNumberOfSongs);

var svg = d3.select("svg")
    .attr("width", svgWidth)
    .attr("height", svgHeight);

d3.csv("data/Album_Track_1.csv", function (data) {

    values = d3.map(data, function (d) {return d.Duration;})
    categories = d3.map(data, function (d) {return d.Track;})

    console.log(values)
    console.log(categories)


    var xScale = d3.scaleLinear()
        .domain([0, d3.max(values)])
        .range([0, svgWidth]);

    var barChart = svg.selectAll("rect")
        .data(values)
        .enter()
        .append("rect")
        .attr("x", function(d) {
            return 0;
        })
        .attr("width", function (d){
            return xScale(d);
        })
        .attr("height", barHeight - barPadding)
        .attr("transform", function(d, i) {
            var translate = [0, barHeight * i];
            return "translate("+translate+")";
        });

    var text = svg.selectAll("text")
        .data(categories)
        .enter()
        .append("text")
        .text(function (d) {
            return d;
        })
        .attr("y", function (d, i) {
            return barHeight*(i+1) - 10;
        })
        .attr("x", function (d, i) {
            return 5;
        })
        .attr("fill", "#CBBEB5");

})



