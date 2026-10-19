# Versioning migration runbook

This runbook applies the tested branch and website layout first to a fork and
then, after approval, to `penmasters/zabbix-book`. Commands are intentionally
split into local preparation, publication approval, remote creation, and Pages
cutover. Do not force-push or move a publication tag.

## Target state

| Website label | Source | URL | Changes accepted |
|---|---|---|---|
| Main (Development) | `main` | `/main/` | New English content and general development |
| 8.0 — English | `release/8.0` | `/8.0/en/` | English 8.0 corrections and errata only |
| 8.0 — German | `translation/8.0/de` | `/8.0/de/` | German translation work based on `v8.0-1` |

Every translation uses its own `translation/8.0/<locale>` branch based on the
final English `v8.0-1` tag. The current locales are `de`, `es`, `fr`, `it`, `nl`,
`pt_BR`, `ru`, `th`, and `zh`. Branch creation and website publication are
separate: all nine branches are declared in `.github/docs-versions.yml`, while
only entries with `website: true` are built and shown in the selector.

The initial migration retains every translation directory until all translation
branches have been created and verified. A later cleanup commit can remove the
translation directories from `main` and `release/8.0`, and remove unrelated
locale directories from each translation branch. Never delete the source copy
before its destination branch has been checked.

## Test-fork procedure

1. Confirm the checkout is clean and inspect the exact remote URL:

   ```sh
   git status --short --branch
   git remote -v
   tools/migrate_version_branches.sh plan
   ```

2. Merge this migration on `main`. Create the local English maintenance branch:

   ```sh
   tools/migrate_version_branches.sh create-branch --id release-8.0 --apply \
     --remote origin \
     --expected-url git@github.com:larcorba/zabbix-book.git
   ```

3. Review the English 8.0 content. Only after a maintainer records that edition
   1 is final, create and push an annotated tag. Replace `APPROVED_COMMIT` with
   the reviewed commit; never reuse or move the tag:

   ```sh
   git tag -a v8.0-1 APPROVED_COMMIT -m "Zabbix Book 8.0 English edition 1"
   git push origin refs/tags/v8.0-1
   ```

4. Create every translation branch from that tag, never from a moving branch:

   ```sh
   for id in \
     german-8.0 spanish-8.0 french-8.0 italian-8.0 dutch-8.0 \
     portuguese-brazil-8.0 russian-8.0 thai-8.0 chinese-8.0
   do
     tools/migrate_version_branches.sh create-branch --id "$id" --apply \
       --remote origin \
       --expected-url git@github.com:larcorba/zabbix-book.git
   done
   ```

5. Push each new branch only after verifying the fork remote again:

   ```sh
   tools/migrate_version_branches.sh push-branch --id release-8.0 --apply \
     --remote origin \
     --expected-url git@github.com:larcorba/zabbix-book.git
   for id in \
     german-8.0 spanish-8.0 french-8.0 italian-8.0 dutch-8.0 \
     portuguese-brazil-8.0 russian-8.0 thai-8.0 chinese-8.0
   do
     tools/migrate_version_branches.sh push-branch --id "$id" --apply \
       --remote origin \
       --expected-url git@github.com:larcorba/zabbix-book.git
   done
   ```

   Immediately add GitHub rulesets that block force-pushes and deletion for
   `release/8.0`, `translation/8.0/*`, and tags matching `v8.0-*`.

6. In repository settings, set Pages **Source** to **GitHub Actions**. Run the
   workflow manually once. Confirm `/main/`, `/8.0/en/`, `/8.0/de/`, the three
   selector labels, search, navigation, images, styles, and representative links.
   The workflow reads the test repository's Pages URL at build time, so test
   links and canonical URLs do not point at the production domain.

7. Create `v8.0-1-<locale>.1` only after editorial sign-off for that language.
   No translation tag is created merely because its branch exists.

8. After every translation branch has been checked, migrate branch ownership in
   normal reviewed commits:

   - Retain only English source on `main` and `release/8.0`.
   - Retain `docs/<locale>/` on its matching translation branch and remove the
     other locale directories from that branch.
   - Do not combine these cleanup commits with tag creation.

## Production reuse

Repeat the procedure in a fresh clone of `penmasters/zabbix-book`, changing only
the exact URL guard to `git@github.com:penmasters/zabbix-book.git` (or the exact
HTTPS URL actually configured). First compare production `main` with the tested
migration commit and open a normal pull request. Never copy the fork's Git refs.

Before the production Pages cutover, archive the current deployment branch and
decide whether existing language URLs should remain as static archives or
redirect elsewhere. Their branches are preserved, but only languages with
`website: true` appear in the selector.

## Add another language

Add one entry to `.github/docs-versions.yml`. Start with `website: false` so the
branch can be created without publishing an unfinished language. For example:

```yaml
  - id: french-8.0
    label: 8.0 — French
    branch: translation/8.0/fr
    language: fr
    path: 8.0/fr/
    status: development
    website: false
    base:
      type: tag
      ref: v8.0-1
    published_tag: v8.0-1-fr.1
```

Then create and push it with `create-branch --id french-8.0` and `push-branch
--id french-8.0`. No Python, JavaScript, validator, or workflow edit is needed.
The language directory is discovered automatically from `docs/fr/`; untranslated
pages fall back to English. Change the entry to `website: true` only after review.
Add a redirect entry only if an old URL must move.

## Rollback

1. Disable the versioned Pages workflow or revert its workflow commit.
2. Restore the previous Pages source/deployment artifact or archived `gh-pages`
   branch.
3. Point Pages back to the previous source in repository settings.
4. Delete newly created *unpublished* branches only after confirming no work was
   added. Never delete or move an edition tag that has been announced as published.

Rollback changes hosting only. Source branches and translation files remain in
Git and can be retried after correction.

## Known limitations and approval gates

- Mike itself rejects `/` in a version identifier, and Material's built-in Mike
  provider assumes sibling version directories. The required nested URLs use a
  small Material-styled selector that reads an extended Mike-format
  `versions.json` with explicit `url` fields.
- Switching GitHub Pages from branch deployment to Actions is a repository
  setting and must be approved by a repository administrator.
- The workflow requires every `website: true` branch. It does not require hidden
  translation branches with `website: false`.
- Every translation uses English fallback for untranslated pages; it must not be
  described as complete or published before editorial sign-off.
- Removal or archival of already-hosted language pages requires a separate
  decision before production cutover.
