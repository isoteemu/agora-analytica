function show_node_info(id){
    // TODO: Kun modaali esittää jonkin, aseta "active" -luokka graphin nodelle. Vastaavasti poista dialogin sulkeutuessa.
    // Find correct node from nodes
    data = graph.nodes.find((x) => x.id == id);

console.log(data)

/*console.log(data.name)
console.log(data.vaalipiiri)
console.log(data.party)*/

color = node_color(data)
document.getElementById("modalheader").style.backgroundColor = color;

console.log(color)

$("#candidateName").text("Name: " + data.name)
$("#candidateNumber").text("Candidate number: " + data.number)
$("#candidateParty").text("Party: " + data.party)
$("#candidateConstituency").text("Constituency: " + data.constituency)

$("#candidateInformationModal").modal('show')
$('.modal-backdrop').removeClass("modal-backdrop");
$(".modal-dialog").draggable({
    "handle":".modal-header",
    "containment":"window"

function ui_init_filters(nodes) {
    // Kerää puolueet ja vaalipiirit solmuista
    const parties = []
    const constituencies = []

    console.log(nodes)

    nodes.forEach(node => {

        var party = node.party
        var constituency = node.constituency

        if (parties.indexOf(party) == -1) {
            parties.push(party)
        }
        if(constituencies.indexOf(constituency) == -1){
            constituencies.push(constituency)
        }
    });

    console.log(parties, constituencies)

    parties.forEach(function(party) {

        let list_item = $("<li><label>").text(party);
        let checkbox = $("<input type =\"checkbox\" checked>")
        checkbox.attr("name", "party");
        checkbox.attr("value", party);
        
        checkbox.on("click", function() {

            const filter_rules = {
                parties: [],
                constituencies: []
            }

            $("#filter-party input:not(:checked").each(function(){
                filter_rules['parties'].push($(this).val());
            })

            // Kutsu filtteröintiä.
            graph_filter(filter_rules)
        });
        list_item.prepend(checkbox)
        $("#filter-party").append(list_item);
    });

    constituencies.forEach(function(constituency) {
        let list_item = $("<li><label>").text(constituency);
        let checkbox = $("<input type =\"checkbox\" checked>")
        checkbox.attr("name", "constituency");
        checkbox.attr("value", constituency);

        checkbox.on("click", function() {
            

            const filter_rules = {
                parties: [],
                constituencies: []
            }

            $("#filter-constituency input:not(:checked").each(function(){
                filter_rules['constituencies'].push($(this).val());
            })

            graph_filter(filter_rules);
        })
        list_item.prepend(checkbox)
        $("#filter-constituency").append(list_item);
    });
}

const rel_el = $("#candidateRelated");
// Remove old html nodes.
$("> .candidate", rel_el).remove()

// Read template
const template = $("#candidateRelatedTemplate").html().trim();

// Find related candidates, and show nearest first.
graph.links.filter((x) => x.target.id == id || x.source.id == id).sort((a, b) => b.distance - a.distance ).forEach(function(link) {
    let node;
    let topic;
    // It's not known if current node is source or target, so check is needed.
    if (link.target.id == id) {
        node = link.source;
        topic = link.source_term;
    } else {
        node = link.target;
        topic = link.target_term;
    }

    // Create new element from template, and populate values.
    let el = $(template)
        .attr("title", node.number+": "+node.name+"\n"+node.party+"\n"+node.constituency)
        .click(() => show_node_info(node.id));
    $("img.node", el)
        .attr("src", node.image ? node.image : default_image)
        .attr("style", "border-color:"+node_color(node))
    $(".topic", el).text(topic);
    $(".name", el).text(node.name);

    // Append into a node tree.
    rel_el.append(el);

})
}