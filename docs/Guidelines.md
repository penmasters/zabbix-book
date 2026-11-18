# Guidelines

## How to contribute

- Sign the [https://www.thezabbixbook.com/files/form%20deed%20of%20transfer%20Book%20Zabbix.pdf](https://www.thezabbixbook.com/files/form%20deed%20of%20transfer%20Book%20Zabbix.pdf) preferably electronically
- Clone this project to your GitHub account
- Clone the repository to your PC

Choose the target branch for your contribution: `main` for new English content,
`release/8.0` for English 8.0 corrections, or `translation/8.0/<locale>` for
translation work. Use that branch in place of `<target branch>` below.

- Install the needed software for MkDocs to work,
  check the file in the root folder how-to-install-mkdocs.md
  - Create a new branch to make your changes
    - git branch "<your branch name\>"
    - git checkout "<your branch name\>"
  - Make the changes you want and commit them
    - git add "files you changed"
    - git commit -m "add useful commit info"
  - Return to the target branch
    - `git checkout <target branch>`
  - Make sure you have the latest changes merged from the target branch
    - `git pull origin <target branch>`
  - Merge your branch into the target branch
    - git merge "<your branch name\>"
    - git push
  - clean up your branch
    - git branch -d "<your branch name\>"
- Create a pull request so that we can merge it :)
- Follow these [https://github.com/penmasters/zabbix-book/blob/main/how-to-rules-for-writing.md](https://github.com/penmasters/zabbix-book/blob/main/how-to-rules-for-writing.md) when you write a topic.
