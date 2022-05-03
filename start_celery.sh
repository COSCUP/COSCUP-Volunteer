docker run -d --restart='always' \
           --name volunteer_celery \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log_docker_celery:/app/log_docker_celery \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           volunteer-app:prod env C_FORCE_ROOT=true poetry run celery -A celery_task.celery_main worker -B -l info -O fair -c 4 --logfile ./log_docker_celery/log.log
