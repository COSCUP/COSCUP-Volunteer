# Contributing on Github

## Before raising an issue

- Check the issues to ensure your suggestion is not already present within the project.
- Check the pull request to ensure that the bug or feature is not already in progress.

## Before submitting a pull request(PR)
- Check the codebase to make sure that your feature does not exist.
- Read, understand and agree with the [DCO guideline](dco.md) for this project.
- Run `pylint`, `mypy` to make sure your codebase is pretty.
    ``` sh
    (poetry) PYTHONPATH=./ pylint --disable=R0801,E1101,E0611 ./view/ ./module/ ./models/ ./celery_task/ ./structs/ ./api/ ./main.py
    ```
    ``` sh
    (poetry) PYTHONPATH=./ mypy ./view/ ./module/ ./models/ ./celery_task/ ./structs/ ./api/ ./main.py
    ```

## Create a pull request
- Submit Pull Request to `main` branch.
- Before submitting your Pull Request, merge `main` to your branch and fix any conflicts.
- The codebase is follow the [Google Style Guide for Python](https://google.github.io/styleguide/pyguide.html).
- The docstring style please follow this section of
  [3.8 Comments and Docstrings](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings),
  but prefer using `'''` rather than `"""`.
- For Beginners: see here how to
  [forking](https://docs.github.com/en/get-started/quickstart/fork-a-repo) and
  [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) from GitHub
