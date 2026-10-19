#!/usr/bin/env python3
"""Report and explicitly record translation review status.

English Markdown pages are read directly from a Git ref. The overview reads
each translation and status file from its declared branch. A locale-specific
report reads the current worktree. No report checks out or modifies a branch.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from typing import Any

import yaml


STATUS_FILE = "translation-status.yml"
SCHEMA_VERSION = 1


class TranslationStatusError(RuntimeError):
    """An expected, user-facing translation status error."""


def git(repo: Path, *args: str, text: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
        check=False,
    )
    if result.returncode:
        message = result.stderr.strip()
        if isinstance(message, bytes):
            message = message.decode("utf-8", errors="replace")
        raise TranslationStatusError(message or f"git {' '.join(args)} failed")
    return result.stdout


def repository_root() -> Path:
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise TranslationStatusError("run this command inside a Git repository") from exc
    return Path(root)


def resolve_source_ref(repo: Path, source_ref: str) -> str:
    candidates = [source_ref]
    if not source_ref.startswith(("origin/", "refs/")):
        candidates.append(f"origin/{source_ref}")
    for candidate in candidates:
        try:
            git(repo, "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}")
            return candidate
        except TranslationStatusError:
            pass
    raise TranslationStatusError(
        f"source ref {source_ref!r} is not available locally; fetch it first"
    )


def validate_locale(locale: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", locale):
        raise TranslationStatusError(f"invalid locale: {locale!r}")


def git_blob(repo: Path, source_ref: str, path: str) -> bytes:
    return git(repo, "cat-file", "blob", f"{source_ref}:{path}")  # type: ignore[return-value]


def configured_locales(repo: Path, source_ref: str) -> set[str]:
    locales: set[str] = set()
    candidates: list[bytes] = []
    metadata = repo / ".github" / "docs-versions.yml"
    if metadata.is_file():
        candidates.append(metadata.read_bytes())
    try:
        candidates.append(git_blob(repo, source_ref, ".github/docs-versions.yml"))
    except TranslationStatusError:
        pass

    for raw in candidates:
        try:
            data = yaml.safe_load(raw) or {}
        except yaml.YAMLError:
            continue
        for entry in data.get("versions", []):
            if isinstance(entry, dict):
                language = entry.get("language")
                if isinstance(language, str) and language != "en":
                    locales.add(language)
    return locales


def source_pages(repo: Path, source_ref: str, locale: str) -> dict[str, str]:
    output = git(repo, "ls-tree", "-r", "-z", "--name-only", source_ref, "--", "docs")
    assert isinstance(output, bytes)
    locales = configured_locales(repo, source_ref) | {locale}
    pages: dict[str, str] = {}
    for raw_path in output.split(b"\0"):
        if not raw_path:
            continue
        full_path = raw_path.decode("utf-8", errors="strict")
        path = PurePosixPath(full_path)
        if path.suffix.lower() != ".md" or len(path.parts) < 2:
            continue
        relative = PurePosixPath(*path.parts[1:])
        if relative.parts[0] in locales:
            continue
        digest = hashlib.sha256(git_blob(repo, source_ref, full_path)).hexdigest()
        pages[relative.as_posix()] = digest
    return dict(sorted(pages.items()))


def empty_status(locale: str, source_ref: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "locale": locale,
        "source_ref": source_ref,
        "reviewed": {},
    }


def parse_status(
    raw: str | bytes, name: str, locale: str, source_ref: str
) -> dict[str, Any]:
    try:
        data = yaml.safe_load(raw)
    except (UnicodeError, yaml.YAMLError) as exc:
        raise TranslationStatusError(f"cannot read {name}: {exc}") from exc
    if not isinstance(data, dict):
        raise TranslationStatusError(f"{name} must contain a YAML mapping")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise TranslationStatusError(
            f"{name} has unsupported schema_version {data.get('schema_version')!r}"
        )
    if data.get("locale") != locale:
        raise TranslationStatusError(
            f"{name} belongs to locale {data.get('locale')!r}, not {locale!r}"
        )
    if data.get("source_ref") != source_ref:
        raise TranslationStatusError(
            f"{name} uses source_ref {data.get('source_ref')!r}, not {source_ref!r}"
        )
    reviewed = data.get("reviewed")
    if not isinstance(reviewed, dict):
        raise TranslationStatusError(f"{name}: reviewed must be a mapping")
    for page, entry in reviewed.items():
        if not isinstance(page, str) or not isinstance(entry, dict):
            raise TranslationStatusError(f"{name}: invalid reviewed entry")
        digest = entry.get("source_sha256")
        if (
            not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-fA-F]{64}", digest)
        ):
            raise TranslationStatusError(
                f"{name}: {page!r} has an invalid source_sha256"
            )
    return data


def load_status(path: Path, locale: str, source_ref: str) -> dict[str, Any]:
    if not path.exists():
        return empty_status(locale, source_ref)
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TranslationStatusError(f"cannot read {path.name}: {exc}") from exc
    return parse_status(raw, path.name, locale, source_ref)


def status_at_ref(
    repo: Path, translation_ref: str, locale: str, source_ref: str
) -> dict[str, Any]:
    listing = git(repo, "ls-tree", "--name-only", translation_ref, "--", STATUS_FILE)
    assert isinstance(listing, bytes)
    if not listing.strip():
        return empty_status(locale, source_ref)
    raw = git_blob(repo, translation_ref, STATUS_FILE)
    return parse_status(raw, f"{translation_ref}:{STATUS_FILE}", locale, source_ref)


def classify(
    repo: Path, locale: str, pages: dict[str, str], status: dict[str, Any]
) -> dict[str, list[str]]:
    translated = {
        page
        for page in pages
        if (repo / "docs" / locale / Path(page)).is_file()
    }
    return classify_pages(pages, status, translated)


def classify_pages(
    pages: dict[str, str], status: dict[str, Any], translated: set[str]
) -> dict[str, list[str]]:
    groups = {
        "Up to date": [],
        "Needs review": [],
        "Not translated": [],
        "Unknown": [],
    }
    reviewed = status["reviewed"]
    for page, current_digest in pages.items():
        if page not in translated:
            groups["Not translated"].append(page)
        elif page not in reviewed:
            groups["Unknown"].append(page)
        elif reviewed[page]["source_sha256"] == current_digest:
            groups["Up to date"].append(page)
        else:
            groups["Needs review"].append(page)
    return groups


def translated_pages_at_ref(repo: Path, translation_ref: str, locale: str) -> set[str]:
    prefix = f"docs/{locale}/"
    output = git(
        repo,
        "ls-tree",
        "-r",
        "-z",
        "--name-only",
        translation_ref,
        "--",
        f"docs/{locale}",
    )
    assert isinstance(output, bytes)
    translated: set[str] = set()
    for raw in output.split(b"\0"):
        if not raw:
            continue
        path = raw.decode("utf-8", errors="strict")
        if path.startswith(prefix) and path.lower().endswith(".md"):
            translated.add(path[len(prefix) :])
    return translated


def translated_pages_in_worktree(repo: Path, locale: str) -> set[str]:
    root = repo / "docs" / locale
    if not root.is_dir():
        return set()
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*.md")
        if path.is_file()
    }


def translation_branches(repo: Path) -> list[tuple[str, str]]:
    metadata = repo / ".github" / "docs-versions.yml"
    try:
        data = yaml.safe_load(metadata.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise TranslationStatusError(f"cannot read {metadata}: {exc}") from exc
    branches: list[tuple[str, str]] = []
    for entry in data.get("versions", []):
        if not isinstance(entry, dict) or entry.get("language") == "en":
            continue
        locale = entry.get("language")
        branch = entry.get("branch")
        if isinstance(locale, str) and isinstance(branch, str):
            validate_locale(locale)
            branches.append((locale, branch))
    if not branches:
        raise TranslationStatusError("no translation branches declared in docs-versions.yml")
    return branches


def print_overview(
    source_ref: str,
    results: list[tuple[str, str, dict[str, list[str]] | None]],
) -> None:
    print("Translation status overview")
    print(f"English source: {source_ref}")
    print()
    print("Locale  Up to date  Needs review  Not translated  Unknown  Branch")
    print("------  ----------  ------------  --------------  -------  ------")
    for locale, branch, groups in results:
        if groups is None:
            print(f"{locale:<6}  {'unavailable':<49}  {branch}")
            continue
        print(
            f"{locale:<6}  {len(groups['Up to date']):>10}  "
            f"{len(groups['Needs review']):>12}  "
            f"{len(groups['Not translated']):>14}  "
            f"{len(groups['Unknown']):>7}  {branch}"
        )


def report_all(repo: Path, source_ref: str, source_git_ref: str) -> int:
    pages = source_pages(repo, source_git_ref, "")
    results: list[tuple[str, str, dict[str, list[str]] | None]] = []
    worktree_fallback = False
    for locale, branch in translation_branches(repo):
        try:
            translation_ref = resolve_source_ref(repo, branch)
        except TranslationStatusError:
            status = empty_status(locale, source_ref)
            translated = translated_pages_in_worktree(repo, locale)
            results.append(
                (locale, f"worktree ({branch} not created)", classify_pages(pages, status, translated))
            )
            worktree_fallback = True
            continue
        status = status_at_ref(repo, translation_ref, locale, source_ref)
        translated = translated_pages_at_ref(repo, translation_ref, locale)
        results.append((locale, branch, classify_pages(pages, status, translated)))
    print_overview(source_ref, results)
    if worktree_fallback:
        print(
            "\nBranches that do not exist yet were read from the current worktree; "
            "their existing translations are Unknown until explicitly reviewed."
        )
    return 0


def print_report(
    locale: str,
    source_ref: str,
    groups: dict[str, list[str]],
    stale_entries: list[str],
) -> None:
    total = sum(len(items) for items in groups.values())
    print(f"Translation status: {locale}")
    print(f"English source:    {source_ref}")
    print()
    print(f"Total pages:       {total:4d}")
    for label in ("Up to date", "Needs review", "Not translated", "Unknown"):
        print(f"{label + ':':18s} {len(groups[label]):4d}")
    for label in ("Needs review", "Not translated", "Unknown"):
        if groups[label]:
            print(f"\n{label}:")
            for page in groups[label]:
                print(f"  {page}")
    if stale_entries:
        print("\nStatus entries without an English source page:")
        for page in stale_entries:
            print(f"  {page}")


def normalize_page(value: str, locale: str) -> str:
    path = PurePosixPath(value.replace(os.sep, "/"))
    parts = list(path.parts)
    if parts[:1] == ["docs"]:
        parts.pop(0)
    if parts[:1] == [locale]:
        parts.pop(0)
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise TranslationStatusError(f"invalid page path: {value!r}")
    normalized = PurePosixPath(*parts)
    if normalized.is_absolute() or normalized.suffix.lower() != ".md":
        raise TranslationStatusError(f"page must be a relative Markdown path: {value!r}")
    return normalized.as_posix()


def write_status(path: Path, data: dict[str, Any]) -> None:
    rendered = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def mark_reviewed(
    repo: Path,
    locale: str,
    source_ref: str,
    source_git_ref: str,
    status_path: Path,
    requested_pages: list[str],
) -> None:
    pages = source_pages(repo, source_git_ref, locale)
    status = load_status(status_path, locale, source_ref)
    normalized_pages = [normalize_page(page, locale) for page in requested_pages]
    for page in normalized_pages:
        if page not in pages:
            raise TranslationStatusError(
                f"{page!r} is not an English Markdown page in {source_ref}"
            )
        translation = repo / "docs" / locale / Path(page)
        if not translation.is_file():
            raise TranslationStatusError(f"translation does not exist: docs/{locale}/{page}")
    for page in normalized_pages:
        status["reviewed"][page] = {"source_sha256": pages[page]}
    status["reviewed"] = dict(sorted(status["reviewed"].items()))
    write_status(status_path, status)
    for page in normalized_pages:
        print(f"Marked reviewed: docs/{locale}/{page}")
    print(f"Updated {status_path.name}; commit it together with the reviewed translation.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--locale", help="translation directory under docs/")
    scope.add_argument("--all", action="store_true", help="summarize every declared language")
    parser.add_argument(
        "--source-ref", default="HEAD", help="Git ref containing English source"
    )
    parser.add_argument(
        "--status-file", default=STATUS_FILE, help="status file relative to repository root"
    )
    parser.add_argument(
        "--mark-reviewed",
        nargs="+",
        metavar="PAGE",
        help="explicitly record the current source hash for one or more translated pages",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        repo = repository_root()
        source_git_ref = resolve_source_ref(repo, args.source_ref)
        if args.all:
            if args.mark_reviewed:
                raise TranslationStatusError("--mark-reviewed requires --locale")
            return report_all(repo, args.source_ref, source_git_ref)
        validate_locale(args.locale)
        status_path = repo / args.status_file
        if status_path.parent != repo:
            raise TranslationStatusError("--status-file must be in the repository root")
        if args.mark_reviewed:
            mark_reviewed(
                repo,
                args.locale,
                args.source_ref,
                source_git_ref,
                status_path,
                args.mark_reviewed,
            )
            return 0
        pages = source_pages(repo, source_git_ref, args.locale)
        status = load_status(status_path, args.locale, args.source_ref)
        groups = classify(repo, args.locale, pages, status)
        stale = sorted(set(status["reviewed"]) - set(pages))
        print_report(args.locale, args.source_ref, groups, stale)
        return 0
    except TranslationStatusError as exc:
        print(f"translation-status: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
