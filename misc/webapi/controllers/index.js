module.exports = function(app, route) {

	app.use(route, function(req, res) {
		res.send('Chains WebAPI frontpage');
	});

}
