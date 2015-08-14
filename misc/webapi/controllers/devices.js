module.exports = function(app, route) {

	app.get(route, function(req, res) {

		app.chains.callOrchestratorAction('getDevices', [], function(err, response) {

			if (err)
				return res.send(err, 500);

			var result = [];
			for(var key in response) {

				var value = response[key];
				if (typeof(value) == 'function') continue;

				result[result.length] = {
					id: value.deviceId,
					name: value.name,
					'class': value['class'],
					online: value.online,
					heartbeat: value.heartbeat,
					manager: value.manager,
					autostart: value.autostart
				};

			}

			res.send(result);

		});

	});

}
