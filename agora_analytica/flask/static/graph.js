

graph = {
    width: parseInt(window.innerWidth),
    height: parseInt(window.innerHeight),

    svg: null,

    node_radius: 15,
    distance: 50,
    strength: -30,

    zoom: null,
    simulation: null,
};

graph.reset = function() {
    graph.svg
        .attr("width", graph.width)
        .attr("height", graph.height);

    graph.simulation.force("link").distance(graph.distance)
    graph.simulation.force("charge").strength(graph.strength)

    graph.svg.selectAll("defs image.node-image")
        .attr("width", graph.node_radius * 2)
        .attr("height", graph.node_radius * 2),
    graph.svg.selectAll(".nodes circle")
        .attr("r", graph.node_radius)
    graph.simulation.force("collide").radius(graph.node_radius)

    graph.simulation.alpha(1).restart();
}

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
            distance: element.distance + graph.node_radius / 10 + 1,
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

            // Add topics. Source and target are reversed, so links are on opposite sides.
            if (x_attr['source_term']) {
                topics.push({
                    source: target,
                    target: source,
                    term: x_attr['source_term']
                });
            }
            if (x_attr['target_term']) {
                topics.push({
                    source: source,
                    target: target,
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

function graph_run() {

    if(nodes.length == 0 || links.length == 0 || parties.length == 0) return;

    // Link into nodes.
    graph.svg = d3.select("#graph svg");

    var defs = graph.svg.append("defs");
    defs.append("clipPath")
        .attr("id", "clip-circle")
        .append("circle")
            .attr("cx", 0)
            .attr("cy", 0)
            // .attr("r", graph.node_radius)

    for(n of nodes) {
        defs.append("pattern")
            .attr("id", "node-"+n.index+"-image")
            .attr("width", "100%")
            .attr("height", "100%")
            .append("image")
                .classed("node-image", true)
                .attr("preserveAspectRatio", "xMidYMid slice")
                .attr("xlink:href", n.image ? n.image : default_image)
                .attr("width", graph.node_radius * 2) 
                .attr("height", graph.node_radius * 2)

    }

    graph.zoom = d3.zoom()
        .on("zoom", function () {
            graph_layer.attr("transform", d3.event.transform)
        });

    let graph_layer = graph.svg.call(graph.zoom).append("g").attr("id", "graph_layer");

    let force = d3.forceManyBody()

    graph.simulation = d3.forceSimulation()
        .force("link", d3.forceLink()
            .distance(function(d) {return d.distance * graph.distance;}))
        .force("center", d3.forceCenter(graph.width / 2, graph.height / 2))
        .force("charge", force)
        .force("collide", d3.forceCollide(graph.node_radius)) 

        // Jos halutaan pallon muotoinen
        // .force("x", d3.forceX())
        // .force("y", d3.forceY())

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
                .append("text")
                    .text((d) => d.term);
    });

    var circles = node.append("circle")
        .attr("r", graph.node_radius)
        .attr("stroke", node_color)
        .attr("fill", (d) => "url(#node-"+ d.index +"-image)")
        // .call(d3.drag()
        //     .on("start", dragstarted)
        //     .on("drag", dragged)
        //     .on("end", dragended))
        .on("click", function(obj) {
            let g = d3.select(this.parentElement);
            let activate = !g.classed("active");

            console.group(obj.index, obj)
            let links = graph.simulation.force("link").links().filter((x) => obj == x.source || obj == x.target)
            links.forEach(function(x) {
                x.old_strength = x.strength;
                x.strength += 1;
                x.distance += 1;
                console.log(x.distance, x.strength);
            })

            console.groupEnd()
            var toggle = !g.classed("active");
            g.classed("active", activate);

            graph.reset();
        })

    var labels = node.append("text")
        .text(function(d) {
            return d.name + "\r\n(" + d.party +")";
        })
        .classed("node-info", true)
        .attr('x', graph.node_radius)
        .attr('y', graph.node_radius);

    node.append("title")
        .text(function(d) { return d.name+"\n"+d.party; });

    graph.simulation
        .nodes(nodes)
        .on("tick.graph", ticked)
        .force("link")
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

            const w = this.getBBox();

            // Align
            const s = Math.sin(atan)
            const c = Math.cos(atan)
            let y = s * (graph.node_radius + 2)// + (w.height / 2 * s);
            let x = c * (graph.node_radius + 2)// + (w.width / 2 * c); 
            // Center point is bottom left, make it "center"
            y -= w.height / 2;
            x += w.width / 2;
            // Push outside regarding box size
            y += w.height / 2 * s;
            x += w.width / 2 * c;

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
        graph.width = parseInt(window.innerWidth);
        graph.height = parseInt(window.innerHeight);

        svg.attr("width", graph.width)
           .attr("height", graph.height);
    });
    graph.reset();
}
