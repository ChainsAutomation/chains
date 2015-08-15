module.exports = function(app, route) {

	app.get(route, function(req, res) {

		app.chains.callOrchestratorAction('getReactors', [], function(err, response) {

			if (err)
				return res.send(err, 500);

			for(var key in response) {
                if (key == req.params.id) {
                    var data = response[key];
                    data.id = key;
                    res.send(data);
                    return;
                }
			}

			res.send('Not found', 500);

		});

	});

}
