module.exports = function(app, route) {

	app.get(route, function(req, res) {

		app.chains.callOrchestratorAction('getManagers', [], function(err, response) {
			if (err)
				res.send(err, 500);
			else
				res.send(response);
		});

	});

}
