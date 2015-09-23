build:
	@if ! which npm >/dev/null; then \
		sudo apt-get install -y npm ; \
	fi
	@if ! which bower >/dev/null; then \
		sudo npm install -g bower ; \
	fi
	sudo npm install
	gulp

watch: build
	gulp watch
