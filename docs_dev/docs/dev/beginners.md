# Overview for Beginners

Fork the project from gihub and make [pull requests] to the origin repository.

[pull requests]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests

## Github

### Sign commits or tags

We prefer your commits or tags are signed.

!!! tip

    Please read [this docs](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification) to learn about how to sign your commits and tags.

## Repository

### Fork

Click [Fork](https://github.com/COSCUP/COSCUP-Volunteer/fork) button on the top-right at the [COSCUP/COSCUP-Volunteer](https://github.com/COSCUP/COSCUP-Volunteer) repo page.

### Clone

`git clone` from the repo you have forked.

## Code style

The codebase is compliant in [PEP8](https://peps.python.org/pep-0008/) and [typing hint](https://docs.python.org/3/library/typing.html) ([PEP484](https://peps.python.org/pep-0483/)).

 - pylint
 - autopep8
 - pytest
 - pytest-cov
 - mypy

!!! note

    We also have github [actions](https://github.com/COSCUP/COSCUP-Volunteer/actions) to verify those quality. The `PEP8` must have to be complied but the typing hint only be defined in `./models`, `./module`.

## Dependency

### Poetry

Please install [Poetry](https://python-poetry.org/) for dependency management and packaging in Python. And [not recommended](https://python-poetry.org/docs/) install in `pip`.

    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

After the poetry is installed, you could run `poetry install` to install the packages at local.

### libmemcached (optional)

If you want development at root system instead of docker containers, please install this dependency for `memcached`.

=== "macOS"

        brew install libmemcached

=== "Ubuntu"

        apt-get install libmemcached-dev

## Development Environment

Install the packages.

    poetry install

Shell within the virtual environment.

    poetry shell

### Setting up IDE

Setting up your IDE for `pylint` and `autopep8`. Find out the poetry env full path.

    poetry env list --full-path

=== "VS Code"
    Setup the `Python: Select Interpreter` ++cmd+shift+p++, and input the poetry's env full path.

=== "vim"
    Create a file `.pylintrc` and with those contents. And replace the `{PUT-POETRY-ENV-FULL-PATH-HERE}` with the value of `poetry env list --full-path`.

    ``` yaml
    [MASTER]
    extension-pkg-whitelist=pydantic
    disable=W0223
    init-hook='import os, sys; sys.path.append(os.getcwd()); sys.path.append("{PUT-POETRY-ENV-FULL-PATH-HERE}")'
    generated-members=setting,googleapiclient.discovery.*,pymongo
    ```
