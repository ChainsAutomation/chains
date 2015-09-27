window.Chains = window.Chains || {};

window.Chains.Backend = function() {

    var self = this;

    self.call = function(method, url, data, callback) {

        var baseUrl = '/api';

console.log('backend.call:',baseUrl+url);
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

    self.get = function(url, data) {
        self.call('GET', url, data);
    }

    self.post = function(url, data) {
        self.call('POST', url, data);
    }

}
