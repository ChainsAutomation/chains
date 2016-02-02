module.exports = function(app, route) {

	app.post(route, function(req, res) {

        var args = req.body || [];

        if (!args)
            return res.send(500, 'Must have event as requets body');
        if (!args.service)
            return res.send(500, 'Missing service');
        if (!args.key)
            return res.send(500, 'Missing key');

        app.chains.sendEvent(args.service, args.key, args);
        res.send(200);

	});

}
