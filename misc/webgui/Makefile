build:
	@if ! which npm >/dev/null; then \
		sudo apt-get install -y npm ; \
	fi
	@if ! which bower >/dev/null; then \
		sudo npm install -g bower ; \
	fi
	@if ! which gulp >/dev/null; then \
		sudo npm install -g gulp ; \
	fi
	@if ! gem list --local|grep sass; then \
        sudo gem install sass ; \
	fi
	sudo npm install
	gulp

watch:
	gulp watch

install:
	cp /srv/chains/misc/webgui/apache/apache.conf /etc/apache2/sites-available/chains.conf
	a2enmod proxy
	a2enmod proxy_http
	a2ensite chains.conf
	service apache2 reload
