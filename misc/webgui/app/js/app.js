window.Chains = window.Chains || {};

window.Chains.App = function() {

    var self = this;

    self.backend = new window.Chains.Backend();
    self.socket = io.connect('http://' + window.location.hostname + ':7890');

    self.services = new window.Chains.Services(self);
    self.managers = new window.Chains.Managers(self);
    self.reactors = new window.Chains.Reactors(self);
    self.state    = new window.Chains.State(self);

    self.views          = {};
    self.views.services = new window.Chains.View.Services(self);
    self.views.system   = new window.Chains.View.System(self);
    self.views.state    = new window.Chains.View.State(self);
    self.views.devices  = new window.Chains.View.Devices(self);

    self.setView = function(view) {
        $('.view').hide();
        $('#view-' + view).show();
        if (self.views[view] && self.views[view].resume)
            self.views[view].resume();
    }

    // Init

    self.routes = function() {
        routie('/', function(date) {
            self.setView('index');
        });
        routie('/services', function(date) {
            self.setView('services');
        });
        routie('/system', function(date) {
            self.setView('system');
        });
        routie('/state', function(date) {
            self.setView('state');
        });
        routie('/devices', function(date) {
            self.setView('devices');
        });
    }

    self.init = function() {

        ko.applyBindings(self);

        self.setView('index');
        self.routes();

        self.services.load(function(){
            self.managers.load(function(){
                self.reactors.load(function(){
                    self.state.load(function(){
                        console.log('Loaded...');
                    });
                });
            });
        });

        self.socket.on('sa.web.reload', function() {
            console.log('reloading');
            document.location.reload();
        });

    }

    self.init();

};
