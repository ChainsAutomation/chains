module.exports = function(app, route) {

	var baseUrl = '';

	app.use(route, function(req, res) {
		res.send([
            {
                "_links":
                {
                    "self": {"href": baseUrl + "/orchestrator"}
                },
                "id": "orchestrator",
                "name": "Orchestrator"
            },
            {
                "_links":
                {
                    "self": {"href": baseUrl + "/services"}
                },
                "id": "services",
                "name": "Services"
            },
            {
                "_links":
                {
                    "self": {"href": baseUrl + "/managers"}
                },
                "id": "managers",
                "name": "Managers"
            },
            {
                "_links":
                {
                    "self": {"href": baseUrl + "/reactors"}
                },
                "id": "reactors",
                "name": "Reactors"
            },
        ]);
	});

}
