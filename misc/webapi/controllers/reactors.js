module.exports = function(app, route) {

	app.get(route, function(req, res) {

		app.chains.callOrchestratorAction('getReactors', [], function(err, response) {

            for(var key in response) {
                response[key].id = key;
            }

			if (err)
				res.send(err, 500);
			else
				res.send(response);

		});

	});

}
