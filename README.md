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

## Nginx 設定
（待補）

## Issues
問題回報請使用 Issues、如果遇到安全問題的回報，可以使用 GPG 加密後回報。

- Toomore Chiang [422B 779C D894 982B C41E 85EE 3624 CAD7 8AFC 3169](https://keyserver.ubuntu.com/pks/lookup?search=0x422b779cd894982bc41e85ee3624cad78afc3169&fingerprint=on&op=index)
