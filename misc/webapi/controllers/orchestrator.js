module.exports = function(app, route) {

	app.get(route, function(req, res) {
        res.send({"id": "main"});
	});

}
