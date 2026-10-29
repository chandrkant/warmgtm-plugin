"""Checks a staged OpenAI plugin package against the directory's submission rules.

Usage: python3 scripts/check-openai-package.py <package-dir>
Exits non-zero with a list of problems; prints "OK" otherwise.
Limits are from https://developers.openai.com/plugins/deploy/submission.
"""
import json
import re
import struct
import sys
from pathlib import Path

pkg = Path(sys.argv[1])
problems = []


def need(cond, msg):
    if not cond:
        problems.append(msg)


plugin = json.loads((pkg / "plugin.json").read_text())
mcp = json.loads((pkg / "mcp.json").read_text())

need(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", plugin.get("name", "")) and len(plugin["name"]) <= 64,
     "name must be lowercase letters/numbers with single hyphens, <= 64 chars")
need(re.fullmatch(r"\d+\.\d+\.\d+", plugin.get("version", "")), "version must be explicit semver")
need(len(plugin.get("description", "")) <= 4000, "description > 4000 chars")

oa = plugin.get("extensions", {}).get("com.openai", {})
ui = oa.get("interface", {})
for field, limit in [("displayName", 30), ("shortDescription", 30), ("longDescription", 4000), ("developerName", 80)]:
    need(ui.get(field), f"interface.{field} is required")
    need(len(ui.get(field, "")) <= limit, f"interface.{field} > {limit} chars")
need(ui.get("category"), "interface.category is required")
for field in ["websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"]:
    url = ui.get(field, "")
    need(url.startswith("https://") and len(url) <= 1024 and "@" not in url, f"interface.{field} must be an HTTPS URL")
caps = ui.get("capabilities", [])
need(len(caps) <= 20 and all(len(c) <= 120 for c in caps), "capabilities: at most 20, each <= 120 chars")
prompts = ui.get("defaultPrompt", [])
prompts = [prompts] if isinstance(prompts, str) else prompts
need(len(prompts) <= 3 and all(len(p) <= 128 for p in prompts), "defaultPrompt: at most 3, each <= 128 chars")
need(len(set(prompts)) == len(prompts), "defaultPrompt entries must be unique")
for color in ["brandColor", "brandColorDark"]:
    if color in ui:
        need(re.fullmatch(r"#[0-9A-Fa-f]{6}", ui[color]), f"{color} must be #RRGGBB")


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


for icon in ["logo", "composerIcon"]:
    rel = ui.get(icon)
    need(rel and rel.startswith("./"), f"interface.{icon} must be a ./ relative path")
    if rel:
        path = pkg / rel
        need(path.is_file(), f"{icon} file missing: {rel}")
        if path.is_file():
            need(path.stat().st_size <= 5 * 1024 * 1024, f"{icon} > 5 MiB")
            size = png_size(path)
            need(size and size[0] == size[1] and 48 <= size[0] <= 4096, f"{icon} must be a square PNG 48-4096px, got {size}")

cases = oa.get("review", {}).get("test_cases", {})
pos, neg = cases.get("positive", []), cases.get("negative", [])
need(len(pos) == 5, f"need exactly 5 positive test cases, have {len(pos)}")
need(len(neg) == 3, f"need exactly 3 negative test cases, have {len(neg)}")
for i, c in enumerate(pos):
    for k in ["description", "prompt", "tools_triggered", "expected_behavior"]:
        need(c.get(k), f"positive[{i}].{k} is required")
for i, c in enumerate(neg):
    for k in ["description", "prompt"]:
        need(c.get(k), f"negative[{i}].{k} is required")

need(mcp.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "mcp.json $schema missing or wrong")
need(set(mcp) <= {"$schema", "mcpServers"}, "mcp.json has unknown top-level keys")
servers = mcp.get("mcpServers", {})
need(len(servers) == 1, "mcp.json must declare exactly one MCP server")
for name, server in servers.items():
    need(server.get("url", "").startswith("https://"), f"server {name} needs a public HTTPS url")
    need(not server.get("headers"), f"server {name} must not set headers")
    auth = server.get("extensions", {}).get("com.openai", {}).get("auth", {})
    need(auth.get("type") in {"oauth", "mixed"}, f"server {name} auth must be oauth for a protected server")
    need("clientSecret" not in json.dumps(auth), "clientSecret must not be in the package")

need(not (pkg / ".app.json").exists() and "apps" not in oa and "hooks" not in oa, "apps / hooks can't be submitted")
for skill in pkg.glob("skills/*/SKILL.md"):
    head = skill.read_text().split("---")
    need(len(head) >= 3 and re.search(r"^name:\s*\S", head[1], re.M) and re.search(r"^description:\s*\S", head[1], re.M),
         f"{skill.relative_to(pkg)} needs name and description frontmatter")
need(any(pkg.glob("skills/*/SKILL.md")), "no skills found")

secret_pattern = re.compile(r"(api[_-]?key|password|secret)\s*[:=]\s*['\"][^'\"]{6,}", re.I)
for f in pkg.rglob("*"):
    if f.is_file() and f.suffix in {".json", ".md"}:
        need(not secret_pattern.search(f.read_text()), f"{f.relative_to(pkg)} looks like it contains a credential")

if problems:
    print("Package check failed:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("OK")
