#!/usr/bin/env python3
"""Create one language-specific MkDocs source tree without altering docs/."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


LOCALE_DIRECTORY = re.compile(r"^[a-z]{2}(?:_[A-Z]{2})?$")


def translation_dirs(source: Path) -> set[str]:
    return {
        path.name
        for path in source.iterdir()
        if path.is_dir() and LOCALE_DIRECTORY.fullmatch(path.name)
    }


def copy_tree(
    source: Path,
    target: Path,
    *,
    excluded_directories: set[str] | None = None,
) -> None:
    excluded_directories = excluded_directories or set()
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if relative.parts[0] in excluded_directories:
            continue
        if relative == Path("CNAME"):
            continue
        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--language", required=True)
    args = parser.parse_args()

    repository = args.repository.resolve()
    source = repository / "docs"
    target = repository / ".build" / "docs"
    target.relative_to(repository / ".build")

    if not source.is_dir():
        parser.error(f"documentation directory not found: {source}")

    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    translations = translation_dirs(source)
    copy_tree(source, target, excluded_directories=translations)

    translated = 0
    if args.language != "en":
        language_source = source / args.language
        if not language_source.is_dir():
            parser.error(f"translation directory not found: {language_source}")
        translated = sum(1 for path in language_source.rglob("*.md") if path.is_file())
        copy_tree(language_source, target)

    total = sum(1 for path in target.rglob("*.md") if path.is_file())
    fallback = total - translated if args.language != "en" else 0
    print(
        f"Prepared {args.language}: {total} Markdown files"
        + (
            f" ({translated} {args.language} translations, {fallback} English fallback)"
            if args.language != "en"
            else ""
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
