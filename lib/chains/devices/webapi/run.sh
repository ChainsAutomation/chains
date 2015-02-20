uwsgi --enable-threads --http :8000 --wsgi-file /srv/chains/lib/chains/devices/webapi/__init__.py --callable app --master --processes 1 -l 50 -L
