
function fetch_problems(qs, parent) {
    $.getJSON('http://api.planning.domains'+qs, function(data) {
        console.log('Problem data: ' + data);
    });
}

function fetch_domains(qs, parent) {
    $.getJSON('http://api.planning.domains'+qs, function(data) {
        console.log('Domain data:' + data);
    });
}

