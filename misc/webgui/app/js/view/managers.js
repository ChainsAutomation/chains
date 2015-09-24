window.Chains = window.Chains || {};
window.Chains.View = window.Chains.View || {};

window.Chains.View.Managers = function(app) {

    var self = this;

    self.managers = ko.observableArray();

    var Manager = function(data) {

        var self = this;

        self.id = ko.observable(data.id);
        self.online = ko.observable(data.online);

    }

    self.resume = function() {
        self.load();
    }

    self.load = function() {

        app.backend.get('/managers', function(response){
            self.managers([]);
            for(var id in response) {
                var manager = new Manager(response[id]);
                self.managers.push(manager);
            }
        });

    }

    // Init

    ko.applyBindings(self, $('#view-managers').get(0));

};
