#!/usr/bin/env bash
set -euo pipefail
exec python3 "$(dirname "$0")/migrate_version_branches.py" "$@"
