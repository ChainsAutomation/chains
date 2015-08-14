module.exports = function(app, route) {

	app.get(route, function(req, res) {

		app.chains.callOrchestratorAction('getReactors', [], function(err, response) {
			if (err)
				res.send(err, 500);
			else
				res.send(response);
		});

	});

}
