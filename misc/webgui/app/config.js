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
        app.router('/hello', function(){ app.setView('hello'); });

        // Create the view model
        app.views.hello = new function(){

            var self = this;

            self.text = ko.observable('Hello');
            self.click = function() { self.text('World'); }
            self.resume = function() { self.text('Hello'); }

        };

        // Add the view html
        var view = $(
            '<div id="view-hello" class="view">' +
            '<h1>Example view</h1>' +
            '<div>Text: <span data-bind="text: views.hello.text"></span></div>' +
            '<button class="btn btn-primary" data-bind="click: views.hello.click">Change text</button>' +
            '</div>'
        );
        view.appendTo($('#views'));

        */

    }

};
