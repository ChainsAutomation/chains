window.Chains = window.Chains || {};

window.Chains.App = function() {

    var self = this;

    window.Chains.instance = self;

    self.config = {
        restUrl:   '/api',
        socketUrl: 'http://' + window.location.hostname + ':7890'
    };

    self.router = routie;
    self.backend = null; // set in start()
    self.socket = null; // set in start()

    self.isSocketConnected = ko.observable(false);

    self.services = new window.Chains.Services(self);
    self.managers = new window.Chains.Managers(self);
    self.reactors = new window.Chains.Reactors(self);
    self.state    = new window.Chains.State(self);

    self.views          = {};
    self.views.services = new window.Chains.View.Services(self);
    self.views.system   = new window.Chains.View.System(self);
    self.views.state    = new window.Chains.View.State(self);
    self.views.devices  = new window.Chains.View.Devices(self);

    self.configure = function(key, data) {
        if (self.config[key] === undefined) {
            console.error('No such configurable key: ' + key);
            return;
        }
        self.config[key] = data;
    };

    self.setView = function(view) {
        $('.view').hide();
        $('#view-' + view).show();
        $('body').removeClass().addClass('active-view-' + view);
        if (self.views[view] && self.views[view].resume)
            self.views[view].resume();
    };

    self.navbar = ko.observableArray([
        { url: '#/devices', name: 'Devices' },
        { url: '#/services', name: 'Services' },
        { url: '#/system', name: 'System' },
        { url: '#/state', name: 'State' },
    ]);

    self.start = function() {

        self.backend = new window.Chains.Backend(self.config.restUrl);
        self.socket = io.connect(self.config.socketUrl);

        ko.applyBindings(self);
        self.setView('index');

        // Init routes

        self.router('/', function(){ self.setView('index'); });
        self.router('/devices', function(){ self.setView('devices'); });
        self.router('/services', function(){ self.setView('services'); });
        self.router('/system', function(){ self.setView('system'); });
        self.router('/state', function(){ self.setView('state'); });

        // Load backend data

        self.services.load(function(){
            self.managers.load(function(){
                self.reactors.load(function(){
                    self.state.load(function(){
                        console.log('Loaded...');
                    });
                });
            });
        });

        // Socket events

        self.socket.on('sa.web.reload', function() {
            console.log('reloading');
            document.location.reload();
        });

        self.socket.on('service-event', function(data) {

            var attrs = {};

            for(var key in data) {
                if (key == 'service' || key == 'device' || key == 'data' || key == 'key')
                    continue;
                attrs[key] = data[key];
            }

            self.state.set(
                data.service,
                data.device,
                data.data,
                attrs
            );

        });

        self.socket.on('service-heartbeat', function(data) {
            // if (data == 2) service is still online
        });

        // Socket connection status

        setInterval(function(){
            self.isSocketConnected(self.socket.socket.connected);
        }, 2000);
    };

};
