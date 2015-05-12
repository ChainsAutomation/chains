.PHONY: test

deps:
	sudo apt-get install -qqy python-pip python-amqplib
	sudo /usr/bin/pip install pytest
	sudo easy_install amqplib


test: deps
	PYTHONPATH=lib/ /usr/local/bin/py.test test/
