function show_node_info(id){
console.log("ddd", id)
d3.json("/api/node/"+id+".json", function(err, data){
console.log("kkkkkkk", data)

/*console.log(data.name)
console.log(data.vaalipiiri)
console.log(data.party)*/

color = node_color(data)
document.getElementById("modalheader").style.backgroundColor = color;

console.log(color)

$("#candidateName").text("Name: " + data.name)
$("#candidateNumber").text("Candidate number: " + data.candidatenumber)
$("#candidateParty").text("Party: " + data.party)
$("#candidateConstituency").text("Constituency: " + data.constituency)

$("#candidateInformationModal").modal('show')
$('.modal-backdrop').removeClass("modal-backdrop");
$(".modal-dialog").draggable({
    "handle":".modal-header",
    "containment":"window"
})
})
}
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