window.Chains = window.Chains || {};

window.Chains.Reactors = function(app) {

    var self = this;

    self.Reactor = function(data) {

        var self = this;

        self.id = ko.observable(data.id);
        self.online = ko.observable(data.online);

    }

    self.data = ko.observableArray();

    self.load = function(callback) {
        app.backend.get('/reactors', function(response){
            self.data([]);
            for(var id in response) {
                self.data.push(new self.Reactor(response[id]));
            }
            if (callback)
                callback();
        });

    }

}
