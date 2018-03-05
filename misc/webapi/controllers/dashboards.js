module.exports = function(app, route) {

    var fs = require('fs');
    var file = '/srv/chains/data/dashboards.json';

    function load() {
        var text = fs.readFileSync(file);
        var data = JSON.parse(text);
        return data;
    }

    function write(data) {
        fs.writeFileSync(file, JSON.stringify(data));
    }

    if (!fs.existsSync(file)) {
        write({});
    }

    // todo: quickfix.. fixme

    app.get(route, function(req, res) {
        res.send(load());
    });

	app.post(route, function(req, res) {
        var data = req.body || {};
        write(data)
        res.send({ ok: true });
	});

}
