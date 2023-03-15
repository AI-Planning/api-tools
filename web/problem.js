
var VERSION = 0.4;

// Delay the version check just so we can be sure jquery is loaded
setTimeout(function(){
    $.getJSON('http://api.planning.domains/json/version', function(data) {
        if (VERSION != data.version)
            alert('Warning: Your javascript API library appears to be outdated! Please download the latest version.');
    });
}, 1000);

function formatProblemData(data){
    $("p.p_id").html("Problem ID: "+data.problem_id+ "<a href=\"" + data.problem_url + "\"><span class='material-symbols-outlined'>download</span></a>");
    $("p.d_id").html("Problem ID: "+data.domain_id+ "<a href=\"" + data.domain_url + "\"><span class='material-symbols-outlined'>download</span></a>");
    $("h1.title").html(data.domain+"/"+data.problem);
    tags = data.tags.substring(1, (data.tags.length-1));
    tags = tags.split(",").map(x => "<code>"+x+"</code>")
    tagstring = ""
    for (let index = 0; index < tags.length; index++) {
        tagstring += tags[index];
    }
    console.log(tagstring);
    if(tagstring.length > 13){
        $("p.tags").html("Problem tags: " + tagstring);
    } else {
        $("p.tags").html("Problem tags: None");
    }
    $("h4.d_link").html("<a href=\"http://api.planning.domains/json/classical/domain/"+data.domain_id+"\">"+data.domain+"</a>");
    $("details.lowerbound").html("<summary>Lower bound: "+data.lower_bound+"</summary>"+data.lower_bound_description);
    $("details.upperbound").html("<summary>Upper bound: "+data.upper_bound+"</summary>"+data.upper_bound_description);
    $("details.av_ef_w").html("<summary>Average effective width: "+data.average_effective_width+"</summary>"+data.average_effective_width_description);
    $("details.max_ef_w").html("<summary>Maximum effective width: "+data.max_effective_width+"</summary>"+data.max_effective_width_description);
}

function formatDomainData(domain_data){
    $("p.d_desc").html(domain_data.description);
    d_tags = domain_data.tags.substring(1, (domain_data.tags.length-1));
    d_tags = d_tags.split(",").map(x => "<code>"+x.substring(2, x.length-1)+"</code>, ")
    d_tagstring = ""
    for (let index = 0; index < d_tags.length; index++) {
        d_tagstring += d_tags[index];
    }
    $("p.d_tags").html("Domain tags: " + d_tagstring);
}

function formatPlanData(plan_data){
    plan = plan_data.plan.split("\n");
    plan = plan.map(x => x + "<br>")
    planstring = ""
    for (let index = 0; index < plan.length; index++) {
        planstring += plan[index];
    }
    $("p.plan").html(planstring);
}

function getDomain(domainno){
    $.getJSON('http://api.planning.domains/json/classical/domain/'+domainno, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
            formatDomainData(data);
    });
}

function getPlan(problemno){
    $.getJSON('https://api.planning.domains/json/classical/plan/'+problemno, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
            formatPlanData(data);
    });
}

//main function from which everything is called
function getProblem(problemno){ 
    $.getJSON('http://api.planning.domains/json/classical/problem/'+problemno, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
            formatProblemData(data);
            getDomain(data.domain_id);
            getPlan(problemno);
    });
}