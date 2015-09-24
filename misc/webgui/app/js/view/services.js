window.Chains = window.Chains || {};
window.Chains.View = window.Chains.View || {};

window.Chains.View.Services = function(app) {

    var self = this;

    self.services = ko.observableArray();

    var Service = function(data) {

        var self = this;

        self.name = ko.observable(data.name);
        self.className = ko.observable(data['class']);
        self.manager = ko.observable(data.manager);
        self.online = ko.observable(data.online);
        self.autostart = ko.observable(data.autostart);

    }

    self.resume = function() {
        self.load();
    }

    self.load = function() {

        app.backend.get('/services', function(response){
            self.services([]);
            for(var id in response) {
                var service = new Service(response[id]);
                self.services.push(service);
            }
        });

    }

    // Init

    ko.applyBindings(self, $('#view-services').get(0));

};
