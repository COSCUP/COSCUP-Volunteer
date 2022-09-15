#!/usr/bin/env sh

docker build --no-cache=true -t coscupweb-base:22.08.31 -f ./Dockerfile-base ./
