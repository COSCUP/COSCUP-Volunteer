# COSCUP Volunteer

COSCUP Volunteer 志工服務系統，主要解決招募、人員管理、行政流程建立。
[https://volunteer.coscup.org/](https://volunteer.coscup.org/)

## License

GNU Affero General Public License version 3 (AGPL-3.0)

## Build / Start

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
    pip install poetry  # Install Poetry

    poetry install  # Install Dependencies

### 設定 VS Code

找到 poetry 建立的 virtual environment：

    poetry env list --full-path

然後 <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>，輸入 `Python: Select Interpreter`，
選擇 `輸入直譯器路徑`，填入路徑即可。

## Nginx 設定

（待補）

## Issues

問題回報請使用 Issues、如果遇到安全問題的回報，可以使用 GPG 加密後回報。

- COSCUP Volunteer (volunteer@coscup.org)
  [8532 8B3E 5669 83C4 F4FD  0487 6842 9A6C D968 9A13](https://volunteer.coscup.org/pgp/85328B3E566983C4F4FD048768429A6CD9689A13.asc)
- Toomore Chiang (toomore@coscup.org)
  [DD5B 53B5 ECC3 0E9F 6B4F  4E47 B55D DBA4 944B 6241](https://volunteer.coscup.org/pgp/DD5B53B5ECC30E9F6B4F4E47B55DDBA4944B6241.asc)
