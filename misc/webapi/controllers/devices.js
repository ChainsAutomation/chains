module.exports = function(app, route) {

	app.get(route, function(req, res) {

		app.chains.callOrchestratorAction('getDevices', [], function(err, response) {

			if (err)
				return res.send(err, 500);

			var result = [];
			for(var key in response) {

				var dev = response[key];
				var main = dev.main || {};
				if (typeof(value) == 'function') continue;

				result[result.length] = {
					id: key,
					name: main.name,
					'class': main['class'],
					online: dev.online,
					heartbeat: dev.heartbeat,
					manager: main.manager,
					autostart: main.autostart
				};

			}

			res.send(result);

		});

	});

}
