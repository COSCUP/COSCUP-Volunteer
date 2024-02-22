---
title: 初次開發
summary: 如何設定基本開發環境
description: 如何設定基本開發環境
---
# 初次開發

請從 Github 上分叉（fork）專案並透過[拉取請求]（Pull Requests）的方式貢獻回專案。

[拉取請求]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests

## Github

### 簽名（sign-off）與簽章（sign）你的提交或標籤

我們希望你的提交與標籤都有**簽章**，並且**[簽名](../how-to-signoff)**你的提交。

!!! tip "提示"

    請參閱[這篇文章]關於如何使用簽章你的提交與標籤。

    [這篇文章]: https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification

## 倉儲

### 分支

在 [COSCUP/COSCUP-Volunteer](https://github.com/COSCUP/COSCUP-Volunteer) 存儲庫頁面的右上方點擊 [Fork](https://github.com/COSCUP/COSCUP-Volunteer/fork) 按鈕。

### 克隆

使用你所 Fork 的存儲庫進行 `git clone`。

## 程式碼風格

這份程式碼遵從 [PEP8](https://peps.python.org/pep-0008/) 和[類型提示](https://docs.python.org/3/library/typing.html) ([PEP484](https://peps.python.org/pep-0483/)) 的規範。

- pylint
- autopep8
- pytest
- pytest-cov
- mypy

!!! note

    我們也有 GitHub [Actions](https://github.com/COSCUP/COSCUP-Volunteer/actions) 來驗證這些程式碼的品質，PEP8 必須要遵守，

## 開發環境相依

### Poetry

請安裝 [Poetry](https://python-poetry.org/) 作為 Python 套件管理工具。並[不建議](https://python-poetry.org/docs/)透過 `pip` 來安裝 Poetry。

    curl -sSL https://install.python-poetry.org | python3 -

當安裝好 Poetry 之後，可以使用 `poetry install` 在本地端安裝專案所需的套件。

### libmemcached (選擇性)

如果你想要在**本地端系統**開發而不是透過 **docker** 與**容器**的方式開發，請安裝 `memcached` 相關套件。

=== "macOS"

        brew install libmemcached

=== "Debian/Ubuntu"

        apt-get install libmemcached11

=== "Fedora"

        dnf install libmemcached

=== "CentOS/Rocky Linux"

        yum install epel-release && yum install libmemcached.x86_64

## 開發環境

安裝套件

    poetry install

啟動開發環境

    poetry shell

!!! note

    由於 Poetry 設定檔 `virtualenvs.in-project` 設定為 `true`，因此 `.venv` 會建立在專案的根目錄中。

### 設定 IDE

=== "VS Code"
    Setup the `Python: Select Interpreter` ++cmd+shift+p++, and input the poetry's env full path.

=== "vim"
    `vim` will auto read the `pyproject.toml` file, so there is nothing changed here.
