window.Chains = {};
window.Chains.Backend = {};
window.Chains.Services = {};

window.Chains.Backend.call = function(method, url, data, callback) {

    var baseUrl = '/api';

    if (typeof(data) == 'function') {
        callback = data;
        data = {};
    }

    $.ajax(baseUrl + url, {
        data: data || {},
        dataType: 'json',
        method: method,
        success: function(result) {
            callback(result);
        }
    });

}

window.Chains.Backend.get = function(url, data) {
    window.Chains.Backend.call('GET', url, data);
}

window.Chains.Backend.post = function(url, data) {
    window.Chains.Backend.call('POST', url, data);
}

window.Chains.Services.list = function(callback) {
    window.Chains.Backend.get('/services', callback);
};

$(document).ready(function(){
    console.log('test...');
    window.Chains.Services.list(function(result){

        var e = $('#services');
        for(id in result) {
            var srv = result[id];
            if (!srv.id)
                continue;
            e.append(
                '<tr>' +
                '<td>' + srv.name + '</td>' +
                '<td class="service-' + (srv.online ? 'online' : 'offline') + '">' + 
                (srv.online ? 'Online' : 'Offline') + 
                '</td>' +
                '</tr>'
            );
        }

    });
});
