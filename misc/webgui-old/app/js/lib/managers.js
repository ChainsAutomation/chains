window.Chains = window.Chains || {};

window.Chains.Managers = function(app) {

    var self = this;

    self.Manager = function(data) {

        var self = this;

        self.id = ko.observable(data.id);
        self.online = ko.observable(data.online);

    }

    self.data = ko.observableArray();

    self.load = function(callback) {
        app.backend.get('/managers', function(response){
            self.data([]);
            for(var id in response) {
                self.data.push(new self.Manager(response[id]));
            }
            if (callback)
                callback();
        });
    }

}
