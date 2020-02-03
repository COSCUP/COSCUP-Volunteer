docker run -d --restart='always' \
           --name secretary_celery \
           --link secretary_mongo:mongo \
           --link queue_sender:celery \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log_docker_celery:/app/log_docker_celery \
           secretary-app:prod env C_FORCE_ROOT=true celery -A celery_task worker -B -l info -O fair -c 4 --logfile ./log_docker_celery/log.log
