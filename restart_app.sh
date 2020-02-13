sh ./build-app.sh

docker stop -t 2 volunteer_celery
docker rm volunteer_celery

sh ./start_celery.sh

docker stop -t 2 volunteer-1
docker rm volunteer-1
sh ./start_app.sh

docker stop -t 2 volunteer-2
docker rm volunteer-2
sh ./start_app.sh
