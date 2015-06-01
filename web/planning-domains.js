
var headings = {'id': 'ID',
                'prob_name': 'Problem',
                'lower_bound': 'Lower Bound',
                'upper_bound': 'Upper Bound',
                'effective_width': 'Width',
                'hplus': 'H-Plus',
                'dom_name': 'Domain',
                'description': 'Description',
                'requirements': 'Requirements',
                'name': 'Collection',
                'domain_set': 'Domain Set',
                'ipc': 'IPC'
};

var default_problem_headings = ['id','prob_name','lower_bound','upper_bound'];
var default_domain_headings = ['id', 'dom_name', 'requirements', 'description'];
var default_collection_headings = ['id', 'name', 'ipc', 'description'];

function val(v) {
    if (v == null)
        return '-';
    else
        return v;
}

function format_problems(data, heads, select_func) {
    if (typeof heads === 'undefined')
        heads = default_problem_headings;
    return format_table(data.sort(function(a,b){return a.prob_name.localeCompare(b.prob_name)}), heads, select_func);
}

function format_domains(data, heads, select_func) {
    if (typeof heads === 'undefined')
        heads = default_domain_headings;
    return format_table(data.sort(function(a,b){return a.dom_name.localeCompare(b.dom_name)}), heads, select_func);
}

function format_collections(data, heads, select_func) {
    if (typeof heads == 'undefined')
        heads = default_collection_headings;
    return format_table(data.sort(function(a,b){return a.id - b.id}), heads, select_func);
}

function format_table(data, heads, select_func) {

    var html, i, j;

    html  = '<table class="table table-hover">\n';
    html += '<thead><tr>\n';
    for (i = 0; i < heads.length; i++) {
        html += '<th>' + headings[heads[i]] + '</th>\n';
    }
    html += '</tr></thead>\n';

    html += '<tbody>\n';
    for (i = 0; i < data.length; i++) {

        if (typeof select_func === 'undefined')
            html += '<tr>';
        else
            html += '<tr style="cursor:pointer" onclick="'+select_func+'('+data[i].id+')">';

        for (j = 0; j < heads.length; j++) {
            html += '<td>' + val(data[i][heads[j]]) + '</td>';
        }
        html += '</tr>';
    }
    html += '</tbody>\n';

    html += '</table>';

    return html;
}



function fetch_problems(qs, parent, select_func) {
    $.getJSON('http://api.planning.domains'+qs, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            $(parent).html(format_problems(data.result,
                                           default_problem_headings,
                                           select_func));
    });
}

function fetch_domains(qs, parent, select_func) {
    $.getJSON('http://api.planning.domains'+qs, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            $(parent).html(format_domains(data.result,
                                          default_domain_headings,
                                          select_func));
    });
}

function fetch_collections(qs, parent, select_func) {
    $.getJSON('http://api.planning.domains'+qs, function(data) {
        if (data.error)
            $(parent).html('Error:' + data.message);
        else
            $(parent).html(format_collections(data.result,
                                              default_collection_headings,
                                              select_func));
    });
}

function _navigator_dom2prob(did) {
    window.nav_prev_step = _navigator_col2dom;
    $('#nav-back-button').show();
    $(window.nav_parent).html('Loading...');
    fetch_problems('/problems/'+did, window.nav_parent, window.nav_func);
}

function _navigator_col2dom(cid) {
    window.nav_prev_step = _navigator_cols;
    window.nav_prev_setting = cid;
    $('#nav-back-button').show();
    $(window.nav_parent).html('Loading...');
    fetch_domains('/domains/'+cid, window.nav_parent, '_navigator_dom2prob');
}

function _navigator_cols() {
    $('#nav-back-button').hide();
    $(window.nav_parent).html('Loading...');
    fetch_collections('/collections', window.nav_parent, '_navigator_col2dom');
}

function _navigator_back() {
    window.nav_prev_step(window.nav_prev_setting);
}

function insert_navigator(parent, select_func) {
    window.nav_parent = '#sub-' + parent.slice(1);
    window.nav_func = select_func;
    $(parent).html('<button id="nav-back-button" onclick="_navigator_back()" type="button" class="btn btn-primary">Back</button><div id="' + window.nav_parent.slice(1) + '"></div>');
    _navigator_cols();
}

