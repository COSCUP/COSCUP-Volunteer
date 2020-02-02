docker run -d --restart='always' \
           --name secretary-1 \
           --link secretary_mongo:mongo \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:6699:6699 \
           secretary-app:prod python3 ./main.py

docker run -d --restart='always' \
           --name secretary-2 \
           --link secretary_mongo:mongo \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:6688:6699 \
           secretary-app:prod python3 ./main.py
