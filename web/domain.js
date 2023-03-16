var VERSION = 0.4;

// Delay the version check just so we can be sure jquery is loaded
setTimeout(function(){
    $.getJSON('http://api.planning.domains/json/version', function(data) {
        if (VERSION != data.version)
            alert('Warning: Your javascript API library appears to be outdated! Please download the latest version.');
    });
}, 1000);

function formatDomainData(data){
    $("p.id").html("Domain ID: "+data.domain_id);
    $("h1.title").html(data.domain_name);
    $("h3.desc").html(data.description);
    d_tags = data.tags.substring(1, (data.tags.length-1));
    d_tags = d_tags.split(",").map(x => "<code>"+x.substring(2, x.length-1)+"</code>, ")
    d_tagstring = ""
    for (let index = 0; index < d_tags.length; index++) {
        d_tagstring += d_tags[index];
    }
    $("p.tags").html("Domain tags: " + d_tagstring);
}

function formatProblems(data){
    problemsList = ""
    for (let index = 0; index < data.length; index++) {
        problemsList += "<a href=\"problem.html?problem="+data[index].problem_id+"\"><h4>"+data[index].problem+"</h4></a>";
    }
    $("div.problemlist").html(problemsList);
}


function getProblems(domainno){
    $.getJSON('http://api.planning.domains/json/classical/problems/'+domainno, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
            formatProblems(data);
    });
}

//main function
function getDomain(domainno){
    $.getJSON('http://api.planning.domains/json/classical/domain/'+domainno, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
            formatDomainData(data);
            getProblems(domainno);
    });
}