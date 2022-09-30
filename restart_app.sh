sh ./build-app.sh

docker stop -t 1 volunteer_celery
docker rm volunteer_celery

sh ./start_celery.sh

docker stop -t 1 volunteer-1
docker rm volunteer-1
sh ./start_app.sh

docker stop -t 1 volunteer-2
docker rm volunteer-2
sh ./start_app.sh

docker stop -t 1 volunteer-api-1
docker rm volunteer-api-1
sh ./start_api.sh

docker stop -t 1 volunteer-api-2
docker rm volunteer-api-2
sh ./start_api.sh
