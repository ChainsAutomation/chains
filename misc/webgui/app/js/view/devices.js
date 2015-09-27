window.Chains = window.Chains || {};
window.Chains.View = window.Chains.View || {};

window.Chains.View.Devices = function(app) {

    var self = this;

    self.groupBy = ko.observable('location');

    self.groupByOptions = ko.observableArray(['none','type','location']);

    self.Group = function(data) {

        var self = this;

        self.id = ko.observable(data.id);
        self.devices = ko.observableArray(data.devices);

        self.name = ko.computed(function(){
            var groupBy = app.views.devices.groupBy();
            switch (self.id()) {
                case 'none':
                    return groupBy == 'none' ? 'All devices' : '(Unknown ' + groupBy + ')';
                default:
                    return self.id();
            }
        });

    }

    self.Device = function(data) {

        var self = this;

        self.serviceId = ko.observable(data.serviceId);
        self.device    = ko.observable(data.device);
        self.type      = ko.observable(data.type);
        self.name      = ko.observable(data.name);
        self.location  = ko.observable(data.location);
        self._value     = ko.observable(data.value);

        // hack/todo: do something nice to cleanly and easily extend things with more types

        self.icon = ko.computed(function(){
            var prefix = '/images/type-icon/';
            switch (self.type()) {
                case 'lamp':
                    return prefix + (
                        self._value() > 0
                        ? 'lamp-on.svg'
                        : 'lamp-off.svg'
                    );
                case 'temperature':
                case 'humidity':
                    return prefix + self.type() + '.svg';
                default:
                    return prefix + 'generic.svg';
            }
        });

        self.cssClass = ko.computed(function(){
            return 'device device-type-' + (self.type() || 'generic');
        });

        self.value = ko.computed(function(){
            switch (self.type()) {
                case 'temperature':
                    return self._value() + ' ℃';
                case 'humidity':
                    return self._value() + ' %';
                default:
                    return self._value();
            }
        });

    }

    self.data = ko.computed(function() {
        var result = {};
        var data = app.state.data();
        var groupBy = self.groupBy();
        for(var serviceId in data) {
            for(var device in data[serviceId]) {
                if (device == '_service')
                    continue;
                var dev = {
                    serviceId: serviceId,
                    device:    device,
                    name:      device,
                    location:  null,
                    type:      null
                };
                for (var key in data[serviceId][device]) {
                    for (var attr in data[serviceId][device][key]) {
                        dev[attr] = data[serviceId][device][key][attr];
                    }
                }

                var group = groupBy == 'none' ? 'none' : dev[groupBy];
                if (group === null || group === undefined) group = 'none';
                if (!result[group])
                    result[group] = [];
                result[group][ result[group].length ] = new self.Device(dev);

            }
        }

        var result2 = [];
        for(var groupId in result) {
            if (groupId == 'none')
                continue;
            var group = new self.Group({
                id: groupId,
                devices: result[groupId]
            });
            result2[result2.length] = group;
        }

        if (result['none']) {
            var groupId = 'none';
            var group = new self.Group({
                id: groupId,
                devices: result[groupId]
            });
            result2[result2.length] = group;
        }

        return result2;

    });

}
