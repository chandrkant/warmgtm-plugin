#!/usr/bin/env bash
# Builds the OpenAI (ChatGPT / Codex) plugin ZIP from openai/ plus the shared
# skill and logo, checks it against the directory's submission limits, and
# writes dist/warmgtm-openai-<version>.zip.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
version="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$root/openai/plugin.json")"
out="$root/dist/warmgtm-openai-$version.zip"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

cp "$root/openai/plugin.json" "$root/openai/mcp.json" "$stage/"
mkdir -p "$stage/skills" "$stage/assets"
cp -R "$root/skills/." "$stage/skills/"
cp "$root/assets/logo.png" "$stage/assets/"

python3 "$root/scripts/check-openai-package.py" "$stage"

mkdir -p "$root/dist"
rm -f "$out"
python3 - "$stage" "$out" <<'EOF'
import sys, zipfile
from pathlib import Path
stage, out = Path(sys.argv[1]), sys.argv[2]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(p for p in stage.rglob("*") if p.is_file()):
        z.write(f, f.relative_to(stage).as_posix())
    for name in z.namelist():
        print("  ", name)
EOF
echo "Built $out"
