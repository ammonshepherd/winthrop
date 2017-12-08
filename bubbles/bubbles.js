$(document).ready(function () {
  var bubbleChart = new d3.svg.BubbleChart({
    supportResponsive: true,
    //container: => use @default
    size: 2000,
    //viewBoxSize: => use @default
    innerRadius: 500 / 3.5,
    //outerRadius: => use @default
    radiusMin: 50,
    radiusMax: 200,
    //intersectDelta: use @default
    //intersectInc: use @default
    //circleColor: use @default
    data: {
      items: [
        {text: "Ander Theil", count: "3"}, 
        {text: "Apocalypsis Iesu Christi", count: "5"}, 
        {text: "Catalogus scriptorum Florentinorum", count: "3"}, 
        {text: "Cheiragogia", count: "2"}, 
        {text: "Colloquiorum", count: "3"}, 
        {text: "Fortalitium Scientiae", count: "2"}, 
        {text: "Gallicae linguae institutio", count: "3"}, 
        {text: "Isagoge optica", count: "1"}, 
        {text: "L'elixir des philosophes", count: "8"}, 
        {text: "Orbis Miraculum", count: "4"}, 
        {text: "The complaint of Roderyck Mors", count: "1"}, 
        {text: "The foure chiefest", count: "1"}, 
        {text: "The image of governance", count: "2"}, 
        {text: "Triga chemica", count: "2"}, 
        {text: "Variet di secreti", count: "2"}, 
        {text: "Veterinaria medicina", count: "3"}, 
        /*
        {text: "The Roman historie", count: "15"}, 
        {text: "Chronologia sacra", count: "20"}, 
        {text: "Flores", count: "21"},
        {text: "De republica Anglorum", count: "31"}, 
        {text: "The Triall of Witch-craft", count: "40"}, 
        {text: "Princeps", count: "52"}, 
        */
      ],
      eval: function (item) {return item.count;},
      classed: function (item) {return item.text.split(" ").join("");}
    },
    plugins: [
      {
        name: "lines",
        options: {
          format: [
            {// Line #0
              textField: "count",
              classed: {count: true},
              style: {
                "font-size": "28px",
                "font-family": "Source Sans Pro, sans-serif",
                "text-anchor": "middle",
                fill: "white"
              },
              attr: {
                dy: "0px",
                x: function (d) {return d.cx;},
                y: function (d) {return d.cy;}
              }
            },
            {// Line #1
              textField: "text",
              classed: {text: true},
              style: {
                "font-size": "14px",
                "font-family": "Source Sans Pro, sans-serif",
                "text-anchor": "middle",
                fill: "white"
              },
              attr: {
                dy: "20px",
                x: function (d) {return d.cx;},
                y: function (d) {return d.cy;}
              }
            }
          ],
          centralFormat: [
            {// Line #0
              style: {"font-size": "50px"},
              attr: {}
            },
            {// Line #1
              style: {"font-size": "30px"},
              attr: {dy: "40px"}
            }
          ]
        }
      }]
  });
});
