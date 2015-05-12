.PHONY: test

deps:
	set +e
	apt-get install -y python-amqplib
	ec=$?
	set -e
	if [ $ec -ne 0 ]; then
	    easy_install amqplib
	fi

test: deps
	PYTHONPATH=lib/ /usr/local/bin/py.test test/
