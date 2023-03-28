
//problem
function formatProblemData_problem(data) {
    $("p.p_id").html("Problem ID: " + data.problem_id + "<a href=\"" + data.problem_url + "\"><span class='material-symbols-outlined'>download</span></a>");
    $("p.d_id").html("Domain ID: " + data.domain_id + "<a href=\"" + data.domain_url + "\"><span class='material-symbols-outlined'>download</span></a>");
    $("h1.title").html(data.domain + "/" + data.problem);
    tags = data.tags.substring(1, (data.tags.length - 1));
    tags = tags.split(",").map(x => "<code>" + x + "</code>")
    tagstring = ""
    for (let index = 0; index < tags.length; index++) {
        tagstring += tags[index];
    }
    if (tagstring.length > 13) {
        $("p.tags").html("Problem tags: " + tagstring);
    } else {
        $("p.tags").html("Problem tags: None");
    }
    $("h4.d_link").html("<a href=\"/html/classical/domain/" + data.domain_id + "\">" + data.domain + "</a>");
    $("details.lowerbound").html("<summary>Lower bound: " + data.lower_bound + "</summary>" + data.lower_bound_description);
    $("details.upperbound").html("<summary>Upper bound: " + data.upper_bound + "</summary>" + data.upper_bound_description);
    $("details.av_ef_w").html("<summary>Average effective width: " + data.average_effective_width + "</summary>" + data.average_effective_width_description);
    $("details.max_ef_w").html("<summary>Maximum effective width: " + data.max_effective_width + "</summary>" + data.max_effective_width_description);
}

function formatDomainData_problem(domain_data) {
    $("p.d_desc").html(domain_data.description);
    d_tags = domain_data.tags.substring(1, (domain_data.tags.length - 1));
    d_tags = d_tags.split(",").map(x => "<code>" + x.substring(2, x.length - 1) + "</code>, ")
    d_tagstring = ""
    for (let index = 0; index < d_tags.length; index++) {
        d_tagstring += d_tags[index];
    }
    $("p.d_tags").html("Domain tags: " + d_tagstring);
}

function formatPlanData_problem(plan_data) {
    plan = plan_data.plan.split("\n");
    console.log(plan);
    if (plan[plan.length - 2].includes("cost = ")) {
        cost = plan[plan.length - 2].split("= ")[1].split(" ")[0];
        $("h3.plan_moves").html("Plan (" + cost + ")");
    } else {
        $("h3.plan_moves").html("Plan (" + plan.length + ")")
    }
    plan = plan.map(x => x + "<br>")
    planstring = ""
    for (let index = 0; index < plan.length; index++) {
        planstring += plan[index];
    }
    $("p.plan").html(planstring);
}

//domain
function formatDomainData_domain(data) {
    $("p.id").html("Domain ID: " + data.domain_id);
    $("h1.title").html(data.domain_name);
    $(".desc").html(data.description);
    d_tags = data.tags.substring(1, (data.tags.length - 1));
    d_tags = d_tags.split(",").map(x => "<code>" + x.substring(2, x.length - 1) + "</code>, ")
    d_tagstring = ""
    for (let index = 0; index < d_tags.length; index++) {
        d_tagstring += d_tags[index];
    }
    $("p.tags").html("Domain tags: " + d_tagstring);
}

function formatProblems_domain(data) {
    problemsList = ""
    // sort based on the data[index].problem field
    data.sort(function (a, b) {
        return a.problem.localeCompare(b.problem);
    });
    for (let index = 0; index < data.length; index++) {
        problemsList += "<a href=\"/html/classical/problem/" + data[index].problem_id + "\"><h4>" + data[index].problem + "</h4></a>";
    }
    $("div.problemlist").html(problemsList);
}

//collection
function formatCollectionData_collection(data) {
    $("p.id").html("Collection ID: " + data.collection_id);
    $("h1.title").html(data.collection_name);
    $(".desc").html(data.description);
}

function formatDomainData_collection(data, index) {
    resultString = "<a href=\"/html/classical/domain/" + data.domain_id + "\"><h4>" + data.domain_name + "</h4></a><p>" + data.description + "</p>";
    $("div.domain" + index).html(resultString);
}

//getters

//problem
function getDomain_problem(domainno) {
    $.getJSON('http://api.planning.domains/json/classical/domain/' + domainno, function (data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
        formatDomainData_problem(data);
    });
}

function getPlan_problem(problemno) {
    $.getJSON('https://api.planning.domains/json/classical/plan/' + problemno, function (data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
        formatPlanData_problem(data);
    });
}

//domain
function getProblems_domain(domainno) {
    $.getJSON('http://api.planning.domains/json/classical/problems/' + domainno, function (data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
        formatProblems_domain(data);
    });
}

//collection
function getDomain_collection(domainno, index) {
    $.getJSON('http://api.planning.domains/json/classical/domain/' + domainno, function (data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
        formatDomainData_collection(data, index);
    });
}

//main functions

//problem
function getProblem(problemno) {
    $.getJSON('http://api.planning.domains/json/classical/problem/' + problemno, function (data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
        formatProblemData_problem(data);
        getDomain_problem(data.domain_id);
        getPlan_problem(problemno);
    });
}

//domain
function getDomain(domainno) {
    $.getJSON('http://api.planning.domains/json/classical/domain/' + domainno, function (data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
        formatDomainData_domain(data);
        getProblems_domain(domainno);
    });
}

//collection

function getDomains_collection(collectionno) {
    $.getJSON('http://api.planning.domains/json/classical/domains/' + collectionno, function (data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;

        domainsListDivs = ""
        for (let index = 0; index < data.length; index++) {
            domainsListDivs += "<div class = domain" + index + "></div>";
        }
        $("div.domainlist").html(domainsListDivs);
        for (let index = 0; index < data.length; index++) {
            formatDomainData_collection(data[index], index);
        }
    });
}
function getCollection(collectionno) {
    $.getJSON('http://api.planning.domains/json/classical/collection/' + collectionno, function (data) {
        console.log(data);
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
        formatCollectionData_collection(data);
        getDomains_collection(collectionno);
    });
}
