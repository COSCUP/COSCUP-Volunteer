#!/bin/sh

function cleanup {
    if [ -d .git ]; then
        rm -r .git
    fi
}

trap cleanup EXIT

apk add git
git config --global user.email "volunteer@coscup.org"
git config --global user.name "COSCUP Volunteer"
git config --global --add safe.directory /app/docs_dev
git init
git add .
git commit -m 'init'

"$@"
