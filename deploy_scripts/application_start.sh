#!/bin/sh

set -e

cd /volunteer

docker compose --project-directory /volunteer up -d

# Remove unsed images
docker image prune
