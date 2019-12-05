function show_node_info(id){
console.log("ddd", id)
d3.json("/api/node/"+id+".json", function(err, data){
console.log(data)

/*console.log(data.name)
console.log(data.vaalipiiri)
console.log(data.party)*/

$("#candidateName").text("Name: " + data.name)
$("#candidateNumber").text("Candidate number: " + "TODO: candidate number here ")
$("#candidateParty").text("Party: " + data.party)
$("#candidateConstituency").text("Constituency: " + data.constituency)

$("#candidateInformationModal").modal('show')

})
}