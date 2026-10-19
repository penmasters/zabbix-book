# Руководство

## Как внести свой вклад

- Подпишите, желательно в электронном виде,
  [https://www.thezabbixbook.com/files/form%20deed%20of%20transfer%20Book%20Zabbix.pdf](https://www.thezabbixbook.com/files/form%20deed%20of%20transfer%20Book%20Zabbix.pdf)
- Клонируйте этот проект в свою учётную запись GitHub
- Клонируйте репозиторий на свой компьютер

- Установите программное обеспечение, необходимое для работы MkDocs.
  Дополнительные сведения см. в файле how-to-install-mkdocs.md в корневом каталоге
  - Создайте новую ветку для внесения изменений
    - git branch "<your branch name\>"
    - git checkout "<your branch name\>"
  - Внесите нужные изменения и создайте коммит
    - git add "files you changed"
    - git commit -m "add useful commit info"
  - Вернитесь в ветку main
    - git checkout main
  - Убедитесь, что получили последние изменения из ветки main
    - git pull origin main
  - Объедините свою ветку с веткой main
    - git merge "<your branch name\>"
    - git push
  - Удалите больше не нужную ветку
    - git branch -d "<your branch name\>"
- Создайте pull request, чтобы мы могли объединить ваши изменения :)
- При написании материала следуйте этим правилам:
  [https://github.com/penmasters/zabbix-book/blob/main/how-to-rules-for-writing.md](https://github.com/penmasters/zabbix-book/blob/main/how-to-rules-for-writing.md)
