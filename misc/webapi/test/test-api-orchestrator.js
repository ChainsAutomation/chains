var should = require('chai').should(),
		supertest = require('supertest'),
		api = supertest('http://localhost:7890');

describe('GET /orchestrator', function() {

	it('it return the orchestrator', function(done) {
		api.get('/orchestrator')
		.expect(200)
		.expect('Content-Type', /json/)
		.end(function(err, res) {
			if (err) return done(err);
			res.body.should.have.property('id');
            res.body.id.should.equal('main');
			done();
		});
	});

});

describe('POST /orchestrator/ping', function() {

	it('it returns pong', function(done) {
		api.post('/orchestrator/ping')
		.expect(200)
		.end(function(err, res) {
			if (err) return done(err);
            res.body.should.have.property('pong');
            res.body.pong.should.equal(true);
			done();
		});
	});

});

describe('POST /orchestrator/echo', function() {

	it('it returns what we sent', function(done) {
		api.post('/orchestrator/echo')
        .send(["hello"])
		.expect(200)
		.end(function(err, res) {
			if (err) return done(err);
            res.body.should.have.property('reply');
            res.body.reply.should.equal("hello");
			done();
		});
	});

});

describe('POST /orchestrator/describe', function() {

	it('it returns description that includes describe action', function(done) {
		api.post('/orchestrator/describe')
		.end(function(err, res) {
			if (err) return done(err);
            res.body.should.have.property('info');
            res.body.should.have.property('events');
            res.body.should.have.property('actions');
            res.body.actions.should.be.instanceof(Array);
            res.body.actions.should.include({
                'info': 'Describe this daemon',
                'name': 'describe',
                'args': []
            });
			done();
		});
	});

});
