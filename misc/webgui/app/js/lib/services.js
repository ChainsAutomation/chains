window.Chains = window.Chains || {};

window.Chains.Services = function(app) {

    var self = this;

    self.Service = function(data) {

        var self = this;

        self.id = ko.observable(data.id);
        self.name = ko.observable(data.name);
        self.className = ko.observable(data['class']);
        self.manager = ko.observable(data.manager);
        self.online = ko.observable(data.online);
        self.autostart = ko.observable(data.autostart);

    };

    self.data = ko.observableArray();

    self.find = function(id) {
        var services = self.data();
        for(var i=0; i < services.length; i++) {
            if (services[i].id() == id)
                return services[i];
        }
        return;
    };

    self.getName = function(id) {
        var service = self.find(id);
        return service ? service.name() : '(' + id + ')';
    };

    self.load = function(callback) {
        app.backend.get('/services', function(response){
            self.data([]);
            for(var id in response) {
                self.data.push(new self.Service(response[id]));
            }
            if (callback)
                callback();
        });
    };

};
