docker run -d --restart=always --log-opt max-size=12m --log-opt max-file=1 \
           -p 127.0.0.1:11212:11211 \
           --name memcached-prod memcached:1.6.22-alpine
