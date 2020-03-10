docker run -d --restart=always --log-opt max-size=12m --log-opt max-file=1 \
           -p 127.0.0.1:11213:11211 \
           --name memcached-prod-1 memcached:1.6.0-alpine
