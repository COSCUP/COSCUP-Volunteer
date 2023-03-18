docker run -d --restart='always' \
           --name volunteer-api-1 \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --link memcached-prod:memcached \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/var/log/apps \
           -p 127.0.0.1:6677:8000 \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           -e UVICORN_HOST=0.0.0.0 \
           -e UVICORN_WORKERS=2 \
           volunteer-app:prod poetry run uvicorn api.main:app

docker run -d --restart='always' \
           --name volunteer-api-2 \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --link memcached-prod:memcached \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/var/log/apps \
           -p 127.0.0.1:6676:8000 \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           -e UVICORN_HOST=0.0.0.0 \
           -e UVICORN_WORKERS=2 \
           volunteer-app:prod poetry run uvicorn api.main:app
