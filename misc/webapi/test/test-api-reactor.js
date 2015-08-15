var should = require('chai').should(),
		supertest = require('supertest'),
		api = supertest('http://localhost:7890');

describe('GET /reactors', function() {

	it('it returns list of reactors', function(done) {
		//api .set('x-api-key', '123myapikey')
		//.auth('correct', 'credentials')
		api.get('/reactors')
		.expect(200)
		.expect('Content-Type', /json/)
		.end(function(err, res) {
			if (err) return done(err);
			res.body.should.have.property('master'); //.and.be.instanceof(Array);
            res.body.master.should.have.property('heartbeat');
            res.body.master.should.have.property('online');
            res.body.master.id.should.equal('master');
			done();
		});
	});

});

describe('GET /reactors/master', function() {

	it('it returns one reactor', function(done) {
		api.get('/reactors/master')
		.expect(200)
		.expect('Content-Type', /json/)
		.end(function(err, res) {
			if (err) return done(err);
            res.body.should.have.property('heartbeat');
            res.body.should.have.property('online');
            res.body.id.should.equal('master');
			done();
		});
	});

});

describe('POST /reactors/master/ping', function() {

	it('it returns pong', function(done) {
		api.post('/reactors/master/ping')
		.expect(200)
		.end(function(err, res) {
			if (err) return done(err);
            res.body.should.have.property('pong');
            res.body.pong.should.equal(true);
			done();
		});
	});

});

describe('POST /reactors/master/echo', function() {

	it('it returns what we sent', function(done) {
		api.post('/reactors/master/echo')
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

describe('POST /reactors/master/describe', function() {

	it('it returns description that includes describe action', function(done) {
		api.post('/reactors/master/describe')
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
