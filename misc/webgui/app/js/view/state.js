window.Chains = window.Chains || {};
window.Chains.View = window.Chains.View || {};

window.Chains.View.State = function(app) {

    var self = this;

    // todo: instead of making huge computed, bind to each item in state
    // so that update of one device only triggers recalc/redraw of that device

    self.data = ko.computed(function() {
        var result = [];
        var data = app.state.data();
        for(var i=0; i<data.length; i++) {
            var srv = {
                serviceId: data[i].id(),
                devices: []
            };
            var devs = data[i].devices();
            for(var j=0; j < devs.length; j++) {
                var dev = {device: devs[j].id(), data: []};
                var devdata = devs[j].data();
                for (var key in devdata) {
                    var entry = {key: key, data: devdata[key]};
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
