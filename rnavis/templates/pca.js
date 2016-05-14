var callback = function(error, data) {
    data.forEach(function(d) {
        d.pc1 = +d.pc1;
        d.pc2 = +d.pc2;
        d.pc3 = +d.pc3;
        d.pc4 = +d.pc4;
        d.exp_var1 = +d.exp_var1;
        d.exp_var2 = +d.exp_var2;
        d.exp_var3 = +d.exp_var3;
        d.exp_var4 = +d.exp_var4;
    });


var axisNames = {
      pc1: "pc1" + " " + data[0].exp_var1,
      pc2: "pc2" + " " + data[0].exp_var2,
      pc3: "pc3" + " " + data[0].exp_var3,
      pc4: "pc4" + " " + data[0].exp_var4,
  };

var testnames = [
  "pc1",
  "pc2",
  "pc3",
  "pc4"
]
x.domain(d3.extent(data, function(d) { return d.pc1; })).nice();
y.domain(d3.extent(data, function(d) { return d.pc2; })).nice();

var tooltip = d3.select("body").append("div")
.attr("class", "tooltip")
.style("opacity", 0);

if (svg.selectAll(".y.axis")[0].length < 1){
svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
  .append("text")
    .attr("class", "label")
    .attr("x", width)
    .attr("y", -6)
    .style("text-anchor", "end")
    .text(axisNames["pc1"]);

svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
  .append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text(axisNames["pc2"])
} else {
svg.select(".x.axis").transition().call(xAxis);
svg.selectAll(".x.axis").selectAll("text.label").text(axisNames["pc1"]);

svg.select(".y.axis").transition().call(yAxis);
svg.selectAll(".y.axis").selectAll("text.label").text(axisNames["pc2"]);
}

var circles = svg.selectAll(".dot")
  .data(data);

circles.exit().remove();

circles.enter().append("circle")
  .attr("class", "dot")
  .attr("r", 3.5)

  circles.transition()
  .attr("cx", function(d) { return x(d.pc1); })
  .attr("cy", function(d) { return y(d.pc2); })
  .style("fill", function(d) { return color(d.sample[0]); })

circles.on("mouseover", function(d) {
          tooltip.transition()
               .duration(200)
               .style("opacity", .9);
          tooltip.html(d.sample)
               .style("left", (d3.event.pageX + 5) + "px")
               .style("top", (d3.event.pageY - 28) + "px");
      })
  .on("mouseout", function(d) {
          tooltip.transition()
               .duration(500)
               .style("opacity", 0);
    });


var legend = svg.selectAll(".legend")
  .data(color.domain())
  .enter().append("g")
  .attr("class", "legend")
  .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });


legend.append("rect")
  .attr("x", width)
  .attr("width", 18)
  .attr("height", 18)
  .style("fill", color);

legend.append("text")
  .attr("x", width - 6)
  .attr("y", 9)
  .attr("dy", ".35em")
  .style("text-anchor", "end")
  .text(function(d) { return d; });

if (document.getElementsByName("xAx").length == 0){
  var dd_x = d3.select("#xaxis_select").append("select")
                    .attr("name", "xAx");

  var options_x = dd_x.selectAll("option")
                        .data(testnames)
                        .enter()
                        .append("option");
    options_x.text(function (d) { return d; })
            .attr("value", function (d) { return d; });

  var dd_y = d3.select("#yaxis_select").append("select")
                    .attr("name", "yAx");

  var options_y = dd_y.selectAll("option")
                      .data(testnames)
                      .enter()
                      .append("option");
    options_y.text(function (d) { return d; })
            .attr("value", function (d) { return d; });

    var batch_list = d3.selectAll("label")
                        .data(data)
                        .enter()
                        .append("label")
        batch_list.text(function (d) { return d.sample; });

    var sample_batch = d3.selectAll("label")
                        .append("input")
                        .attr("style", "width: 30px")
                        .attr("name", "batch")

} else {
  var drop_downX = d3.select("#xaxis_select")
  var optionsX = drop_downX.selectAll("option")
                    .data(testnames);
                 optionsX.exit().remove();
                 optionsX.enter().append("option");
                 optionsX.text(function (d) { return d; })
                          .attr("value", function (d) { return d; });

  var drop_downX = d3.select("#xaxis_select")
  var optionsX = drop_downX.selectAll("option")
                    .data(testnames);
                optionsX.exit().remove();
                optionsX.enter().append("option");
                optionsX.text(function (d) { return d; })
                         .attr("value", function (d) { return d; });

}

d3.select("[name=xAx]").on("change", function(){
xAxy = this.value;
console.log(xAxy)
x.domain(d3.extent(data, function(d) { return d[xAxy]; })).nice();

svg.select(".x.axis").transition().call(xAxis);

svg.selectAll(".dot").transition().attr("cx", function(d) {
    return x(d[xAxy]);
});
svg.selectAll(".x.axis").selectAll("text.label").text(axisNames[xAxy]);
});

d3.select("[name=yAx]").on("change", function(){
yAxy = this.value;
console.log(yAxy)
y.domain(d3.extent(data, function(d) { return d[yAxy]; })).nice();
svg.select(".y.axis").transition().call(yAxis);
svg.selectAll(".dot").transition().attr("cy", function(d) {
    return y(d[yAxy]);
});
svg.selectAll(".y.axis").selectAll("text.label").text(axisNames[yAxy]);
});
};
