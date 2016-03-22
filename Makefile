.PHONY: test

deps:
	pip install pytest amqplib pyyaml

test:
	PYTHONPATH=lib/ /usr/local/bin/py.test test/

deploy:
	./deploy.sh

clearpyc:
	find . -name \*.pyc -delete

travis: deps test
	echo "Running travis"
