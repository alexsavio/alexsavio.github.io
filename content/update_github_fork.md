Title: How to keep a GitHub fork updated
Date: 2014-05-30 21:00:00
Category: Software
Tags: git, unix
Slug: keep_github_fork_updated
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: How to keep a GitHub fork updated
Status: draft

Keep a forked repository of **git/git** like **alexsavio/git** updated:

### Clone the forked repo

    ```bash
    git clone git@github.com:alexsavio/git.git
    cd git
    git remote add upstream git@github.com:git/git.git
    ```

### Update it

To update the forked repo from the local **master** branch:

    ```bash
    git fetch upstream
    git rebase upstream/master
    ```

### Commit rights upstream

If you also have commit rights to the upstream repo, you can create a
local **upstream** branch and do work that will go upstream there.

    ```bash
    git checkout -b upstream upstream/master
    ```

#### References

[1]<http://robots.thoughtbot.com/keeping-a-github-fork-updated>
