#!/usr/bin/env python3
"""Safely create and push branches declared in docs-versions.yml."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], text=True, capture_output=True)
    if check and result.returncode:
        raise SystemExit(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def metadata(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))["versions"]


def select(versions: list[dict], identifier: str) -> dict:
    for version in versions:
        if version["id"] == identifier:
            return version
    raise SystemExit(f"unknown version id: {identifier}")


def remote_ref(remote: str, ref: str) -> str:
    result = subprocess.run(
        ["git", "ls-remote", remote, ref], text=True, capture_output=True, check=True
    )
    return result.stdout.split()[0] if result.stdout.strip() else ""


def require_mutation(args: argparse.Namespace) -> None:
    if not args.apply or not args.remote or not args.expected_url:
        raise SystemExit("--apply, --remote, and --expected-url are required")
    actual = git("remote", "get-url", args.remote)
    if actual != args.expected_url:
        raise SystemExit(f"remote URL is {actual!r}, expected {args.expected_url!r}")
    if git("status", "--porcelain"):
        raise SystemExit("working tree is not clean")


def local_commit(reference: str) -> str:
    for candidate in (f"refs/heads/{reference}", f"refs/remotes/origin/{reference}", reference):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"{candidate}^{{commit}}"],
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    raise SystemExit(f"base reference is unavailable: {reference}")


def create_branch(args: argparse.Namespace, versions: list[dict]) -> None:
    require_mutation(args)
    version = select(versions, args.id)
    branch = str(version["branch"])
    if branch == "main":
        raise SystemExit("main already exists and is not a migration branch")
    local_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"]
    ).returncode == 0
    if local_exists:
        raise SystemExit(f"local branch already exists: {branch}")
    if remote_ref(args.remote, f"refs/heads/{branch}"):
        raise SystemExit(f"remote branch already exists: {branch}")

    base = version["base"]
    base_ref = str(base["ref"])
    commit = local_commit(base_ref)
    if base["type"] == "tag":
        if git("cat-file", "-t", f"refs/tags/{base_ref}", check=False) != "tag":
            raise SystemExit(f"{base_ref} must be an annotated local tag")
        remote_commit = remote_ref(args.remote, f"refs/tags/{base_ref}^{{}}")
        if not remote_commit or remote_commit != commit:
            raise SystemExit(f"remote annotated tag {base_ref} is missing or differs locally")
    elif base["type"] != "branch":
        raise SystemExit(f"unsupported base type: {base['type']}")

    git("branch", branch, commit)
    print(f"Created local {branch} from {base_ref}; nothing was pushed.")


def push_branch(args: argparse.Namespace, versions: list[dict]) -> None:
    require_mutation(args)
    version = select(versions, args.id)
    branch = str(version["branch"])
    if branch == "main":
        raise SystemExit("push main through the normal reviewed pull-request workflow")
    local = git("rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}")
    if remote_ref(args.remote, f"refs/heads/{branch}"):
        raise SystemExit(f"refusing to overwrite existing remote branch: {branch}")
    git("push", args.remote, f"{local}:refs/heads/{branch}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=Path(".github/docs-versions.yml"))
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan")
    for command in ("create-branch", "push-branch"):
        child = subparsers.add_parser(command)
        child.add_argument("--id", required=True)
        child.add_argument("--apply", action="store_true")
        child.add_argument("--remote")
        child.add_argument("--expected-url")
    args = parser.parse_args()
    versions = metadata(args.metadata)

    if args.command == "plan":
        for version in versions:
            base = version["base"]
            tag = version.get("published_tag", "not assigned")
            website = "website enabled" if version.get("website", True) else "website disabled"
            print(
                f"{version['id']}: {version['branch']} -> {version['path']} "
                f"({version['status']}, {website}, base {base['type']} {base['ref']}, "
                f"tag {tag})"
            )
        print("No plan operation changes Git or a remote.")
    elif args.command == "create-branch":
        create_branch(args, versions)
    else:
        push_branch(args, versions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
