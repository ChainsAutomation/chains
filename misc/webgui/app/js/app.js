window.Chains = window.Chains || {};

window.Chains.App = function() {

    var self = this;

    self.backend = new window.Chains.Backend();

    self.services = new window.Chains.Services(self);
    self.managers = new window.Chains.Managers(self);
    self.reactors = new window.Chains.Reactors(self);
    self.state    = new window.Chains.State(self);

    self.views          = {};
    self.views.services = new window.Chains.View.Services(self);
    self.views.system   = new window.Chains.View.System(self);
    self.views.state    = new window.Chains.View.State(self);

    self.setView = function(view) {
        $('.view').hide();
        $('#view-' + view).show();
        if (self.views[view] && self.views[view].resume)
            self.views[view].resume();
    }

    // Init

    self.routes = function() {

        routie('/services', function(date) {
            self.setView('services');
        });

        routie('/system', function(date) {
            self.setView('system');
        });

        routie('/state', function(date) {
            self.setView('state');
        });

    }

    self.init = function() {
        ko.applyBindings(self);
        self.routes();
        self.setView('index');
        self.services.load(function(){
            self.managers.load(function(){
                self.reactors.load(function(){
                    self.state.load(function(){
console.log('all done!');
                    });
                });
            });
        });
    }

    self.init();

};

$(document).ready(function(){

    window.Chains.app = new window.Chains.App();

});
