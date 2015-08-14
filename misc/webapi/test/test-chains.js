var chains = require('../lib/chains.js');

chains.rpc(
	'm',
	'master',
	'ping',
	[],
	function(response) {
		console.log('response:',response);
		process.exit();
	}
);
