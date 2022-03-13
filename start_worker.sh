#!/usr/bin/env bash
# -*- coding: utf-8 -*-

docker run \
           -it --rm \
           --name volunteer-worker \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --link memcached-prod:memcached \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -p 6699:6699 \
           -v $(pwd)/scripts:/app/scripts \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           -e PYTHONPATH=/app \
           volunteer-app:prod sh
