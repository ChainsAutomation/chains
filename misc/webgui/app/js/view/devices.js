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
        self.name      = ko.observable(data.name);
        self._type     = ko.observable(data.type);
        self._location = ko.observable(data.location);
        self._data     = ko.observable(data.data);

        self.cssClass = ko.computed(function(){
            return 'device device-type-' + (self._type() || 'generic');
        });

        self.data = ko.computed(function(){
			var result = [];
			var data = self._data() || {};
			for (key in data) {
				result[result.length] = { key: key, data: data[key] };
			}
			return result;
        });

		self.location = ko.computed(function(){
			return self._location() || 'unknown';
		});

		self.type = ko.computed(function(){
			return self._type() || 'unknown';
		});

        self.icon = ko.computed(function(){
			return '/images/type-icon/' + self.type() + '.svg';
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
                    type:      null,
					data:      {}
                };
                for (var key in data[serviceId][device]) {
                    dev[key] = data[serviceId][device][key];
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
