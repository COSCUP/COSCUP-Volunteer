# COSCUP Volunteer

COSCUP Volunteer 志工服務系統，主要解決招募、人員管理、行政流程建立。
[https://volunteer.coscup.org/](https://volunteer.coscup.org/)

## License

GNU Affero General Public License version 3 (AGPL-3.0)

## For Developer

目前我們使用 docker-compose 的方式進行開發，可以使用 `docker-compose up` 來建立與啟動必要的服務。完成後可以連到 `http://127.0.0.1:80` 看到首頁！

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

## Issues

問題回報請使用 Issues、如果遇到安全問題的回報，可以使用 GPG 加密後回報。

- COSCUP Volunteer (volunteer@coscup.org)
  [8532 8B3E 5669 83C4 F4FD 0487 6842 9A6C D968 9A13](https://volunteer.coscup.org/pgp/85328B3E566983C4F4FD048768429A6CD9689A13.asc)
- Toomore Chiang (toomore@coscup.org)
  [DD5B 53B5 ECC3 0E9F 6B4F 4E47 B55D DBA4 944B 6241](https://volunteer.coscup.org/pgp/DD5B53B5ECC30E9F6B4F4E47B55DDBA4944B6241.asc)
