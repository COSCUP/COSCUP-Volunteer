# Build Base Image

## Docker

### Installation

We use the [docker compose](https://docs.docker.com/compose/) (not docker-compose) to run the project in containers, please pre-install [Docker Engine](https://docs.docker.com/engine/) or [Docker Desktop](https://docs.docker.com/get-docker/) before getting started.

### Build the base image

Build the base image for local development.

    docker build -t coscupweb-base:22.10.17 -f ./Dockerfile-base-dev ./

!!! note

    We've not registed the `coscupweb-base` on Docker Hub, therefor you need to build this image manually.
    In this way, you haven't needed to signup the Docker Hub account.

### setting.py

Setup the `setting.py`

    cp setting_sample.py setting.py

Edit the `setting.py`, make `MONGO_MOCK` to be `False`.

!!! todo

    At this section, just only setting up the `MONGO_MOCK`, the rest of settings please read this section of about `setting.py`.

### Compose up

Build the rest of app images

    docker compose build --no-cache

Or directly execute `up` to build and run ...

    docker compose up --build

Wait an amount until all services are available, open browser and visit to:

    http://127.0.0.1:80/

!!! warning

    Because of the cookie with secure attributes (`__Host-`) at local in `127.0.0.1` is not allowed for Chrome and Safari ([Issue 1056543], [Issue 1263426]), the following steps are works only in [Firefox](https://www.mozilla.org/firefox/).

    [Issue 1056543]: https://bugs.chromium.org/p/chromium/issues/detail?id=1056543
    [Issue 1263426]: https://bugs.chromium.org/p/chromium/issues/detail?id=1263426

!!! tip

    For more information about the Compose file, see the [Compose file reference](https://docs.docker.com/compose/compose-file/).

### Create first user account

To create a user for dev.

    docker compose run --rm cmdapp dev user_add

If succeed, the command will display the message like below:

    [!] Next step
     | Please visit these link to setup the cookie/session:
        -> http://127.0.0.1/dev/cookie?sid={sid}

Open browser visit to:

    http://127.0.0.1/dev/cookie?sid={sid}

!!! info

    This command will create an user account and register an session, so you need to feed the cookie for your browser.

### Dev page

Visit the dev page to setup.

    http://127.0.0.1:80/dev/
