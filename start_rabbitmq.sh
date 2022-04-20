#!/usr/bin/env sh
# -*- coding: utf-8 -*-

docker run -d --restart=always --log-opt max-size=12m --log-opt max-file=1 \
           -p 127.0.0.1:5673:5672 \
           -p 127.0.0.1:15673:15672 \
           -v queue_sender:/var/lib/rabbitmq \
           --name queue_sender rabbitmq:3.8.5-management-alpine
