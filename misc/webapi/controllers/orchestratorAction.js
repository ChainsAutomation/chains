module.exports = function(app, route) {

	app.post(route, function(req, res) {

        var args = req.body || [];

		app.chains.callOrchestratorAction(req.params.action, args, function(err, response) {
			if (err)
				return res.send(err, 500);
            res.send(response);
		});

	});

}
