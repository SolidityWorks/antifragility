var row_index = 0;
function addNextData() {
    console.log(row_index);
    row_index++;
    document.button_form.row.value = row_index;
}

var edges;
var network;
var container;
var options, data;
var edge_ids;

function drawGraph() {
    var container = document.getElementById('mynetwork');
    var nodes = {{nodes|safe}};
    edges = {{edges|safe}};

    var e_values = [];

    console.log("edges: " + e_values);

    data = {nodes: nodes, edges: edges};
    var options = {{options|safe}};

    network = new vis.Network(container, data, options);
    return network;
}


function getEdges() {
    old_edges = {};
    for (var i = 0; i < edges.length; i++) {
        old_edges[i] = edges[i]["width"];
    }
    return old_edges;
}

function outputUpdate(vol) {
    document.querySelector('#volume').value = vol;
    updateEdges(vol);
}

function updateEdges(vol) {
    console.log("Updating edges based off original widths of " + JSON.stringify(edge_ids));
    for (var i = 0; i < edges.length; i+2) {

        var originalVal = old_edges[i];
        console.log("original value: " + originalVal);
        edges[i]["width"] = originalVal * 2;
        edges[i]["label"] = parseFloat();
        console.log("new edge width: " + edges[i]["width"]);

    }

    data.edges = edges;
    console.log(data);
    network.setData(data);
}

new_network = drawGraph();
old_edges = getEdges();
