#!/bin/sh

set -e

cd /volunteer

docker compose --project-directory /volunteer up -d

# Remove unused images
docker image prune -f
