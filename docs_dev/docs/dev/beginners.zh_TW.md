# 初次開發

請從 Github 上分叉（fork）專案並透過[拉取請求]（Pull Requests）的方式貢獻回專案。

[拉取請求]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests

## Github

### 簽名（sign-off）與簽章（sign）你的提交或標籤

We prefer your commits or tags are **signed**. And also **[sign-off](/dev/how-to-signoff)** your commits.

我們希望你的提交與標籤都有**簽章**，並且**[簽名](how-to-signoff.zh_TW.md)**你的提交。

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

## Dependency

### Poetry

Please install [Poetry](https://python-poetry.org/) for dependency management and packaging in Python. And [not recommended](https://python-poetry.org/docs/) install in `pip`.

    curl -sSL https://install.python-poetry.org | python3 -

After the poetry is installed, you could run `poetry install` to install the packages at local.

### libmemcached (optional)

If you want development at **root system** instead of **docker containers**, please install this dependency for `memcached`.

=== "macOS"

        brew install libmemcached

=== "Debian/Ubuntu"

        apt-get install libmemcached11

=== "Fedora"

        dnf install libmemcached

=== "CentOS/Rocky Linux"

        yum install epel-release && yum install libmemcached.x86_64

## Development Environment

Install the packages.

    poetry install

Shell within the virtual environment.

    poetry shell

!!! note

    The `virtualenvs.in-project` of poetry configuration has been set to `true`.
    The folder named `.venv` is in the root directory of the project.

### Setting up IDE

Setting up your IDE for `pylint` and `autopep8`. Find out the poetry env full path.

    poetry env list --full-path

=== "VS Code"
    Setup the `Python: Select Interpreter` ++cmd+shift+p++, and input the poetry's env full path.

=== "vim"
    `vim` will auto read the `pyproject.toml` file, so there is nothing changed here.
