# JARVIS

> Your local AI assistant. No cloud. No subscriptions. No bullshit.

JARVIS runs entirely on your machine. It talks, it listens, it remembers, it acts.
One `pnpm dev` and you're talking to a full AI assistant that keeps its mouth shut
about your data — because it never leaves your computer.

---

## The "Holy Shit" Moment
```
You: "Hey JARVIS"
JARVIS: "Yes?"
You: "Research the best mechanical keyboards under $150, draft a comparison table,
      and send it to my email."
JARVIS: "On it. Done. Check your inbox."
```

No API key. No internet required after setup. Runs on a 3-year-old laptop.

---

## Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| RAM | 8 GB | 16 GB+ |
| Node.js | 20+ | 20 LTS |
| Python | 3.11 | 3.11 |
| pnpm | 9+ | latest |
| Ollama | 0.3+ | latest |

GPU is optional. Everything degrades gracefully.

---

## Quick Start
```bash
# 1. Clone
git clone https://github.com/your-org/jarvis.git
cd jarvis

# 2. Install Node dependencies
corepack enable
pnpm install

# 3. Set up Python environments (one per service)
bash scripts/setup_python_envs.sh

# 4. Check your hardware — get recommended loop tier
python scripts/check_hardware.py

# 5. Copy and fill in your env file
cp .env.example .env
# edit .env — at minimum set JARVIS_AUTH_TOKEN

# 6. Install Ollama (if not already installed)
# https://ollama.ai — then:
ollama pull llama3.2

# 7. Start JARVIS
pnpm dev
```

Navigate to `http://localhost:5173` to open the web UI,
or say "Hey JARVIS" if your mic is plugged in.

---

## Architecture
```
Voice / Discord / Telegram / Web UI / iMessage
             ↓
    Gateway (WebSocket, Node.js)
             ↓
       Core Engine (Python)
      /    |     \      \
  ECHO  ATLAS  NEXUS  QUANTUM  ← Loop tiers (complexity-matched)
             ↓
     Memory (Hot RAM + Cold SQLite/FAISS)
             ↓
         Skills (sandboxed)
   Browser · Email · Terminal · Git · Files
```

See `docs/architecture/overview.md` for the full picture.

---

## Loop Tiers

| Tier | When | What |
|------|------|------|
| **ECHO** | Simple Q&A, lookups | Single-pass, fast, quantized |
| **ATLAS** | Multi-step tasks | Shadow execution, checkpointing |
| **NEXUS** | Destructive/code actions | Transactional, validator pool, rollback |
| **QUANTUM** | Research, creative, complex | 3–5 parallel branches, validator swarm |

JARVIS selects the right tier automatically based on task complexity and your hardware.

---

## Project Status

> **Iteration 1 of 35** — Repo scaffold only. Nothing runs yet.
> Follow the iteration plan in `JARVIS_IMPLEMENTATION_GUIDE.md`.

| Phase | Status |
|-------|--------|
| Phase 1 — Foundation | 🔨 In progress |
| Phase 2 — Channels | ⏳ Pending |
| Phase 3 — Tools | ⏳ Pending |
| Phase 4 — Intelligence | ⏳ Pending |
| Phase 5 — Power Features | ⏳ Pending |
| Phase 6 — Personalization | ⏳ Pending |
| Phase 7 — Ecosystem | ⏳ Pending |

---

## Non-Negotiables

1. **Local-first.** Data never leaves your machine without your explicit say-so.
2. **100% free.** No subscriptions, no required cloud services.
3. **Runs on 8GB RAM.** GPU is never required.
4. **All four loop tiers ship.** ECHO, ATLAS, NEXUS, QUANTUM.
5. **Memory persists and retrieves correctly.**
6. **Security is built in** — sandboxed skills, permission declarations, human gates.
7. **Contributor-friendly** — touch any part without understanding the whole.

---

## License

MIT — see [LICENSE](./LICENSE)
```

---

**PATH:** `LICENSE`
**ACTION:** add
```
MIT License

Copyright (c) 2025 JARVIS Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.