---
title: 建立基本映像檔
summary: 在本地端建立基本映像檔案
description: 在本地端建立基本映像檔
---
# 建立基本映像檔

## Docker

### 安裝

我們是使用 [docker compose](https://docs.docker.com/compose/)（不是 **docker-compose**）來將專案跑在容器中，請預先安裝 [Docker Engine](https://docs.docker.com/engine/) 或是 [Docker 桌面版](https://docs.docker.com/get-docker/)後再繼續。

!!! tip "Docker 在 macOS 中的效能"

    如果你是將 Docker 執行在 macOS 系統，請選擇 `VirtioFS` 作為檔案分享實作。（可[參考](https://www.paolomainardi.com/posts/docker-performance-macos/)）

### 建立「基本映像檔」

建立「基本映像檔」於本地開發。（建立的版本號會依[每次釋出](https://github.com/COSCUP/COSCUP-Volunteer/releases)而有所改變）

    docker build -t coscupweb-base:24.04.25 -f ./Dockerfile-base-dev ./

!!! note

    由於我們沒有註冊 `coscupweb-base` 於 Docker Hub，因此你需要手動建立映像檔，透過這樣的方式建立並不需要註冊或登入 Docker Hub 帳號。

### setting.py

設定設定檔 `setting.py`

    cp setting_sample.py setting.py

編輯 `setting.py`，使 `MONGO_MOCK` 為 `False`.

!!! todo

    在此階段，只需要設定 `MONGO_MOCK` 即可，其他的設定可以參考 `setting_sample.py` 中的註解。

### Compose up

建立 App 映像檔

    docker compose build --no-cache

或是直接使用 `up` 來建立與啟動。

    docker compose up --build

等待直到所有的服務都啟用，開啟瀏覽器連到以下位置：

    http://127.0.0.1:80/

!!! warning

    因為 cookie 安全屬性 `__Host-` 在本地位置 `127.0.0.1` 是不被 **Chrome** 與 **Safari** 允許使用([Issue 1056543], [Issue 1263426])。因此以下步驟將只在 Firefox 中有效。

    [Issue 1056543]: https://bugs.chromium.org/p/chromium/issues/detail?id=1056543
    [Issue 1263426]: https://bugs.chromium.org/p/chromium/issues/detail?id=1263426

    或是你可以暫時註解掉與 cookie/session 相關的程式碼於 `./main.py` 中。

    ``` python title="main.py"
    # comment them all
    app.config['SESSION_COOKIE_NAME'] = '__Host-vl'
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = True
    ```

!!! tip

    更多有關 Compose 檔案細節可參閱[官方文件](https://docs.docker.com/compose/compose-file/)。

### 建立第一個測試帳號

建立測試帳號，請執行以下指令：

    docker compose run --rm cmdapp dev user_add

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/docs_add_users.png">
    <img alt="docs_add_users"
         src="https://volunteer.coscup.org/doc/docs_add_users.png"
         style="border: 1px #ececec solid; border-radius: 0.4rem;"
    >
  </a>
</figure>

如果成功，將會顯示以下訊息：

    [!] Next step
     | Please visit one of these links to setup the cookie/session:
        -> http://127.0.0.1/dev/cookie?sid={sid}

打開瀏覽器，選擇其中一個連結即可登入：

    http://127.0.0.1/dev/cookie?sid={sid}

!!! info

    這段指令會建立 10 組帳號與註冊工作階段，連結網只是讓瀏覽器可以交換到可登入的工作階段。

### 本地瀏覽開發文件

在啟動 `docker compose up` 之後，會有一個容器 `docs` 執行文件的建立，你可以透過連結到以下位置在本地端瀏覽開發文件：

    http://127.0.0.1/docs/
