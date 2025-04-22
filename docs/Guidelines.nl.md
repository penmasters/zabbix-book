# Richtlijnen

## Hoe u kunt bijdragen


- Onderteken de [akte van overdracht](./files/form deed of transfer Book
  Zabbix.pdf)bij voorkeur elektronisch
- Kloon dit project naar uw Github account
- Kloon de repository naar uw pc

- Installeer de benodigde software om Mkdocs te laten werken. Controleer het
  bestand in de hoofdmap how-to-install-mkdocs.md
  - Maak een nieuwe branch om uw wijzigingen door te voeren
    - git branch ""
    - git checkout ""
  - Maak de gewenste wijzigingen en commit ze
    - git add "bestanden die je hebt gewijzigd"
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
- Follow these
  [guidelines](https://github.com/penmasters/zabbix-book/how-to-rules-for-writing.md)
  when you write a topic.
