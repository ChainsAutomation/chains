window.Chains = window.Chains || {};

window.Chains.Backend = function() {

    var self = this;

    self.call = function(method, url, data, callback) {

        var baseUrl = '/api';

        if (typeof(data) == 'function') {
            callback = data;
            data = {};
        }

        $.ajax(baseUrl + url, {
            data: data ? JSON.stringify(data) : {},
            dataType: 'json',
            method: method,
            contentType: "application/json",
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
