#!/usr/bin/env bash
set -e
# Qinglong stores its Environment Variables in this generated shell file.
source /ql/shell/preload/env.sh
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec /opt/ylpl-venv/bin/python -E "$script_dir/run_qinglong.py" "$@"
