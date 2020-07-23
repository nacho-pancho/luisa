/* eslint-sourceType: module */

class barChart {

    /**
     * Creates an instance of barChart.
     * @param {string} baseSelector Selector del contenedor 
     * @param {object} box   Por ahora, un campo "margin" - top, left, bottom, right otro "svg" con height y width. svg.width se calcula en función barDef.barWidth y barPadding y el los margin si no está.
     * @param  {object} barDef {barPadding: separación entre barras, barWidth: ancho de las barras}
     * @param {string} idSvg : identificación del svg. 
     * 
     * @memberOf barChart
     */
    constructor(baseSelector, dataset,barDef,legends, box,idSvg) {
        barChart.count = (++barChart.count) || 1;
        this.count = barChart.count;
        this.lChartSpaceName = `chart_${this.count}`;
        this.svgName = idSvg || "svg_" + this.count;
        this.gChartSpace = $(baseSelector).append(`<div id="${this.lChartSpaceName}" style="overflow:auto;">`);
        this.lChartSpace = $(`#${this.lChartSpaceName}`);
        this.lChartSpace.append(`<svg id="${this.svgName}">`);
        this.jlSvg = this.lChartSpace.find("#svg_" + barChart.count);
        this.lSvg = this.jlSvg[0];
        this.box = Object.assign({ "margin": { top: 10, right: 10, bottom: 10, left: 10 },"svg":{"height":400}},box);
        this.barDef = Object.assign({"barPadding":5,"barWidth":15},barDef);
        this.dataset = dataset;
        this.size=dataset.length+2;
        this.legends=legends || {"x":"Valores en X","y":"Valores en Y"};
        this.barSpaceName = `barSpace_${this.count}`;
    }
    /**
     * Dibuja efectivamente el gráfico en el selector que se pasó.
     * 
     * 
     * @memberOf barChart
     */
    draw(){
        // simplificación de nombres :-)
        let margin=this.box.margin;
        let barWidth = this.barDef.barWidth;
        let barPadding = this.barDef.barPadding;
        // Algunos colores
        let blue = d3.color("blue");
        let green = d3.color("green");
        // El ancho del área del gráfico
        let realWidth = this.barDef.barWidth * this.size;
        // El ancho exterior del SVG 
        let svgWidth = this.box.svg.width || realWidth + this.box.margin.left + this.box.margin.right;
        // El alto exterior del SVG
        let svgHeight = this.box.svg.height;
        // El alto del área del gráfico
        let realHeight = svgHeight - margin.top - margin.bottom;

        // el SVG versión d3.
        let svg = d3.select(`#${this.jlSvg.attr("id")}`)
            .attr("width", svgWidth)
            .attr("height", svgHeight)
            .attr("class", "bar-chart");

        // Grafico
        let g = svg.append("g")
            .attr("id", "realChart")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        
        // range para el x
        // Si el primer elemento es un objeto, se toma el campo x.
        // Si no es un objeto, entonces se toma la posición.
        let aux = this.dataset.concat([0,0,0]);
        let lRange=aux.map((d, i) => {
            //  console.log("range scale:", i, svgWidth * (i) / size.length);
            return realWidth * (i - 1) / this.size;
        });

        // Escalas y Ejes
        let scaleX = d3.scaleQuantize()
            .domain([0, this.size])
            .range(lRange)
            ;

        let axisX = d3.axisBottom(scaleX).ticks(this.size);


        //    let xAxisCall = d3.axisBottom(x)
        let ejeXChart = g.append("g")
            .attr("class", "x-axis")
            .attr("id", "ejeX")
            .attr("transform", "translate(" + 15 + "," + realHeight + ")");

        let scaleY = d3.scaleLinear()
            .domain([0, realHeight])
            .range([realHeight, margin.top]);

        let axisY = d3.axisLeft(scaleY);

        let ejeYChart = g.append("g")
            .attr("class", "y-axis")
            .attr("id", "ejeY")
            .attr("transform", "translate(" + 0 + "," + 0 + ")");

        // Se agrega el ejeY al grafico         
        ejeYChart = ejeYChart
            .call(axisY);

        // se agrega el ejeX al grafico.

        ejeXChart = ejeXChart
        .call(axisX);

        // Se ajusta el tamaño para que entre el ejeX totalmente. Esto hay que hacerlo después del call del ejeX
        // Gira las leyendas...
        let ticksEjeX = ejeXChart.selectAll(" g > text")
            .attr("transform", "rotate(-90,0,15)");

        ejeXChart.append("text")
            .text(this.legends.x)
            .attr("stroke", "black")
            .attr("class", "axis-title")
            .attr("transform", "translate(" + 50 + ", 0)")
            .attr("y", 50);

        ejeYChart.append("text")
            .text(this.legends.y)
            .attr("stroke", "black")
            .attr("class", "axis-title")
            .attr("transform", "translate(0," + (realHeight / 2 - 50) + ") rotate(-90)")
            .attr("y", -50);    

        // Recalcula la altura y el ancho
        let ejeX = document.querySelector("#ejeX");
        svg.attr("height", this.lSvg.getBBox().height + ejeX.getBBox().height + 50);
        let ejeY = document.querySelector("#ejeY");
        svg.attr("width", this.lSvg.getBBox().width + ejeY.getBBox().width + 50);
        g.attr("transform", g.attr("transform") + " translate(" + ejeY.getBBox().width + ",0)");
        //    // lSvg= document.querySelector("svg");
        //     svg.attr("height",parseInt(svg.attr("height"))+50+ ejeX.getBBox().height)
    
        var bars = g
            .append("g")
            .attr("transform", "translate(" + (barWidth - barPadding) * (barPadding / barWidth) + "," + (-ejeX.getBBox().height / 2 + 5) + ")")
            .attr("id", this.barSpaceName);
        
        bars = svg.select(`#${this.barSpaceName}`).selectAll("g")
            .data(this.dataset)
            .enter()
            .append("g");

        bars.append("rect")
            .attr("y", function (d) {
                return svgHeight - d
            })
            .attr("height", function (d) {
                return d;
            })
            .attr("width", barWidth - barPadding)
            .attr("fill", function (d) {
                if (d % 2 == 0) {
                    return green;
                } else {
                    return blue;
                }

            }
            )
            .attr("transform", function (d, i) {
                var translate = [(barWidth) * (i + 0.5), 0];
                return "translate(" + translate + ")";
            });

        bars.append("text")
            .attr("fill", "white")
            .text(function (d) { return d; })
            .attr("font-size", barWidth - 5)
            .attr("y", function (d) {
                return svgHeight - d + 2 * this.getBBox().width + 5;
            })
            .attr("x", function (d, i) {
                return this.getBBox().x + 4;
            })
            .attr("transform", function (d, i) {
                var translate = [(barWidth) * (i + 0.5), 0];
                return "translate(" + translate + ") rotate(-90," + (this.getBBox().x - 4) + "," + this.getBBox().y + ")";
            })
            .style("width", barWidth)
            .style("font-style", "italic")
            .style("text-align", "center");

    }
}