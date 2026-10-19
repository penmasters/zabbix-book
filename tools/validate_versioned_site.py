#!/usr/bin/env python3
"""Validate a composed Pages artifact against docs-versions.yml."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        wanted = "href" if tag in {"a", "link"} else "src" if tag in {"img", "script"} else None
        if wanted:
            for name, value in attrs:
                if name == wanted and value:
                    self.values.append(value)


def exists(site: Path, page: Path, reference: str) -> bool:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("#", "mailto:", "tel:", "data:")):
        return True
    raw_path = unquote(parsed.path)
    if not raw_path:
        return True
    candidate = site / raw_path.lstrip("/") if raw_path.startswith("/") else page.parent / raw_path
    if raw_path.endswith("/"):
        candidate /= "index.html"
    elif candidate.is_dir():
        candidate /= "index.html"
    return candidate.exists()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", type=Path)
    parser.add_argument("--metadata", type=Path, default=Path(".github/docs-versions.yml"))
    args = parser.parse_args()
    site = args.site.resolve()

    metadata = yaml.safe_load(args.metadata.read_text(encoding="utf-8"))
    expected = [
        (str(item["id"]), str(item["label"]), str(item["path"]).strip("/") + "/")
        for item in metadata["versions"]
        if item.get("website", True)
    ]
    manifest = json.loads((site / "versions.json").read_text(encoding="utf-8"))
    actual = [(item["version"], item["title"], item["url"]) for item in manifest]
    if actual != expected:
        raise SystemExit(f"selector does not match metadata: {actual!r}")

    problems: list[str] = []
    for _version, _title, url in expected:
        root = site / url
        for required in ("index.html", "search/search_index.json", "assets"):
            if not (root / required).exists():
                problems.append(f"missing {url}{required}")
        index = root / "index.html"
        if index.is_file() and "data-version-manifest=" not in index.read_text(
            encoding="utf-8", errors="replace"
        ):
            problems.append(f"missing version selector hook in {url}index.html")

    pages = list(site.rglob("*.html"))
    for page in pages:
        parser_html = References()
        parser_html.feed(page.read_text(encoding="utf-8", errors="replace"))
        for reference in parser_html.values:
            if not exists(site, page, reference):
                problems.append(f"{page.relative_to(site)} -> {reference}")
                if len(problems) >= 50:
                    break
        if len(problems) >= 50:
            break

    if problems:
        raise SystemExit("Versioned-site validation failed:\n" + "\n".join(problems))
    print(
        f"Validated {len(expected)} versions and {len(pages)} HTML pages: "
        "selector, assets, search indexes, and local links"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
