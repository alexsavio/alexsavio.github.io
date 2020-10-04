Title: Git usage guidelines for team collaboration
Date: 2020-06-11 12:00:00
Category: Git
Tags: git, collaboration, team
Slug: git-collaboration-guidelines
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: Suggestions on how to use a code repository with git for teams.

## Introduction

This is a set of rules that I have been gathering in the past few years, which work well for most of the projects I worked on with small teams of 3-8 people. These guidelines are heavily based on the [angular.js/DEVELOPERS.md document on  GitHub](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines).
This is not about [GitFlow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow), I think it is too complex and goes against fast development cycles. Build good and reliable CI/CD pipelines to be able to deliver faster, use canary releases whenever possible.

## Branching model

Always create a new branch from an updated "master" branch.
The branches should have a short life (no more than 2 days) and have a very determined objective.
Once the objective is reached, a Pull Request (PR) should be created to merge the branch to “master”.
Once the branch is merged, it should be deleted.
Always merge to “master”.

### Branch names

The branch names are not that important in very small teams, but when the team is bigger or work remotely,
a pattern for the branch names is also good to follow. Here is a suggestion:

    ```python
    <type>/[<ticket_id>]_<subject>
    ```

Some tools like Sourcetree from Atlassian pick the `/` from the branch name and splits the name in their GUI,
so you can see the different types of branches as in different folders.

#### Type

The <type> describes the generic objective of the branch, it can be one of the following:

- **feat**: a new feature,
- **fix**: a bug fix,
- **docs**: documentation only changes (in or out of the code),
- **tests**: new tests or fixes in tests,
- **refactor**: code change that neither fixes a bug or adds a feature,
- **style**: code changes that neither,
- **chore**: Changes to the build process or auxiliary tools for the project maintenance,
- **perf**: A code change that improves performance.

#### Ticket ID

This is optional, but is good if the purpose of the branch is too complex or if you follow a Scrum development process.
The <ticket_id> should be the identifier of the ticket or user story that the branch is going to solve.
The format depends on the project management tool you are using, but usually it has a project acronym and a number: `PRJ_123`.

#### Subject

The <subject> part should be no more than 3 or 4 words about the specific objective of the branch.
If you don’t put a ticket ID, the specificity of the name is more relevant.

### Commit messages

Here we follow a very specific pattern in order to be able to parse the commit messages to automatically generate a
change log for each release in a CI/CD process and also semantic release version bumps
with tools like semantic-release (available for Node.js and Python).

#### Format

Each commit message consists of a header, a body and a footer. The header has a special format that includes a type, a scope and a subject:

    ```python
    <type>(<scope>): <subject>
    <BLANK LINE>
    <body>
    <BLANK LINE>
    <footer>
    ```

The header is mandatory and the scope of the header is optional.
Any line of the commit message cannot be longer 100 characters!
This allows the message to be easier to read on GitHub as well as in various git tools.

##### Type
The <type> describes the generic objective of the commit, use the same types used for branches. I will repeat them here:

- **feat**: a new feature,
- **fix**: a bug fix,
- **docs**: documentation only changes (in or out of the code),
- **tests**: new tests or fixes in tests,
- **refactor**: code change that neither fixes a bug or adds a feature,
- **style**: code changes that neither,
- **chore**: Changes to the build process or auxiliary tools for the project maintenance,
- **perf**: A code change that improves performance.

##### Scope

The <scope> could be anything specifying place of the commit change. A scope should be a part of the project that the stakeholders understand.
The possible scopes can be agreed beforehand with the developers and/or stakeholders.
You can use * when the change affects more than a single scope, but you can also not put anything (remove the parentheses as well).

##### Subject

The <subject> contains succinct description of the change:

- use the imperative, present tense: "change" not "changed" nor "changes"
- don't capitalize first letter
- no dot (.) at the end

Don’t use generic subjects as: 'debug' or 'few fixes'. Be clear and specific.

##### Body

The <body> is optional, but if you use it, just as in the subject, use the imperative, present tense: "change" not "changed" nor "changes".
The body should include the motivation for the change and contrast
this with the previous behavior.

##### Footer

The <footer> is optional. The footer should contain any information about Breaking Changes and is also the place to reference GitHub issues that this commit closes.
Breaking Changes should start with the word BREAKING CHANGE: with a space or two newlines. The rest of the commit message is then used for this.
A detailed explanation can be found in the Angular.js document.

### Pull Requests

The Pull or Merge Requests (PR) are used to share with your co-developers the code changes
you did in your branch and ask them to review it. Here we always do a PR from your branch to
the 'master' branch.
In a PR, your colleagues will have a view of the differences between the branches and the
commits. You must also add a title and a description.

The title should be sufficient to understand what is being changed.

In the description you should:

- make a useful description,
- describe what was changed in the pull request,
- explain why this PR exists,
- make it clear how it does what it sets out to do. E.g: Does it change a column in the database?

How is this being done? What happens to the old data?

- you may want to use screenshots to demonstrate what has changed if there is a
GUI involved in the project.

**Pull request size:** It should be small. The pull request must have a maximum of 250 lines of change.
**Feature breaking:** Whenever it’s possible break pull requests into smaller ones.
**Single Responsibility Principle:** The pull request should do only 1 thing.

### CI/CD

With this setup your CI/CD pipeline would:

1. run your checks and tests for every push to a PR and every merge to 'master',
2. run a deployment to your test environment every merge to 'master', and
3. enable a manual deployment to your production environment for every merge to 'master'.

This deployment should trigger a release first, with automatic version bumping
and change log generation. Bitbucket-pipelines supports this.

### <span style="color:red">Remember: git is a collaboration tool, not a reporting tool.</span>

### References

- [The anatomy of a perfect pull request – Hugo Dias – Medium](https://medium.com/@hugooodias/the-anatomy-of-a-perfect-pull-request-567382bb6067)
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.4/#specification)
- [Gitflow Workflow \| Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [angular.js/DEVELOPERS.md at master · angular/angular.js · GitHub](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines)
- [GitHub - semantic-release/semantic-release: Fully automated version management and package publishing](https://github.com/semantic-release/semantic-release)
