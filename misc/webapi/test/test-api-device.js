var should = require('chai').should(),
		supertest = require('supertest'),
		api = supertest('http://localhost:7890'),
        timerId = '157ddfcfd7814735aa9add5ed9e05085';

describe('GET /devices', function() {

	it('it returns list of devices', function(done) {
		api.get('/devices')
		.expect(200)
		.expect('Content-Type', /json/)
		.end(function(err, res) {
			if (err) return done(err);
            res.body.should.have.property(timerId);
            res.body[timerId].should.have.property('heartbeat');
            res.body[timerId].should.have.property('online');
            res.body[timerId].should.have.property('id');
            res.body[timerId].should.have.property('name');
            res.body[timerId].should.have.property('class');
            res.body[timerId].id.should.equal(timerId);
            res.body[timerId].name.should.equal('timer');
            res.body[timerId]['class'].should.equal('Timer');
			done();
		});
	});

});

describe('GET /devices/<timerId>', function() {

	it('it returns timer device', function(done) {
		api.get('/devices/' + timerId)
		.expect(200)
		.expect('Content-Type', /json/)
		.end(function(err, res) {
			if (err) return done(err);
            res.body.should.have.property('heartbeat');
            res.body.should.have.property('online');
            res.body.should.have.property('id');
            res.body.should.have.property('name');
            res.body.should.have.property('class');
            res.body.id.should.equal(timerId);
            res.body.name.should.equal('timer');
            res.body['class'].should.equal('Timer');
			done();
		});
	});

});

describe('POST /devices/<timerId>/ping', function() {

	it('it returns pong', function(done) {
		api.post('/devices/' + timerId + '/ping')
		.expect(200)
		.end(function(err, res) {
			if (err) return done(err);
            res.body.should.have.property('pong');
            res.body.pong.should.equal(true);
			done();
		});
	});

});

describe('POST /devices/<timerId>/echo', function() {

	it('it returns what we sent', function(done) {
		api.post('/devices/' + timerId + '/echo')
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

describe('POST /devices/<timerId>/describe', function() {

	it('it returns description that includes describe action', function(done) {
		api.post('/devices/' + timerId + '/describe')
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
