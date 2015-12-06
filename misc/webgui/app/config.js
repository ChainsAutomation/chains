window.Chains = window.Chains || {};

window.Chains.Config = function() {

    var self = this;

    self.restUrl   = '/api';
    self.socketUrl = 'http://' + window.location.hostname + ':7890';
    
    // This function will run *before* webgui initializes.
    // You can add custom code, plugins etc, here.
    self.init = function(app) {

        /* Example: Add a custom view:

        // Add item to navbar
        app.navbar.push({
            url: '#/hello', name: 'Hello World'
        });

        // Add a route for it
        app.router('/test', function(){ app.setView('hello'); });

        // Create the view model
        app.views.hello = new function(){

            this.text = ko.observable('Hello');
            this.click = function() { this.text('World'); }

        };

        // Add the view html
        var view = $(
            '<div id="view-hello" class="view">' +
            '<h1>Example view</h1>' +
            '<div>Text: <span data-bind="text: views.hello.text"></span></div>' +
            '<button class="btn btn-primary" data-bind="click: views.hello.click"></button>' +
            '</div>'
        );
        view.appendTo($('#views'));

        */

    }

};
