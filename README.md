# COSCUP Volunteer

COSCUP Volunteer 志工服務系統，主要解決招募、人員管理、行政流程建立。
[https://volunteer.coscup.org/](https://volunteer.coscup.org/)

## License

GNU Affero General Public License version 3 (AGPL-3.0)

## For Developer

目前我們使用 `docker compose` 的方式進行開發，可以使用 `docker compose up` 來建立與啟動必要的服務。完成後可以連到 `http://127.0.0.1:80` 看到首頁！

### Code Style

- [pylint](https://pypi.org/project/pylint/)
- [autopep8](https://pypi.org/project/autopep8/)
- [pytest](https://pypi.org/project/pytest/)
- [pytest-cov](https://pypi.org/project/pytest-cov/)

### 已知問題

- [ ] 登入認證目前還不能使用，還在處理開發時的臨時帳號登入方式。開發時會使用　`Dockerfile-app-dev` 來建立 images。
- [ ] 目前還沒有開發時的測試資料。

### 目前開發重點

- [ ] 提升 testing cases 的涵蓋率
- [ ] 開發帳號與資料預建立

## For Production

### Build Image

需要 Docker 來建立 Image。

    sh ./build-base.sh && sh ./build-app.sh

### Start

啟動服務，使用到 MongoDB、RabbitMQ

    sh ./start_mongo.sh && sh ./start_rabbitmq.sh && sh ./start_celery.sh

啟動 web app

    sh ./start_app.sh

如果有修正後的重啟，可以直接執行

    sh ./restart_app.sh

## Local Development

### 安裝依賴

您可能需要先安裝 `libmemcached` 和 `poetry`，才能安裝依賴。

    brew install libmemcached  # macOS

Poetry 的安裝請使用[官方文件](https://python-poetry.org/docs/)建議安裝在全域環境。

    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

### 設定 VS Code

找到 poetry 建立的 virtual environment：

    poetry env list --full-path

然後 <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>，輸入 `Python: Select Interpreter`，
選擇 `輸入直譯器路徑`，填入路徑即可。

### Build from Docker Compose

We use the [docker compose](https://docs.docker.com/compose/) (not `docker-compose`) to run the project in containers, please pre-install [Docker Engine](https://docs.docker.com/engine/) or [Docker Desktop](https://docs.docker.com/get-docker/) before get start.

Only to build the base images

    docker compose build --no-cache

Or build and run ...

    docker compose up --build

Wait an amount until all services are available, open browser and visit to:

    http://127.0.0.1:80/

**Notice: Because of the cookie with secure attributes (`__Host-`) at local for `127.0.0.1` is not allowed for Chrome and Safari ([1056543](https://bugs.chromium.org/p/chromium/issues/detail?id=1056543), [1263426](https://bugs.chromium.org/p/chromium/issues/detail?id=1263426)), the following steps are works only in [Firefox](https://www.mozilla.org/firefox/).**

To create an user for dev

    docker compose run --rm cmdapp dev user_add

This command will create an user account and register an session, so you need to feed the cookie for your browser.

    http://127.0.0.1/dev/cookie?sid={sid}

Visit the dev page to setup.

    http://127.0.0.1:80/dev/


## 如何貢獻專案

### Fork me

1. 使用 [github fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) 的方式建立一份到自己的帳號底下。（詳細的操作可以參考 [Working with forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks)）
2. 參考 `README.md` 的 `Local Development` 先建立起本地端開發環境。

### Create a Pull Request(PR)

如果你的開發很順利，覺得可以送出一版 PR 讓我們 review，也請透過 Github [create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) 的方式發給我們！

### More Details

1. 參考這兩份資訊，瞭解平台的[架構](https://github.com/COSCUP/COSCUP-Volunteer/wiki/How-to-make-COSCUP-Volunteer%3F)與[服務](https://github.com/COSCUP/COSCUP-Volunteer/wiki/What-service-is-in-the-COSCUP-Volunteer%3F)。
2. 查看目前已知的問題 [Issues](https://github.com/COSCUP/COSCUP-Volunteer/issues)。
3. 查看目前的開發 [roadmap](https://github.com/COSCUP/COSCUP-Volunteer/wiki/roadmap)。
4. 或是到 [COSCUP 行政組 - 開發組](https://chat.coscup.org/coscup/channels/secretary-develop)頻道討論。

## Issues

問題回報請使用 Issues、如果遇到安全問題的回報，可以使用 GPG 加密後回報。

- COSCUP Volunteer (volunteer@coscup.org)
  [8532 8B3E 5669 83C4 F4FD 0487 6842 9A6C D968 9A13](https://volunteer.coscup.org/pgp/85328B3E566983C4F4FD048768429A6CD9689A13.asc)
- Toomore Chiang (toomore@coscup.org)
  [DD5B 53B5 ECC3 0E9F 6B4F 4E47 B55D DBA4 944B 6241](https://volunteer.coscup.org/pgp/DD5B53B5ECC30E9F6B4F4E47B55DDBA4944B6241.asc)
