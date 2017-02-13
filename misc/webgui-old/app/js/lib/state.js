window.Chains = window.Chains || {};

window.Chains.State = function(app) {

    var Device = function(id, data) {
        this.id = ko.observable(id);
        this.data = ko.observable(data);
    }

    var Service = function(id, devices) {
        this.id = ko.observable(id);
        this.devices = ko.observableArray();
        for(var deviceId in devices) {
            this.devices.push( new Device(deviceId, devices[deviceId]) );
        }
    };

    var self = this;

    self.data = ko.observableArray(); //Array();

    self.load = function(callback) {
        app.backend.get('/state', function(response){
            //self.data(response.data);

            for(var serviceId in response.data) {
                var service = new Service(serviceId, response.data[serviceId]);
                self.data.push(service);
            }

            if (callback)
                callback();
        });

    }

    self.getService = function(serviceId) {
        var state = self.data();
        for(var i=0; i < state.length; i++) {
            if (state[i].id() == serviceId) {
                return state[i];
            }
        }
    }

    self.getDevice = function(service, deviceId) {
        var devices = service.devices();
        for(var j=0; j < devices.length; j++) {
            if (devices[j].id() == deviceId) {
                return devices[j];
            }
        }
    }

    self.get = function(path) {
        if (!path)
            return;
        var parts = path.split('.');
        var service = self.getService(parts[0]);
        if (parts.length == 1 || !service)
            return service;
        var device = self.getDevice(service, parts[1]);
        if (parts.length == 2 || !device)
            return device;
        var data = device.data();
        for(var i=2; i < parts.length; i++) {
            data = data[ parts[i] ];
            if (!data)
                return data;
        }
        return data;
    }

    self.set = function(serviceId, deviceId, data, attrs) {
        var service = self.getService(serviceId);

        if (!service) {
            service = new Service(serviceId, []);
            self.data.push(service);
        }

        var device = self.getDevice(service, deviceId);

        if (!device) {
            device = new Device(deviceId, {});
        }

        var deviceData = device.data();

        if (!deviceData.data)
            deviceData.data = {};

        for(var key in attrs) {
            deviceData[key] = attrs[key];
        }

        for(var key in data) {
            deviceData.data[key] = data[key];
        }

        device.data(deviceData);

    }


}
