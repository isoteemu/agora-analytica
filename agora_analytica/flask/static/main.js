function show_node_info(id){
console.log("ddd", id)
d3.json("/api/node/"+id+".json", function(err, data){
console.log(data)
})
    $("#ehdokastiedotmodal").modal("show")
}