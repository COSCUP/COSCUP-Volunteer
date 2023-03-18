docker run -d --restart='always' \
           --name volunteer-1 \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --link memcached-prod:memcached \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/var/log/apps \
           -p 127.0.0.1:6699:5000 \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           volunteer-app:prod poetry run uwsgi ./uwsgi.ini

docker run -d --restart='always' \
           --name volunteer-2 \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --link memcached-prod:memcached \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/var/log/apps \
           -p 127.0.0.1:6688:5000 \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           volunteer-app:prod poetry run uwsgi ./uwsgi.ini
