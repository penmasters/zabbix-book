#!/usr/bin/env python3
"""Build every website version declared in .github/docs-versions.yml."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

import yaml


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
        if relative.parts[0] in excluded_directories or relative == Path("CNAME"):
            continue
        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)


def prepare_docs(repository: Path, language: str) -> None:
    source = repository / "docs"
    target = repository / ".build" / "docs"
    if not source.is_dir():
        raise SystemExit(f"documentation directory not found: {source}")

    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    excluded = translation_dirs(source) | {"overrides"}
    copy_tree(source, target, excluded_directories=excluded)

    translated = 0
    if language != "en":
        language_source = source / language
        if not language_source.is_dir():
            raise SystemExit(f"translation directory not found: {language_source}")
        translated = sum(1 for path in language_source.rglob("*.md") if path.is_file())
        copy_tree(language_source, target)

    total = sum(1 for path in target.rglob("*.md") if path.is_file())
    fallback = total - translated if language != "en" else 0
    details = (
        f" ({translated} {language} translations, {fallback} English fallback)"
        if language != "en"
        else ""
    )
    print(f"Prepared {language}: {total} Markdown files{details}")


def safe_relative(value: str, field: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not value.strip("/"):
        raise SystemExit(f"{field} must be a safe relative path: {value!r}")
    return value.strip("/") + "/"


def load_metadata(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    versions = data.get("versions", [])
    if not versions:
        raise SystemExit("metadata must declare at least one version")

    seen: dict[str, set[str]] = {key: set() for key in ("id", "label", "branch", "path")}
    aliases: set[str] = set()
    required = ("id", "label", "branch", "language", "path", "status", "base")
    for version in versions:
        missing = [key for key in required if key not in version]
        if missing:
            raise SystemExit(f"version entry is missing {', '.join(missing)}: {version!r}")
        version["path"] = safe_relative(str(version["path"]), f"{version['id']}.path")
        for key in seen:
            value = str(version[key])
            if value in seen[key]:
                raise SystemExit(f"duplicate {key}: {value}")
            seen[key].add(value)

        website = version.get("website", True)
        if not isinstance(website, bool):
            raise SystemExit(f"{version['id']}.website must be true or false")

        raw_aliases = version.get("aliases", [])
        if not isinstance(raw_aliases, list):
            raise SystemExit(f"{version['id']}.aliases must be a list")
        version["aliases"] = []
        for raw_alias in raw_aliases:
            alias = safe_relative(str(raw_alias), f"{version['id']}.aliases")
            if alias in aliases:
                raise SystemExit(f"duplicate alias: {alias}")
            aliases.add(alias)
            version["aliases"].append(alias)

    data["default_path"] = safe_relative(str(data["default_path"]), "default_path")
    website_paths = {
        str(version["path"])
        for version in versions
        if version.get("website", True)
    }
    if not website_paths:
        raise SystemExit("metadata must declare at least one website version")
    if data["default_path"] not in website_paths:
        raise SystemExit("default_path must match a website-enabled version path")
    collisions = aliases & seen["path"]
    if collisions:
        raise SystemExit(f"aliases collide with version paths: {', '.join(sorted(collisions))}")
    return data


def redirect(destination: str) -> str:
    escaped = html.escape(destination, quote=True)
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<meta http-equiv=\"refresh\" content=\"0; url={escaped}\">"
        f"<link rel=\"canonical\" href=\"{escaped}\"></head>"
        f"<body><a href=\"{escaped}\">Continue</a></body></html>\n"
    )


def resolve_branch(repository: Path, branch: str) -> str:
    for candidate in (f"refs/remotes/origin/{branch}", f"refs/heads/{branch}"):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"{candidate}^{{commit}}"],
            cwd=repository,
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            return candidate
    raise SystemExit(f"required branch is unavailable locally: {branch}")


def materialize(repository: Path, branch: str, destination: Path) -> Path:
    reference = resolve_branch(repository, branch)
    destination.mkdir(parents=True)
    process = subprocess.Popen(
        ["git", "archive", "--format=tar", reference],
        cwd=repository,
        stdout=subprocess.PIPE,
    )
    assert process.stdout is not None
    with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
        for member in archive:
            member_path = PurePosixPath(member.name)
            link_path = PurePosixPath(member.linkname) if member.issym() or member.islnk() else None
            if (
                member_path.is_absolute()
                or ".." in member_path.parts
                or (link_path and (link_path.is_absolute() or ".." in link_path.parts))
                or member.isdev()
            ):
                raise SystemExit(f"unsafe path in Git archive: {member.name}")
            archive.extract(member, destination)
    if process.wait() != 0:
        raise SystemExit(f"git archive failed for {branch}")
    return destination


def build(
    source: Path,
    version: dict,
    destination: Path,
    base_url: str,
) -> None:
    if not (source / "mkdocs.yml").is_file():
        raise SystemExit(f"mkdocs.yml not found in {source}")
    subject_index = source / "tools" / "build_subject_index.py"
    if subject_index.is_file():
        subprocess.run([sys.executable, str(subject_index), "--check"], check=True, cwd=source)
    prepare_docs(source, str(version["language"]))
    environment = os.environ.copy()
    environment.update(
        {
            "ZABBIX_BOOK_DOCS_DIR": ".build/docs",
            "ZABBIX_BOOK_EDIT_URI": f"edit/{version['branch']}/docs/",
            "ZABBIX_BOOK_SITE_URL": base_url + version["path"],
            "ZABBIX_BOOK_THEME_LANGUAGE": str(version["language"]),
            "ZABBIX_BOOK_VERSION_MANIFEST": base_url + "versions.json",
        }
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--clean",
            "--config-file",
            "mkdocs.yml",
            "--site-dir",
            str(destination),
        ],
        check=True,
        cwd=source,
        env=environment,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--metadata", type=Path, default=Path(".github/docs-versions.yml"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-url", default="https://thezabbixbook.com/")
    parser.add_argument(
        "--use-current-checkout",
        action="store_true",
        help="Use the current files for every version; intended only for local preview.",
    )
    args = parser.parse_args()

    repository = args.repository.resolve()
    metadata_path = args.metadata if args.metadata.is_absolute() else repository / args.metadata
    metadata = load_metadata(metadata_path.resolve())
    output = args.output.resolve()
    if ".build" not in output.parts:
        parser.error("--output must be inside a .build directory")
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True)

    source_root = repository / ".build" / "version-sources"
    if not args.use_current_checkout:
        shutil.rmtree(source_root, ignore_errors=True)
        source_root.mkdir(parents=True)

    base_url = args.base_url.rstrip("/") + "/"
    manifest = []
    for version in metadata["versions"]:
        if not version.get("website", True):
            continue
        source = (
            repository
            if args.use_current_checkout
            else materialize(repository, str(version["branch"]), source_root / str(version["id"]))
        )
        build(source=source, version=version, destination=output / version["path"], base_url=base_url)
        manifest.append(
            {
                "version": str(version["id"]),
                "title": str(version["label"]),
                "aliases": version["aliases"],
                "url": version["path"],
            }
        )

    (output / "versions.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "index.html").write_text(redirect(metadata["default_path"]), encoding="utf-8")
    for version in metadata["versions"]:
        if not version.get("website", True):
            continue
        for alias in version["aliases"]:
            redirect_dir = output / alias
            redirect_dir.mkdir(parents=True, exist_ok=True)
            relative = os.path.relpath(output / version["path"], redirect_dir).replace(os.sep, "/") + "/"
            (redirect_dir / "index.html").write_text(redirect(relative), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
