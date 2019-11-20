
var width = parseInt(window.innerWidth),
    height = parseInt(window.innerHeight);

var circleRadius = 15;

function process_links(data) {
    var links_map = {};
    
    var attrs = {};

    // Collect node links, from closest to furthest.
    data.sort((a, b) => a["distance"] - b["distance"] ).forEach((element) => {

        // Pointers to node indexes.
        source = element["source"];
        target = element["target"];
        let k = [parseInt(source), parseInt(target)].sort();

        if(!(source in links_map)) links_map[source] = [];
        if(!(target in links_map)) links_map[target] = [];
        if(!(k in attrs)) attrs[k] = {
            distance: element.distance + circleRadius / 10 + 1,
            source_term: element.source_term,
            target_term: element.target_term,
        };

        // Pointers
        let src_links = links_map[source];
        let trg_links = links_map[target];

        if( src_links.length < 3) src_links.push(target);
        if( trg_links.length < 3) trg_links.push(source);
    });

    for(let source in links_map) {
        for(let target of links_map[source]) {
            let [src, trg] = [parseInt(source), parseInt(target)].sort();
            let x_attr = attrs[[src,trg]]
            links.push(Object.assign({
                source: src,
                target: trg
            }, x_attr));

            // Add topics.
            if (x_attr['source_term']) {
                topics.push({
                    source: src,
                    target: trg,
                    term: x_attr['source_term']
                });
            }
            if (x_attr['target_term']) {
                topics.push({
                    source: trg,
                    target: src,
                    term: x_attr['target_term']
                });
            }
        }
    }
}

function node_color(d) {
    let party = parties.find(function(x) {
        if(x.itemLabel.includes(d.party)) return true; 
        if("itemAltLabel" in x) return x.itemAltLabel.includes(d.party)
    });
    let color = party && "sRGB_color_hex_triplet" in party ? "#"+party.sRGB_color_hex_triplet : "#CCC"

    return color;
}

function run() {

    if(nodes.length == 0 || links.length == 0 || parties.length == 0) return;

    // Link into nodes.
    var svg = d3.select("#graph svg")
        .attr("width", width)
        .attr("height", height);

    var defs = svg.append("defs");
    defs.append("clipPath")
        .attr("id", "clip-circle")
        .append("circle")
            .attr("cx", 0)
            .attr("cy", 0)
            .attr("r", circleRadius)

    for(n of nodes) {
        defs.append("pattern")
            .attr("id", "node-"+n.index+"-image")
            .attr("width", "100%")
            .attr("height", "100%")
            .append("image")
                .attr("preserveAspectRatio", "xMidYMid slice")
                .attr("xlink:href", n.image)
                .attr("width", circleRadius * 2) 
                .attr("height", circleRadius * 2);

    }

    var zoom = d3.zoom()
        .on("zoom", function () {
            graph_layer.attr("transform", d3.event.transform)
        });

    var graph_layer = svg.call(zoom).append("g").attr("id", "graph_layer");

    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink()
            .id(function(d) { return d.index; })
            .distance(function(d) {return d.distance * 30;}))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    var link = graph_layer.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter()
            .append("line")
            .attr("stroke-width", 1)

    var node = graph_layer.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(nodes)
        .enter().append("g")
            .classed("node", true)
            .attr("id", (d) => "node-"+d.index)

    let topic_nodes = node.select(function(e) {
        let g = d3.select(this);

        g.selectAll().append("g")
            .data(
                topics.filter((x) => x.source == g.data()[0].index)
            ).enter().append("g")
                .classed("topic", true)
                .attr("style", "outline: 1px black solid;")
                .append("text")
                    // .text(".")
                    .text((d) => d.term);
    });

    // var images = node.append("image")
    //     .attr("x", -circleRadius)
    //     .attr("y", -circleRadius)
    //     .attr("width", circleRadius * 2)
    //     .attr("height", circleRadius * 2)
    //     .attr("xlink:href", function(d) {
    //         if (d.image)
    //             return d.image;
    //         else   
    //             return "{{url_for("static", filename="default-person.png")}}";
    //     })
    //     .attr("clip-path", "url(#clip-circle)")

    var circles = node.append("circle")
        .attr("r", circleRadius)
        .attr("stroke", node_color)
        .attr("fill", (d) => "url(#node-"+ d.index +"-image)")
        // .call(d3.drag()
        //     .on("start", dragstarted)
        //     .on("drag", dragged)
        //     .on("end", dragended))
        .on("click", function(obj) {
            var g = d3.select(this.parentElement);
            var toggle = !g.classed("active");
            g.classed("active", toggle);
        })

    var labels = node.append("text")
        .text(function(d) {
            return d.name + "\r\n(" + d.party +")";
        })
        .classed("node-info", true)
        .attr('x', circleRadius)
        .attr('y', circleRadius);

    node.append("title")
        .text(function(d) { return d.name+"\n"+d.party; });

    simulation
        .nodes(nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(links);

    function ticked() {
        link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        })
        node.selectAll("g.topic").attr("transform", function(d) {
            const atan = Math.atan2(nodes[d.source].y - nodes[d.target].y, nodes[d.source].x - nodes[d.target].x)

            const s = this.getBBox();

            let y = Math.sin(atan) * (circleRadius + 5);
            let x = Math.cos(atan) * (circleRadius + 5);

            return "translate("+ x * -1 +","+ y * -1 +")"
        });
    }

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    d3.select(window).on("resize", function() {
        width = parseInt(window.innerWidth);
        height = parseInt(window.innerHeight);

        console.log("resize");

        svg.attr("width", width)
           .attr("height", height);

    });

}
