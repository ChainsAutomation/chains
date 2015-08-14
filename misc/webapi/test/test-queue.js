var Queue = require('../lib/queue.js');

var testTopic = 'foo-test';
var receivedMessage = null;
var queue = new Queue();
queue.setDebug(true);

queue.on('message', function(topic, message) {
	if (topic == testTopic) {
		console.log('Received message: ' + topic, message);
		receivedMessage = message;
	}
});

queue.on('ready', function() {
	queue.publish(testTopic, {'foo': 'bar'});
});

var checkCount = 0;
function checkReceived() {
	if (receivedMessage && receivedMessage.foo == 'bar') {
		console.log('SUCCESS - Message received');
		process.exit();
	}
	checkCount++;
	if (checkCount > 50) {
		console.error('ERROR - Did not receive message in 5 sec');
		process.exit(99);
	}
	setTimeout(checkReceived, 100);
}

checkReceived();
queue.connect();
