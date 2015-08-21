module.exports = function(app, route) {

	app.post(route, function(req, res) {

		app.chains.callOrchestratorAction('stopService', [req.params.id], function(err, response) {

			if (err)
				res.send(err, 500);
			else
				res.send(response);

		});

	});

}
