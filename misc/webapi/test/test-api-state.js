var should = require('chai').should(),
		supertest = require('supertest'),
		api = supertest('http://localhost:7890'),
        timerId = '157ddfcfd7814735aa9add5ed9e05085';

describe('GET /state', function() {

	it('it returns full state', function(done) {
		api.get('/state')
		.expect(200)
		.expect('Content-Type', /json/)
		.end(function(err, res) {
			if (err) return done(err);
			res.body.data.should.have.property(timerId);
			res.body.data[timerId].should.be.instanceof(Object);
			res.body.data[timerId].should.have.property('online');
			done();
		});
	});

});

describe('GET /state/<timerId>', function() {

	it('it returns state for timer device', function(done) {
		api.get('/state/' + timerId)
		.expect(200)
		.expect('Content-Type', /json/)
		.end(function(err, res) {
			if (err) return done(err);
			res.body.data.should.be.instanceof(Object);
			res.body.data.should.have.property('online');
			done();
		});
	});

});

describe('GET /state/<timerId>/online/data', function() {

	it('it returns state for timer device online key', function(done) {
		api.get('/state/' + timerId + '/online/data')
		.expect(200)
		.expect('Content-Type', /json/)
		.end(function(err, res) {
			if (err) return done(err);
			res.body.data.should.have.property('value');
			done();
		});
	});

});
