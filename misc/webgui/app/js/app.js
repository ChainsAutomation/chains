window.Chains = window.Chains || {};

window.Chains.App = function() {

    var self = this;

    self.backend = new window.Chains.Backend();
    self.views = {};
    self.views.services = new window.Chains.View.Services(self);
    self.views.managers = new window.Chains.View.Managers(self);

    self.setView = function(view) {
        $('.view').hide();
        $('#view-' + view).show();
        if (self.views[view])
            self.views[view].resume();
    }

    // Init

    self.setView('index');

    routie('/services', function(date) {
        self.setView('services');
    });

    routie('/managers', function(date) {
        self.setView('managers');
    });

    console.log('started');

};

$(document).ready(function(){

    window.Chains.app = new window.Chains.App();

});
