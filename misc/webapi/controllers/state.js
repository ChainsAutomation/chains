module.exports = function(app, route) {

	app.get(route, function(req, res) {

        var tmp = req.params.path ? req.params.path.split('/') : [];
        var path = tmp.join('.');

        // remove trailing slash
        if(path.substr(-1) === '.') {
            path = path.substr(0, path.length - 1);
        }

        var args = path ? [path] : [];

		app.chains.callReactorAction('master', 'getState', args, function(err, response) {

            if (err)
                res.send(err, 500);
            else
                res.send({"data": response});

		});

	});

}
