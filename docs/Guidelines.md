# Guidelines

## How to contribute


- Sign the [deed of transfer](./files/form deed of transfer Book Zabbix.pdf) preferable electronically
- Clone this project to your Github account
- Clone the repository to you pc

- Install the needed software for Mkdocs to work,
  check the file in the root folder how-to-install-mkdocs.md
  - Create a new branch to make your changes
    - git branch "<your branch name\>"
    - git checkout "<your branch name\>"
  - Make the changes you want and commit them
    - git add "files you changed"
    - git commit -m "add useful commit info"
  - Return back to the main branch
    - git checkout main
  - Make sure you have the latest changes merged from main
    - git pull origin main
  - Merge your branch into the main branch
    - git merge "<your branch name\>"
    - git push
  - cleanup your branch
    - git branch -d "<your branch name\>"
- Create a pull requests so that we can merge it :)
- Follow these [guidelines](https://github.com/penmasters/zabbix-book/how-to-rules-for-writing.md) when you write a topic.
