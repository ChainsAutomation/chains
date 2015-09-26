window.Chains = window.Chains || {};
window.Chains.View = window.Chains.View || {};

window.Chains.View.State = function(app) {

    var self = this;

    self.data = ko.computed(function() {
        var result = [];
        var data = app.state.data();
        for(var serviceId in data) {
            var srv = {
                serviceId: serviceId, 
                devices: []
            };
            for(var device in data[serviceId]) {
                if (device == '_service')
                    continue;
                var dev = {device: device, data: []};
                for (var key in data[serviceId][device]) {
                    var entry = {key: key, data: data[serviceId][device][key]};
                    dev.data[dev.data.length] = entry;
                }
                srv.devices[srv.devices.length] = dev;
            }
            if (srv.devices.length > 0)
                result[result.length] = srv;
        }
        return result;
    });

}
