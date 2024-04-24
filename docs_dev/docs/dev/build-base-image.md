# Build Base Image

## Docker

### Installation

We use the [docker compose](https://docs.docker.com/compose/) (not **docker-compose**) to run the project in containers, please pre-install [Docker Engine](https://docs.docker.com/engine/) or [Docker Desktop](https://docs.docker.com/get-docker/) before getting started.

!!! tip "Docker performance on macOS"

    If you are using docker on macOS, please choose `VirtioFS` as the file sharing implementation. ([why](https://www.paolomainardi.com/posts/docker-performance-macos/))

### Build the base image

Build the base image for local development.

    docker build -t coscupweb-base:24.04.25 -f ./Dockerfile-base-dev ./

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

    Because of the cookie with secure attributes (`__Host-`) at local in `127.0.0.1` is not allowed for **Chrome** and **Safari** ([Issue 1056543], [Issue 1263426]), the following steps are works only in [Firefox](https://www.mozilla.org/firefox/).

    [Issue 1056543]: https://bugs.chromium.org/p/chromium/issues/detail?id=1056543
    [Issue 1263426]: https://bugs.chromium.org/p/chromium/issues/detail?id=1263426

    Or you could **temporarily** comment on the codes of the flask session settings in `./main.py`.

    ``` python title="main.py"
    # comment them all
    app.config['SESSION_COOKIE_NAME'] = '__Host-vl'
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = True
    ```

!!! tip

    For more information about the Compose file, see the [Compose file reference](https://docs.docker.com/compose/compose-file/).

### Create first user account

To create a user for dev.

    docker compose run --rm cmdapp dev user_add

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/docs_add_users.png">
    <img alt="docs_add_users"
         src="https://volunteer.coscup.org/doc/docs_add_users.png"
         style="border: 1px #ececec solid; border-radius: 0.4rem;"
    >
  </a>
</figure>

If succeed, the command will display the message like below:

    [!] Next step
     | Please visit one of these links to setup the cookie/session:
        -> http://127.0.0.1/dev/cookie?sid={sid}

Open browser visit one of those links to:

    http://127.0.0.1/dev/cookie?sid={sid}

!!! info

    This command will create 10 user accounts and the register sessions, so you
    need to feed the cookie for your browser.

### Docs in docker

After starting up `docker compose up`, the `docs` of container will build all of
the documents into a volume and directly attach to the nginx container as
a static website.

Open browser and visit to:

    http://127.0.0.1/docs/
