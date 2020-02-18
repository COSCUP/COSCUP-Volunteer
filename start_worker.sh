docker run \
           -it --rm \
           --name volunteer-worker \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/scripts:/app/scripts \
           volunteer-app:prod sh
