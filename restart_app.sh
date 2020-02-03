sh ./build-app.sh

docker stop -t 2 secretary_celery
docker rm secretary_celery

sh ./start_celery.sh

docker stop -t 2 secretary-1
docker rm secretary-1
sh ./start_app.sh

docker stop -t 2 secretary-2
docker rm secretary-2
sh ./start_app.sh
