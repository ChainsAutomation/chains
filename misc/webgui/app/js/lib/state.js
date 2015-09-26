window.Chains = window.Chains || {};

window.Chains.State = function(app) {

    var self = this;

    self.data = ko.observableArray();

    self.load = function(callback) {
        app.backend.get('/state', function(response){
            self.data(response.data);
            if (callback)
                callback();
        });

    }

}
