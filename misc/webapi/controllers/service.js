module.exports = function(app, route) {

	app.get(route, function(req, res) {

        var id = req.params.id;

		app.chains.callOrchestratorAction('getServices', [], function(err, response) {

			if (err)
				return res.send(err, 500);

			var result = {};
			for(var key in response) {

                if (key != id)
                    continue;

				var dev = response[key];
				var main = dev.main || {};

                result = {
					id: key,
					name: main.name,
					'class': main['class'],
					online: dev.online,
					heartbeat: dev.heartbeat,
					manager: main.manager,
					autostart: main.autostart
				};

                break;

			}

			res.send(result);

		});

	});

}
