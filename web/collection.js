var VERSION = 0.4;

// Delay the version check just so we can be sure jquery is loaded
setTimeout(function(){
    $.getJSON('http://api.planning.domains/json/version', function(data) {
        if (VERSION != data.version)
            alert('Warning: Your javascript API library appears to be outdated! Please download the latest version.');
    });
}, 1000);

function formatCollectionData(data){
    $("p.id").html("Collection ID: "+data.collection_id);
    $("h1.title").html(data.collection_name);
    $("h3.desc").html(data.description);
}

function formatDomainData(data, index){
    resultString  = "<a href=\"domain.html?domain="+data.domain_id+"\"><h4>"+data.domain_name+"</h4></a><p>"+data.description+"</p>";
    $("div.domain"+index).html(resultString);
}

function getDomain(domainno, index){
    $.getJSON('http://api.planning.domains/json/classical/domain/'+domainno, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
            formatDomainData(data, index);
    });
}

function getCollection(collectionno){
    $.getJSON('http://api.planning.domains/json/classical/collection/'+collectionno, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            data = data.result;
            formatCollectionData(data);
            domainsListDivs = ""
            domains = data.domain_set.substring(1, data.domain_set.length-1).split(", ").map(x => Number(x));
            for (let index = 0; index < domains.length; index++) {
                domainsListDivs += "<div class = domain"+index+"></div>";
            }
            $("div.domainlist").html(domainsListDivs);
            for (let index = 0; index < domains.length; index++) {
                getDomain(domains[index], index);
            }
    });
}