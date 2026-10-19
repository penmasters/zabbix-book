# The Zabbix Book

English is the source language. Choose the branch for your change before opening
a pull request:

| Change | Pull request target |
|---|---|
| New English content and general development | `main` |
| Corrections and errata for English 8.0 | `release/8.0` |
| Translation work for 8.0 | `translation/8.0/<locale>` |

`<locale>` matches the translation directory, for example `de`, `fr`, or
`pt_BR`. Do not send new English features to `release/8.0`, and do not edit the
English source on a translation branch.

## Branch and publication model

```text
main (English development)                              [DEV]
|
`-- release/8.0 (English maintenance and errata)        [MAINTENANCE]
    |
    `-- v8.0-1 (English edition 1)                      [IMMUTABLE TAG]
        |
        |-- translation/8.0/de (German development)     [DEV]
        |   `-- v8.0-1-de.1 (German edition 1)          [IMMUTABLE TAG]
        |
        |-- translation/8.0/fr (French development)     [DEV]
        |   `-- v8.0-1-fr.1 (French edition 1)          [IMMUTABLE TAG]
        |
        `-- translation/8.0/<locale>                    [DEV]
            `-- v8.0-1-<locale>.1                       [IMMUTABLE TAG]
```

Each translation branch starts from the finalized English `v8.0-1` tag. The
current translation locales are `de`, `es`, `fr`, `it`, `nl`, `pt_BR`, `ru`,
`th`, and `zh`; each receives its own `translation/8.0/<locale>` branch.

Branches accept reviewed changes. Published edition tags are frozen snapshots:
never move, recreate, or force-update `v8.0-1`,
`v8.0-1-<locale>.1`, or any later publication tag.

A translation branch does not automatically appear on the website. Set
`website: true` for its entry in `.github/docs-versions.yml` only after the
language is ready. The selector, builder, validator, deployment workflow, and
release documentation all use that metadata. Entries with `website: false`
declare a branch without publishing it.

See [VERSIONING.md](VERSIONING.md) for the branch, release, deployment, and
rollback procedure.
Website versions are declared once in `.github/docs-versions.yml`; the builder,
selector, validator, and deployment workflow all read that file.

Translation branches can compare their pages with the English release without
switching branches. See [TRANSLATION_STATUS.md](TRANSLATION_STATUS.md) for the
read-only report and the explicit review command.

Please before you start take a look at our most updated license : [License](https://github.com/penmasters/zabbix-book/blob/main/readme.md)
on Github.

*The Zabbix Book* is a freely accessible resource designed to help users understand
and master Zabbix. Contributions are highly encouraged to improve and expand its
content. However, the book is distributed under the
**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)**
license, meaning it is free for non-commercial use only.

Contributors should be aware that:  

- By contributing to this work, you irrevocably assign and transfer all rights, title,
and interest in your contributions to **The Monitoring Penmasters Foundation**,
including any associated intellectual property rights, to the fullest extent permitted
by law.
- **The Monitoring Penmasters Foundation** reserves the right to use, reproduce,
modify, distribute, and commercially exploit any contributed material in any form,
including but not limited to the publication of physical and digital books.
- All contributors must sign a **Deed of Transfer of Intellectual Property Rights**
before making any contributions, ensuring the proper transfer of rights and handling
of the content by **The Monitoring Penmasters Foundation**. Any contributions without
a signed **Deed of Transfer of Intellectual Property Rights** cannot be accepted.
- All profits generated will be used by The Monitoring Penmasters Foundation to
cover operational expenses and to sponsor other open-source projects, as determined
by the foundation.

Your contributions are invaluable and will help make *The Zabbix Book* an even greater
resource for the entire community!

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

Read the book here :
[https://www.thezabbixbook.com](https://www.thezabbixbook.com)

Help us Translate the book :
[https://weblate.thezabbixbook.com](https://weblate.thezabbixbook.com)

Contribute to the book :
[https://github.com/penmasters/zabbix-book/blob/main/how-to-rules-for-writing.md](https://github.com/penmasters/zabbix-book/blob/main/how-to-rules-for-writing.md)

## Contributors

Thanks for your contribution to the project!

![Contributors Count](https://img.shields.io/github/contributors/penmasters/zabbix-book)

[![Contributors Avatars](https://contrib.rocks/image?repo=penmasters/zabbix-book)](https://github.com/penmasters/zabbix-book/graphs/contributors)
