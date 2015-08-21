module.exports = function(app, route) {

	app.post(route, function(req, res) {

        var args = req.body || [];

		app.chains.callServiceAction(req.params.id, req.params.action, args, function(err, response) {
			if (err)
				return res.send(err, 500);
            res.send(response);
		});

	});

}
