# Richtlijnen

## Hoe u kunt bijdragen


- Sign the [deed of
  transfer](https://www.thezabbixbook.com/files/form%20deed%20of%20transfer%20Book%20Zabbix.pdf)
  preferable electronically
- Kloon dit project naar uw Github account
- Kloon de repository naar uw pc

- Installeer de benodigde software om Mkdocs te laten werken. Controleer het
  bestand in de hoofdmap how-to-install-mkdocs.md
  - Maak een nieuwe branch om uw wijzigingen door te voeren
    - git branch ""
    - git checkout ""
  - Maak de gewenste wijzigingen en commit ze
    - git add "bestanden die je hebt gewijzigd"
    - git commit -m "voeg nuttige commit info toe"
  - Terug naar de hoofdtak
    - git checkout main
  - Zorg ervoor dat je de laatste wijzigingen hebt samengevoegd vanuit het
    hoofdgedeelte
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
