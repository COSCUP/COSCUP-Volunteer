docker run -d --restart='always' \
           --name volunteer-1 \
           --link secretary_mongo:mongo \
           --link queue_sender:celery \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:6699:6699 \
           volunteer-app:prod python3 ./main.py

docker run -d --restart='always' \
           --name volunteer-2 \
           --link secretary_mongo:mongo \
           --link queue_sender:celery \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:6688:6699 \
           volunteer-app:prod python3 ./main.py
