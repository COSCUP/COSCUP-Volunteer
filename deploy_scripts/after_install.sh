#!/bin/sh

set -e

cd /volunteer

# Copy settings
cp /home/ubuntu/setting.py /volunteer/setting.py

# Build images
/bin/bash /volunteer/build-base.sh
docker compose --project-directory /volunteer build --no-cache