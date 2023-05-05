# Developer Beginner

Fork the project from github and make [pull requests] to the origin repository.

[pull requests]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests

## Github

### Sign and sign-off all commits or tags

We prefer your commits or tags are **signed**. And also **[sign-off](how-to-signoff.md)** your commits.

!!! tip

    Please read [this docs](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification) to learn about how to **sign** your commits and tags.

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

    We also have github [actions](https://github.com/COSCUP/COSCUP-Volunteer/actions) to verify those quality. The `PEP8` must have to be complied.

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

=== "VS Code"
    Setup the `Python: Select Interpreter` ++cmd+shift+p++, and input the poetry's env full path.

=== "vim"
    `vim` will auto read the `pyproject.toml` file, so there is nothing changed here.
