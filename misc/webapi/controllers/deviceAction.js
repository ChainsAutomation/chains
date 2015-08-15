module.exports = function(app, route) {

	app.post(route, function(req, res) {

console.log('dev act');
        var args = [ ]; // todo: optional more params

		app.chains.callDeviceAction(req.params.id, req.params.action, args, function(err, response) {
			if (err)
				return res.send(err, 500);
            res.send(response);
		});

	});

}
