window.Chains = window.Chains || {};

window.Chains.Backend = function(baseUrl) {

    var self = this;

    self.baseUrl = baseUrl;

    self.call = function(method, url, data, callback) {

        if (typeof(data) == 'function') {
            callback = data;
            data = {};
        }

        $.ajax(self.baseUrl + url, {
            data: data ? JSON.stringify(data) : null,
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
