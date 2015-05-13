.PHONY: test

deps:
	sudo apt-get install -qqy python-pip
	sudo /usr/bin/pip install pytest amqplib

test:
	PYTHONPATH=lib/ /usr/local/bin/py.test test/

travis: deps test
	echo "Running travis"
