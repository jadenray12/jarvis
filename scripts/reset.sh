#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# JARVIS Nuclear Reset
# Wipes all runtime data, caches, venvs, and node_modules.
# USE WITH CAUTION — this cannot be undone.
# Run: bash scripts/reset.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              JARVIS NUCLEAR RESET                        ║"
echo "║                                                          ║"
echo "║  This will permanently delete:                           ║"
echo "║   - All memory data (data/)                              ║"
echo "║   - All logs (logs/)                                     ║"
echo "║   - All Python venvs (packages/*/.venv)                  ║"
echo "║   - All node_modules                                     ║"
echo "║   - All build artifacts (dist/, build/)                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
read -r -p "Type YES to confirm: " confirm

if [ "$confirm" != "YES" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Resetting..."

# Runtime data
rm -rf "$ROOT_DIR/data/"
rm -rf "$ROOT_DIR/logs/"
rm -rf "$ROOT_DIR/.jarvis_session/"
rm -rf "$ROOT_DIR/memory_store/"
rm -rf "$ROOT_DIR/action_log/"

# Python venvs
for pkg in core voice memory skills; do
    rm -rf "$ROOT_DIR/packages/$pkg/.venv"
done

# Node modules + build artifacts
find "$ROOT_DIR" -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$ROOT_DIR" -name "dist"         -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$ROOT_DIR" -name "build"        -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$ROOT_DIR" -name "*.tsbuildinfo"        -exec rm -f  {} + 2>/dev/null || true
find "$ROOT_DIR" -name "__pycache__"  -type d -prune -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Reset complete. Re-run setup to start fresh:            ║"
echo "║                                                          ║"
echo "║    pnpm install                                          ║"
echo "║    bash scripts/setup_python_envs.sh                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
```

---
```
TESTS

COMMAND: pnpm --version
EXPECTED OUTPUT: 9.x.x (or higher)

COMMAND: test -f jarvis.config.yaml && echo "config OK"
EXPECTED OUTPUT: config OK

COMMAND: test -f .env.example && echo "env OK"
EXPECTED OUTPUT: env OK

COMMAND: ls packages/*/pyproject.toml | wc -l
EXPECTED OUTPUT: 4

COMMAND: ls packages/*/package.json | wc -l
EXPECTED OUTPUT: 4  (gateway, channels, ui, skills)

COMMAND: bash scripts/setup_python_envs.sh
EXPECTED OUTPUT: "All Python environments are ready." with no errors

COMMAND: python scripts/check_hardware.py
EXPECTED OUTPUT: Hardware summary + recommended tier (ECHO, ATLAS, or NEXUS)
                 All required tools show ✅ except those not yet installed

COMMAND: ls skills/community/.gitkeep
EXPECTED OUTPUT: skills/community/.gitkeep  (file exists)
```

---
```
RUN COMMANDS

# Ensure you are in the repo root

node --version
# Must print v20.x.x or higher

corepack enable
pnpm install

bash scripts/setup_python_envs.sh

cp .env.example .env
# Open .env and set JARVIS_AUTH_TOKEN at minimum

python scripts/check_hardware.py
```

---
```
GIT

COMMIT_COMMANDS:
  git init                          # if not already a git repo
  git add .
  git commit -m "feat: iteration 1 — repo scaffold

  - Monorepo root with pnpm workspaces
  - jarvis.config.yaml and .env.example
  - Package manifests and tsconfigs for gateway, channels, ui
  - pyproject.toml + requirements.txt for core, voice, memory, skills
  - scripts/setup_python_envs.sh, check_hardware.py, reset.sh
  - Root README.md and LICENSE"

PR:
  title: "feat: iteration 1 — repo scaffold"
  body: |
    Sets up the complete JARVIS monorepo structure per the Implementation Guide.
    Nothing runs yet — this is the foundation every subsequent iteration builds on.

    **Checklist:**
    - [ ] pnpm install completes without errors
    - [ ] setup_python_envs.sh creates .venv in all 4 Python packages
    - [ ] check_hardware.py runs and prints a tier recommendation
    - [ ] .env created from .env.example
```

---
```
VERIFICATION CHECKLIST

[ ] repo root contains: package.json, pnpm-workspace.yaml, .nvmrc, .python-version,
    .gitignore, .env.example, jarvis.config.yaml, README.md, LICENSE
[ ] pnpm install completes — node_modules present at root and in each TS package
[ ] packages/gateway/, packages/channels/, packages/ui/ each have package.json + tsconfig.json
[ ] packages/core/, packages/voice/, packages/memory/, packages/skills/ each have
    pyproject.toml + requirements.txt
[ ] bash scripts/setup_python_envs.sh creates .venv in all 4 Python packages
[ ] python scripts/check_hardware.py runs without crashing and prints tier recommendation
[ ] skills/community/.gitkeep exists
[ ] ITERATION_MANIFESTS/iteration-1.json saved to repo
[ ] .env exists (copied from .env.example) — NOT committed to git
[ ] .gitignore correctly ignores .env, node_modules, .venv, data/, logs/
```

---
```
ROLLBACK

git checkout -- .
git clean -fd
# This restores all tracked files and removes any untracked files/dirs
# (including node_modules, .venv directories, etc.)
# If you already committed: git revert HEAD
```

---
```
NEXT ITERATION SUGGESTIONS

1. Iteration 2 — Gateway Core
   Build the WebSocket server on ws://127.0.0.1:18789 with token auth,
   session management, and message routing. This is the nervous system
   every other package plugs into.

2. Iteration 3 — Core Engine + CLI
   Python agent core, Ollama client, and a text-mode CLI connected to
   the gateway. This is the first moment JARVIS actually responds to input.

3. (Optional pre-work) Model download
   If you want Iteration 3 to work immediately out of the box, run:
     ollama pull llama3.2
   now so the model is ready when the engine first calls it.