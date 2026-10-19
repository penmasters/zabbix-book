# Translation status report

English Markdown files directly below `docs/` are the source. A translation
of `docs/ch01-zabbix-components/chapter.md`, for example, is expected at
`docs/nl/ch01-zabbix-components/chapter.md` for Dutch.

Fetch the branches, then run the overview. The tool reads English and translated
files directly with Git, so it does not switch branches and does not modify the
worktree:

```sh
git fetch origin
make translation-status
```

While the project is still developed entirely on `main`, the default English
source is `HEAD`. Translation branches that do not exist yet are represented by
their `docs/<locale>/` directories in the current worktree. Existing
translations have status **Unknown** until they are explicitly reviewed.

After `release/8.0` and the translation branches have been created, run the
same overview against that release:

```sh
make translation-status SOURCE_REF=release/8.0
```

The source may then exist as the local `release/8.0` branch or as the fetched
`origin/release/8.0` remote-tracking branch. The tool checks both without
checking either one out.

The overview contains one row for every language declared in
`.github/docs-versions.yml`. For a detailed page-by-page report, switch to that
translation branch and provide its locale:

```sh
git switch translation/8.0/nl
make translation-status LOCALE=nl
```

The report has four page states:

- **Up to date**: the translation exists and was reviewed against the current
  SHA-256 hash of the English source.
- **Needs review**: the English source changed after the recorded review.
- **Not translated**: the matching file under `docs/<locale>/` does not exist.
- **Unknown**: the translation exists but has never been explicitly marked as
  reviewed.

The report command is read-only. It never edits a translation and never marks a
changed translation as reviewed automatically.

After reviewing and, if needed, manually updating a translation, record that
review explicitly:

```sh
python3 tools/translation_status.py \
  --locale nl \
  --mark-reviewed ch01-zabbix-components/chapter.md
```

The equivalent Make target is:

```sh
make translation-mark-reviewed \
  LOCALE=nl \
  PAGE=ch01-zabbix-components/chapter.md
```

This creates or updates `translation-status.yml` in the repository root. Commit
that status file together with the reviewed translation. Each translation
branch keeps its own status file; do not copy one locale's status file to
another locale.

`HEAD` is the default source reference while development is on `main`. You can
select another local source ref explicitly, for example:

```sh
make translation-status LOCALE=nl SOURCE_REF=release/8.0
```
