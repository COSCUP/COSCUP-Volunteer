# How to sign-off commits

We require a sign-off commit message in the following format on each commit in pull request.

```text
This is a commit message.

COSCUP Volunteer <volunteer@coscup.org>
```

## Creating your signoff

Git has a `-s | --sign-off` command line option to append the message automatically.

```bash
git commit --signoff --message 'This is a commit message'
git commit -s -m 'This is a commit message'
```

This will use your default value on your git configure in `user.name`, `user.email`.

Setup your name:

```bash
git config user.name 'FIRST_NAME LAST_NAME'
```

Setup your mail:

```bash
git config user.email 'MY_EMAIL@example.com'
```

## How to amend a sign-off

If you miss your sign-off on the last commit, you can amend the commit and then push to Github.

```bash
git commit --amend --signoff
```

## DCO Failures

If you miss series of commits, you can use the rebase with `-i | --interactive` to edit and append into.

???+ Example

    If you have 4 commits in your history.

    ```bash
    git rebase --interactive HEAD~4
    (interactive squash + DCO append)
    git push origin --force
    ```

???+ Info

    We will enable the Probot/DCO on Github. For more details about
    the DCO on Github, please read the
    [article here](https://github.blog/changelog/2022-06-08-admins-can-require-sign-off-on-web-based-commits/).
