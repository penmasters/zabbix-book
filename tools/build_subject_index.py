#!/usr/bin/env python3
"""Build and validate the curated subject index for the Zabbix Book."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from markdown import Markdown


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
DEFAULT_SOURCE = ROOT / "index" / "en.yml"
DEFAULT_OUTPUT = DOCS_DIR / "subject-index.md"


class IndexError(ValueError):
    """Raised when curated index data is invalid."""


@dataclass(frozen=True)
class Target:
    label: str
    start: str
    end: str | None = None


@dataclass(frozen=True)
class Subterm:
    term: str
    targets: tuple[Target, ...]


@dataclass(frozen=True)
class Entry:
    term: str
    targets: tuple[Target, ...]
    subterms: tuple[Subterm, ...]
    see: str | None
    see_also: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate data and fail when the generated file is not current.",
    )
    return parser.parse_args()


def require_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IndexError(f"{context} must be a non-empty string")
    return value.strip()


def parse_targets(raw: Any, context: str) -> tuple[Target, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise IndexError(f"{context}.targets must be a list")

    targets: list[Target] = []
    for number, item in enumerate(raw, start=1):
        target_context = f"{context}.targets[{number}]"
        if not isinstance(item, dict):
            raise IndexError(f"{target_context} must be a mapping")
        unknown = set(item) - {"label", "start", "end"}
        if unknown:
            raise IndexError(
                f"{target_context} has unknown fields: {', '.join(sorted(unknown))}"
            )
        label = require_string(item.get("label"), f"{target_context}.label")
        start = require_string(item.get("start"), f"{target_context}.start")
        end_value = item.get("end")
        end = require_string(end_value, f"{target_context}.end") if end_value else None
        targets.append(Target(label=label, start=start, end=end))
    return tuple(targets)


def load_entries(source: Path) -> tuple[Entry, ...]:
    try:
        raw_document = yaml.safe_load(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IndexError(f"Index source does not exist: {source}") from exc
    except yaml.YAMLError as exc:
        raise IndexError(f"Invalid YAML in {source}: {exc}") from exc

    if not isinstance(raw_document, dict) or not isinstance(
        raw_document.get("entries"), list
    ):
        raise IndexError(f"{source} must contain an 'entries' list")

    entries: list[Entry] = []
    for number, item in enumerate(raw_document["entries"], start=1):
        context = f"entries[{number}]"
        if not isinstance(item, dict):
            raise IndexError(f"{context} must be a mapping")
        unknown = set(item) - {"term", "targets", "subterms", "see", "see_also"}
        if unknown:
            raise IndexError(f"{context} has unknown fields: {', '.join(sorted(unknown))}")

        term = require_string(item.get("term"), f"{context}.term")
        targets = parse_targets(item.get("targets"), context)
        see_value = item.get("see")
        see = require_string(see_value, f"{context}.see") if see_value else None

        raw_see_also = item.get("see_also", [])
        if not isinstance(raw_see_also, list):
            raise IndexError(f"{context}.see_also must be a list")
        see_also = tuple(
            require_string(value, f"{context}.see_also") for value in raw_see_also
        )

        raw_subterms = item.get("subterms", [])
        if not isinstance(raw_subterms, list):
            raise IndexError(f"{context}.subterms must be a list")
        subterms: list[Subterm] = []
        for sub_number, raw_subterm in enumerate(raw_subterms, start=1):
            sub_context = f"{context}.subterms[{sub_number}]"
            if not isinstance(raw_subterm, dict):
                raise IndexError(f"{sub_context} must be a mapping")
            unknown_sub = set(raw_subterm) - {"term", "targets"}
            if unknown_sub:
                raise IndexError(
                    f"{sub_context} has unknown fields: "
                    f"{', '.join(sorted(unknown_sub))}"
                )
            subterm = require_string(raw_subterm.get("term"), f"{sub_context}.term")
            sub_targets = parse_targets(raw_subterm.get("targets"), sub_context)
            if not sub_targets:
                raise IndexError(f"{sub_context} must have at least one target")
            subterms.append(Subterm(term=subterm, targets=sub_targets))

        if see and (targets or subterms):
            raise IndexError(f"{context} cannot combine 'see' with targets or subterms")
        if not (targets or subterms or see or see_also):
            raise IndexError(f"{context} does not contain any index information")

        entries.append(
            Entry(
                term=term,
                targets=targets,
                subterms=tuple(subterms),
                see=see,
                see_also=see_also,
            )
        )
    return tuple(entries)


def anchor_id(text: str) -> str:
    value = text.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return "index-" + value.strip("-")


def split_target(target: str) -> tuple[Path, str | None]:
    page, separator, fragment = target.partition("#")
    if not page or page.startswith(("/", "http://", "https://")) or ".." in Path(page).parts:
        raise IndexError(f"Index target must be a relative docs path: {target}")
    if not page.endswith(".md"):
        raise IndexError(f"Index target must point to a Markdown page: {target}")
    return DOCS_DIR / page, fragment if separator else None


def collect_heading_ids(page: Path) -> set[str]:
    markdown = Markdown(extensions=["toc", "attr_list"])
    markdown.convert(page.read_text(encoding="utf-8"))

    found: set[str] = set()

    def walk(tokens: list[dict[str, Any]]) -> None:
        for token in tokens:
            identifier = token.get("id")
            if identifier:
                found.add(identifier)
            walk(token.get("children", []))

    walk(getattr(markdown, "toc_tokens", []))
    return found


def validate_target(target: str, heading_cache: dict[Path, set[str]]) -> None:
    page, fragment = split_target(target)
    if not page.is_file():
        raise IndexError(f"Index target page does not exist: {target}")
    if fragment:
        if page not in heading_cache:
            heading_cache[page] = collect_heading_ids(page)
        if fragment not in heading_cache[page]:
            relative = page.relative_to(DOCS_DIR)
            raise IndexError(f"Heading '#{fragment}' does not exist in {relative}")


def validate_entries(entries: tuple[Entry, ...]) -> None:
    known: dict[str, str] = {}
    heading_cache: dict[Path, set[str]] = {}

    for entry in entries:
        key = entry.term.casefold()
        if key in known:
            raise IndexError(f"Duplicate index term: {entry.term!r} and {known[key]!r}")
        known[key] = entry.term

        seen_subterms: set[str] = set()
        for subterm in entry.subterms:
            sub_key = subterm.term.casefold()
            if sub_key in seen_subterms:
                raise IndexError(
                    f"Duplicate subterm {subterm.term!r} under {entry.term!r}"
                )
            seen_subterms.add(sub_key)
            known[f"{key}, {sub_key}"] = f"{entry.term}, {subterm.term}"

        for target in entry.targets:
            validate_target(target.start, heading_cache)
            if target.end:
                validate_target(target.end, heading_cache)
        for subterm in entry.subterms:
            for target in subterm.targets:
                validate_target(target.start, heading_cache)
                if target.end:
                    validate_target(target.end, heading_cache)

    for entry in entries:
        references = ((entry.see,) if entry.see else ()) + entry.see_also
        for reference in references:
            if reference.casefold() not in known:
                raise IndexError(
                    f"Cross-reference {reference!r} from {entry.term!r} is undefined"
                )


def markdown_link(label: str, target: str, css_class: str) -> str:
    return f"[{label}]({target}){{ .{css_class} }}"


def render_target(target: Target) -> str:
    rendered = markdown_link(target.label, target.start, "index-target")
    if target.end:
        rendered += markdown_link("", target.end, "index-range-end")
    return rendered


def render_entries(entries: tuple[Entry, ...], source: Path) -> str:
    entries = tuple(sorted(entries, key=lambda entry: entry.term.casefold()))
    canonical = {
        entry.term.casefold(): anchor_id(entry.term)
        for entry in entries
    }
    for entry in entries:
        for subterm in entry.subterms:
            canonical[f"{entry.term.casefold()}, {subterm.term.casefold()}"] = anchor_id(
                f"{entry.term}-{subterm.term}"
            )

    lines = [
        "---",
        "description: |",
        "    An alphabetical subject index for the Zabbix Book, with links to the",
        "    sections where each concept is explained or configured.",
        "---",
        "",
        "# Subject index",
        "",
        "Use this index to find concepts, configuration tasks, and troubleshooting",
        "topics throughout the book. On the website, each locator is a link. In the",
        "print edition, locators are rendered as page numbers.",
        "",
        "<!-- This file is generated. Edit index/en.yml and run",
        "     python3 tools/build_subject_index.py instead. -->",
        "",
        '<nav class="subject-index-letters" aria-label="Subject index letters" markdown>',
    ]

    letters = sorted({entry.term[0].upper() for entry in entries})
    lines.append(
        " · ".join(f'[{letter}](#index-letter-{letter.casefold()})' for letter in letters)
    )
    lines.extend(["</nav>", "", '<div class="subject-index" markdown>', ""])

    current_letter: str | None = None
    for entry in entries:
        letter = entry.term[0].upper()
        if letter != current_letter:
            if current_letter is not None:
                lines.append("")
            lines.extend(
                [
                    f'## {letter} {{#index-letter-{letter.casefold()}}}',
                    "",
                ]
            )
            current_letter = letter

        lines.append(f'- <span id="{anchor_id(entry.term)}"></span>**{entry.term}**')
        for target in entry.targets:
            lines.append(f"    - {render_target(target)}")
        for subterm in sorted(entry.subterms, key=lambda item: item.term.casefold()):
            sub_id = anchor_id(f"{entry.term}-{subterm.term}")
            for target_number, target in enumerate(subterm.targets):
                prefix = f'<span id="{sub_id}"></span>' if target_number == 0 else ""
                lines.append(f"    - {prefix}{render_target(target)}")
        if entry.see:
            destination = canonical[entry.see.casefold()]
            lines.append(f"    - *See* [{entry.see}](#{destination})")
        if entry.see_also:
            references = ", ".join(
                f"[{reference}](#{canonical[reference.casefold()]})"
                for reference in entry.see_also
            )
            lines.append(f"    - *See also* {references}")

    lines.extend(["", "</div>", ""])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()

    try:
        entries = load_entries(source)
        validate_entries(entries)
        rendered = render_entries(entries, source)
    except IndexError as exc:
        print(f"subject-index: {exc}", file=sys.stderr)
        return 1

    if args.check:
        try:
            current = output.read_text(encoding="utf-8")
        except FileNotFoundError:
            current = ""
        if current != rendered:
            print(
                f"subject-index: {output.relative_to(ROOT)} is stale; run "
                "python3 tools/build_subject_index.py",
                file=sys.stderr,
            )
            return 1
        print(f"subject-index: validated {len(entries)} entries")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"subject-index: wrote {output.relative_to(ROOT)} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
