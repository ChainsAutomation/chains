window.Chains = {};
window.Chains.Backend = {};
window.Chains.Devices = {};

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

window.Chains.Device.list = function() {

    window.Chains.Backend.get('/devices', function(result) {
        console.log('devices result:', result);
    });

};
