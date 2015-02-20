var App = function() {

    var self = this;

    self.socket = io.connect('/');

    self.socket.on('device-event', function(data) {
        self.renderMessage('device-event', data);
    });
    self.socket.on('daemon-status', function(data) {
        self.renderMessage('daemon-status', data);
    });

    self.renderMessage = function(type, data) {

        $(
              '<div style="border: 1px solid #ccc; padding: 0px; margin: 10px">'
			+ '<div style="background: green; color: white; font-weight: bold; padding: 10px">' + type + '</div>'
            + ' <div style="padding: 10px">' + JSON.stringify(data) + '</div>'
            + '</div>'
        ).appendTo('#container');

    }

};

var app = new App();
