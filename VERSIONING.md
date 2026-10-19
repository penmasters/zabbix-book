# Versioning and publishing

English is the source language. Development branches accept changes; published
edition tags are immutable and must never be moved, recreated, or force-pushed.

## Branch model

| Purpose | Git reference | Website path |
|---|---|---|
| English development | `main` | `/main/` |
| English 8.0 maintenance and errata | `release/8.0` | `/8.0/en/` |
| 8.0 translation development | `translation/8.0/<locale>` | `/8.0/<locale>/` when enabled |

Every translation branch starts from the finalized English `v8.0-1` tag. The
current locales are `de`, `es`, `fr`, `it`, `nl`, `pt_BR`, `ru`, `th`, and `zh`.
Branch existence and website publication are separate: only metadata entries
with `website: true` are built and shown in the selector.

## Create the initial branches

Run these commands only after the versioning pull request has been merged into
`main`. Start from a clean checkout and verify the official remote:

```sh
git status --short --branch
git remote get-url origin
git fetch origin --prune --tags
git ls-remote --heads origin release/8.0 'translation/8.0/*'
```

The remote must be `git@github.com:penmasters/zabbix-book.git`, or the equivalent
official HTTPS URL. The final command must not show a branch that you intend to
create. Never overwrite an existing branch.

Create the English maintenance branch from the reviewed `main` commit:

```sh
git switch main
git pull --ff-only origin main
git switch -c release/8.0
git push -u origin release/8.0
git switch main
```

Review the English 8.0 content on `release/8.0`. Only after maintainers approve
edition 1, replace `APPROVED_COMMIT` below with the reviewed commit ID and create
the annotated publication tag:

```sh
git tag -a v8.0-1 APPROVED_COMMIT -m "Zabbix Book 8.0 English edition 1"
git show v8.0-1
git push origin refs/tags/v8.0-1
```

After confirming the local and remote tag point to the approved commit, create
all translation branches from that immutable tag:

```sh
git fetch origin --tags
git rev-parse 'v8.0-1^{commit}'
git ls-remote origin refs/tags/v8.0-1 'refs/tags/v8.0-1^{}'

for locale in de es fr it nl pt_BR ru th zh
do
  git branch "translation/8.0/$locale" v8.0-1
  git push -u origin "translation/8.0/$locale"
done
```

These commands do not use force. Stop if any local or remote branch already
exists and inspect it instead of replacing it.

Immediately add GitHub rulesets that block force-pushes and deletion for
`release/8.0`, `translation/8.0/*`, and tags matching `v8.0-*`.

## Move existing translation work

The initial versioning commit retains every translation directory so no work is
lost. After all destination branches exist and have been checked:

- Retain only English source on `main` and `release/8.0`.
- On each translation branch, retain its matching `docs/<locale>/` directory and
  remove the other locale directories.
- Make the cleanup through normal reviewed commits.
- Never delete a source copy before its destination branch has been verified.

## Publish the website

Before the Pages cutover, archive the current deployment and decide whether old
language URLs should remain as static archives or redirect elsewhere. Then set
GitHub Pages **Source** to **GitHub Actions** and run the workflow.

Verify `/main/`, `/8.0/en/`, every enabled language path, selector labels,
search, navigation, images, styles, and representative links. The workflow
requires every `website: true` branch; it ignores hidden entries.

## Enable or add a language

For an existing translation branch, change its metadata entry from
`website: false` to `website: true` only after editorial review. The next
deployment builds it and adds it to the selector.

For a new locale, first add an entry to `.github/docs-versions.yml` with
`website: false`. For example:

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

Create `translation/8.0/<locale>` from `v8.0-1`, push it without force, and add
`docs/<locale>/`. Untranslated pages fall back to English. No Python,
JavaScript, validator, or workflow change is required.

Create `v8.0-1-<locale>.1` only after editorial sign-off for that language. The
final `.1` is the first translated publication based on English `v8.0-1`; later
translation-only corrections can use `.2`, `.3`, and so on.

## Rollback

1. Disable the versioned Pages workflow or revert its workflow commit.
2. Restore the previous Pages artifact or archived `gh-pages` branch.
3. Point Pages back to the previous source in repository settings.
4. Delete newly created unpublished branches only after confirming no work was
   added. Never delete or move an announced publication tag.

Rollback changes hosting only. Source branches and translation files remain in
Git and can be retried after correction.

## Known limitations

- Mike rejects `/` in a version identifier, and Material's built-in Mike
  provider assumes sibling version directories. The nested URLs therefore use
  a small Material-styled selector with explicit paths in `versions.json`.
- Every translation uses English fallback for untranslated pages and must not be
  described as complete before editorial sign-off.
- Archiving or redirecting existing language URLs requires a separate decision
  before the production Pages cutover.
