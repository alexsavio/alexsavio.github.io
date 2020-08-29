Title: Remove big files from a git repositor
Date: 2017-12-30 12:28:00
Category: Git
Tags: git, clean, trash
Slug: git-cleanup-bfg
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: Remove large blobs from your git repository history

### Introduction

[BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) is a tool to "remove large or troublesome blobs" from Git repositories.

Here goes a quick guide on how to remove files larger than 10 MiB.

### Installation

Download the lastest release from https://rtyley.github.io/bfg-repo-cleaner/.
It includes a `.jar` file which we will use through the command line.

You can use `bfg` as an alias for `java -jar ~/Software/bfg-1.12.16.jar`.
Meaning that "`~/Software/bfg-1.12.16.jar`" is wherever you downloaded the `.jar` file.

```bash
alias bfg=java -jar ~/Software/bfg-1.12.16.jar
```

### First step

First you must delete the blobs that you want to delete from the HEAD of your repository, commit, and push.

### Usage

Clone your repository in mirror mode:

```bash
git clone --mirror git://example.com/some-big-repo.git
```

Run BFG to delete files bigger than 10MiB (see more examples in the project documentation):

```bash
bfg --strip-blobs-bigger-than 10M some-big-repo.git
```

Prune the reference log entries and push:

```bash
cd some-big-repo.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push
```

### References

 1. <https://rtyley.github.io/bfg-repo-cleaner/>
