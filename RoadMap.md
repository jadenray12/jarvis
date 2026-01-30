# JARVIS Development Roadmap — Moltbot Features Integrated

> **Note:** This document is an *edited/expanded* version of your existing roadmap. It adds concrete, implementable steps for every Moltbot-inspired feature you asked for (connectivity, memory, context management, tools, automation, agentic loops, lobster shell, multi-agent, jobs, HITL, autonomous processes, privacy/local-first, command execution, file management, persistent memory, infinite context, browser control, scheduling, gateway, user profile, two-layer memory, vector+BM25 search, compaction, and more). Use this as a drop-in replacement or appendix to the roadmap you already have.

---

## Quick orientation

- This file builds on the Gateway/Skills/Memory-first architecture in the base roadmap.
- Each feature below contains: **what** you'll implement, **how** you'll implement it (tech choices & architecture), **tests & safety**, **success metrics**, and **priority/phase** mapping to the original timeline.

---

# Moltbot‑Specific Feature Implementations

> Implementation notes below assume a Node.js/TypeScript control plane (Gateway/Skills) with local services in Python where appropriate (embeddings, FAISS). Swap to Java for parts you prefer, but the public ecosystem has stronger tooling for multi-channel and skill libraries in TS/Node.

---

## 1) Gateway & Connectivity — hardened, extensible control plane

**What:** A single WebSocket-based Gateway that mediates clients (mobile apps, WebChat, Discord, socials), skills, and tool execution. All commands and events flow through it.

**How (implementation):**
- Reuse the existing `ws`/Socket layer from roadmap Phase 1. Build a strict session handshake: `HELLO -> AUTH (pairing token or user token) -> READY`.
- Connection types: `client`, `skill`, `agent-worker`, `remote-gateway`.
- Messages are versioned JSON envelopes: `{type, id, session, timestamp, auth, payload}`.
- Include presence & negotiation (capabilities exchange) so clients advertise what they support (TTS, display, input types).
- Gateway plugins: channel adapters register with the Gateway at runtime (Discord, WhatsApp, Telegram, WebChat). Use a plugin interface: `registerChannel({ send, receive, metadata })`.

**Security & Safety:**
- Require DM pairing codes for unknown remote clients; enforce per-channel allowlists.
- Default to local-only binding; require explicit opt-in to expose on the public network.
- TLS for remote gateways; JWT for client tokens.

**Tests / Success Metrics:**
- Gateway accepts connections and authenticates within 250ms.
- Connection loss & reconnection handled without state corruption.

**Priority/Phase:** Phase 1 (Week 1) — Gateway enhancements and security hardening (Phase 7) later.

---

## 2) Two‑Layer Memory System (Daily stream + Deep store)

**What:** Implement the Two-Layer Memory: fast daily stream (human-readable markdown files) + deep semantic store (vector DB + BM25). Automatic compaction moves important facts into deep store.

**How (implementation):**
- **Daily Stream:** folder `memory/daily/YYYY-MM-DD.md` with structured frontmatter and short entries. Provide CLI to append (`jarvis memory note "..." --tags`) and auto-extract named entities.
- **Deep Store (MEMORY):** single `MEMORY.md` (human readable) + JSONL & vector DB for retrieval. On compaction, append canonicalized entries to MEMORY.md and index them in vector DB.
- **Embeddings:** `sentence-transformers` local or `onnx`-based model; compute embedding when entry is created or when compaction pulls it in.
- **Vector DB:** FAISS for local indexes; persist vectors to disk and checkpoint regularly.
- **BM25 fallback:** use a local BM25 implementation (Whoosh or Lunr-like library) for keyword queries and fast filtering.
- **Metadata:** store timestamps, source (channel/skill), confidence, tags, and ownership flags.

**Compaction rules:**
- Age threshold: daily logs older than N days are candidates.
- Importance heuristics: frequency, assigned `important:true` flag, long-term tags (e.g., `project/finance`), user-pinned items.
- Auto summarization: use an LLM step to reduce a 2k-word daily thread to a 2–4 sentence canonical memory.
- Human review queue: compaction can be automatic or require approval (HITL) depending on privacy settings.

**Tests / Success Metrics:**
- Retrieval relevance: P@5 > 0.8 on sample queries.
- Compaction compresses daily stream by >70% while preserving recall for prioritized facts.

**Priority/Phase:** Phase 1 Week 4 + ongoing compaction work across Phases 2–6.

---

## 3) Vector Search + BM25 Hybrid Retrieval

**What:** Fast semantic search (vectors) supplemented by BM25 keyword search; combine results with hybrid scoring.

**How (implementation):**
- Vector index (FAISS) for semantic similarity.
- BM25 index (Whoosh) for exact keyword signals.
- Query flow: generate query embedding → get top-k vectors; do BM25 query → merge sorted lists with tunable weights (e.g., 0.7 vector + 0.3 BM25).
- Retrieval cache for popular queries and answers.

**Performance:**
- Periodic reindexing; incremental indexing for new memory.
- Sharding for large stores (by year or user namespace).

**Tests / Success Metrics:**
- Latency <150ms for local queries (cold) and <50ms warm.
- Ablation tests to choose weight blend that maximizes recall.

**Priority/Phase:** Phase 1–2 (Week 4 + Week 12 enhancements).

---

## 4) Compaction & Context Management (infinite context support)

**What:** Automatically compress active conversation context into a compact memory artifact and keep the model prompt limited.

**How (implementation):**
- Maintain a context manager per session. When token budget reaches threshold, call `summarizeContext(sessionId, window)` -> produce “context-summary” used as a compact context prompt.
- Versioned summaries: keep last N summaries indexed for retrieval.
- Compaction pipeline: `rawMessages -> candidate facts -> embed -> rank -> summarize -> store in daily + deep memory`.

**Algorithm specifics:**
1. Identify named entities and actions with lightweight NER.
2. Score messages by novelty (embedding distance to deep memory), frequency, and explicit user flags.
3. For high-score items, create compact bullet entries to inject back into prompt.

**Safety:**
- Respect `do-not-store` markers (user privacy), and provide per-channel defaults.

**Priority/Phase:** Phase 1 Week 4, with refinements during Phase 4.

---

## 5) Skills & Tool System (explicit tool registry + allowlist)

**What:** Extend skill loader to support safety descriptions, permission manifests, and runtime sandboxing.

**How (implementation):**
- Skill manifest (`skill.json`) with fields: `id`, `name`, `description`, `permissions` (files, network, shell), `entrypoint`, `exits`.
- At load time, verify manifest and prompt user for permission requests.
- Runtime: spawn skills in isolated worker processes (or containers) with IPC to Gateway, limiting accessible primitives.
- Tool registry: central directory of callable endpoints, versioned.

**Security:**
- Denylist and allowlist enforcement in Gateway. Skills requesting shell access must be explicitly approved.
- Skill sandboxing with process-level resource limits.

**Tests / Success Metrics:**
- Time to safely load a skill < 100ms (metadata); execution sandbox prevents file access outside allowed scope.

**Priority/Phase:** Phase 1 Week 3, Phase 5 for MCP compatibility.

---

## 6) Lobster Shell (CLI + Automation Shell)

**What:** `lobster` — a thin, predictable shell for agentic automation (inspired by Moltbot’s CLI). Users can script complex flows with lobster syntax.

**How (implementation):**
- Implement a REPL CLI with structured commands (JS/TS AST-like). Commands map to skill calls and can be piped.
- Example: `lobster> search web "best small AC" | summarize --length 3 | email --to me@example.com`
- Add dry-run and sandbox modes.

**Security:**
- `lobster config` stores allowlists; `lobster run --confirm` for any operation that writes files or sends messages.

**Priority/Phase:** Phase 1–3 (provide developer tooling early).

---

## 7) Multiple-Agent Management & Isolation

**What:** Allow multiple agents with different SOULs, permissions, and dedicated sessions (multi-agent swarms).

**How (implementation):**
- Agents are first-class objects: `{id, soul, capabilities, allowlist, sessionPolicy}`.
- Multi-agent orchestration where a parent orchestrator can spawn sub-agents for tasks (e.g., a ResearchAgent + ExecutorAgent). Use lightweight workers or containers for isolation.
- Agent communication channel internal to Gateway with ACLs.

**Monitoring & Audit:**
- Per-agent logs, quotas, and kill-switch.
- Supervisor to detect infinite loops and resource abuse.

**Priority/Phase:** Phase 5 (weeks 17–20) but provide primitives earlier (agent metadata and session separation).

---

## 8) Job Processing, Async Workflows & Scheduler

**What:** Robust job queue for background tasks (async workflows), scheduling, and notifications.

**How (implementation):**
- Use Redis + BullMQ (or local SQLite queue for single-user) for job persistence and retries.
- Jobs have metadata: required agent, priority, channel, estimated cost, steps.
- Workflow engine breaks tasks into steps (planner), each step is a job. Steps can be sequential/parallel with rollback strategies.
- Scheduler: cron-like job runner (node-cron) and a calendar-driven scheduler integrated with Google Calendar.

**Human-in-the-loop:**
- Jobs can be gated with approval tokens. Gateway will pause and notify user for confirmation.

**Priority/Phase:** Phase 4 Week 14 (Task Planning & Async Workflows).

---

## 9) Human‑In‑The‑Loop (HITL) & Safety Overrides

**What:** When actions have risk (file deletion, money transfer), require user confirmation or provide an approval flow.

**How (implementation):**
- Mark skill/tool actions with `risk_level` in manifest.
- For `risk_level: high`, create a short-form approval prompt and send to paired channels (push, Telegram, WebChat). The job pauses until approved.
- Use signed approval tokens to prevent replay attacks.

**Auditability:**
- All approvals logged; ability to rollback where possible.

**Priority/Phase:** Phase 2–4 (integrate with channels and job queue).

---

## 10) Executing Commands & File Management

**What:** Controlled shell execution and file-system tools (read, write, edit, diff).

**How (implementation):**
- Implement a `shell` skill that exposes controlled commands: sandboxed chroot (or container) with resource limits and an allowlist of executable binaries.
- File operations must pass through a File API: `read(path)`, `write(path, content, opts)`, `list(dir)`, `stat(path)`.
- File manager skill includes search, watch, and hash-based dedup.

**Tests / Safety:**
- Prevent arbitrary `rm -rf /`. Implement path normalization and allowlist.
- Use dry-run and explicit confirmations for destructive ops.

**Priority/Phase:** Phase 3 Week 9 and ongoing.

---

## 11) Browser Control & Web Automation

**What:** Playwright-based browser automation skill that can navigate, click, fill forms, and extract pages.

**How (implementation):**
- Skill APIs: `navigate(url)`, `screenshot(selector?)`, `fill(selector, value)`, `click(selector)`, `extract(selector)`, `run-script(js)`.
- Profiles: headless for server tasks, headed for local debug or display on Jarvis screen.
- Sandboxing: run pages in ephemeral contexts; rate-limit and throttle.

**Priority/Phase:** Phase 3 Week 9 (high).

---

## 12) Gateway → Jarvis Screen / UI Display Protocol

**What:** A lightweight UI protocol so Gateway can instruct the local Jarvis screen to display cards, toasts, or full pages.

**How (implementation):**
- Message types: `display/card`, `display/tiles`, `display/fullscreen`, `input/request`.
- Use a small templating format (JSON + markdown) to render content.
- Optional WebSocket direct connection from Gateway to a local Electron app for secure local rendering.

**Priority/Phase:** Phase 2 Week 7 + Phase 6 Week 24 (Desktop App).

---

## 13) User Profile (USER.md) & SOUL.md schema

**What:** Formalize user profile schema and personality file so agents can programmatically read/write user facts.

**How (implementation):**
- `USER.md` frontmatter schema: `{id, name, timezone, locale, preferences: {language, code_style, short_answers}, contacts: [...], devices: [...]}`.
- `SOUL.md` fields define persona and assistant constraints: tone, policy (no shipping keys), forbidden actions.
- CRUD API (`jarvis user set/get/delete`) and permissioned edits.

**Priority/Phase:** Phase 1 Week 4.

---

## 14) Privacy, Local‑First Operation & Optional Remote Access

**What:** Default local-only behavior with optional encrypted remote access.

**How (implementation):**
- Default store data locally in `~/.jarvis/`. Provide `export` and `delete` commands.
- Optional remote access via Tailscale or SSH tunnels; when enabled, require device registration and identity headers.
- Encryption-at-rest: optional passphrase-based encryption for memory files using libsodium.

**Privacy UI:**
- Settings page to view what’s stored, export, and redact.

**Priority/Phase:** Phase 1 (design) + Phase 7 (hardening).

---

## 15) Autonomous Agents & Self‑Healing

**What:** Autonomous loops for retrying failed jobs, self-diagnostics, and repair actions.

**How (implementation):**
- Supervisor detects failed jobs and triggers a `diagnose` skill that runs tests, collects logs, and attempts fix strategies (restart services, roll back changes).
- Budgeting: set resource and API quotas for autonomous actions; require high-level opt-in for money/costly network ops.
- Kill-switch: global emergency stop available via CLI and paired device.

**Priority/Phase:** Phase 4–5.

---

## 16) Infinite Context Techniques & Prompt Management

**What:** Techniques to effectively present an “infinite” memory to LLMs without exceeding token limits.

**How (implementation):**
- Context manager pulls only relevant memory (hybrid retrieval) and appends compacted summaries to the prompt.
- Implement speculative prefetch of background facts for long-running tasks.
- Use MCP-style tool calls for offloading sub-steps to a planner or tool instead of stuffing prompt with everything.

**Priority/Phase:** Phase 1–4.

---

## 17) Testing, Auditing & Observability for Agentic Actions

**What:** Monitoring and logs that make every agented action auditable.

**How (implementation):**
- Structured logs (JSON) with trace IDs for each job step.
- Action replay: ability to replay the exact sequence of tool calls in a sandbox.
- Alerts & dashboards: Prometheus metrics served by Gateway; Grafana dashboards.

**Priority/Phase:** Phase 7 (Weeks 25–28).

---

## 18) Integration: Social Channels & Remote Control

**What:** Connect socials (Discord, WhatsApp, Telegram) and allow remote control (paired devices). Provide rich message formatting and control flows.

**How (implementation):**
- Each channel adapter maps channel messages to Gateway events. Include rate limiting and message size checks.
- For remote control: pairing codes per-device, per-channel allowlists, per-skill permission steps.

**Priority/Phase:** Phase 2 (Weeks 5–8).

---

## Implementation Checklist (short)

1. Gateway security & versioned messaging (Week 1)
2. Daily stream + MEMORY + compaction pipeline (Week 4)
3. Vector + BM25 hybrid indexes (Week 4–6)
4. Skill manifests + sandboxing (Week 3)
5. Lobster shell CLI with dry-run (Week 2–4)
6. Job queue + workflow engine + HITL gates (Week 14)
7. Browser Playwright skill (Week 9)
8. Screen display protocol + Electron app (Week 24)
9. Multi-agent isolation + supervisor (Phase 5)
10. Privacy defaults & encryption options (Phase 1/7)

---

## Acceptance criteria — what "done" looks like

- Jarvis Gateway runs locally and accepts authenticated client connections.
- Core memory system writes daily logs and returns high-quality retrievals (vector+BM25 hybrid).
- Skill system supports manifests, enforces permissions, and runs skills in isolated workers.
- Job queue reliably executes background workflows with HITL approval and clear audit logs.
- Browser automation skill can navigate, screenshot and extract pages safely.
- Local-first defaults and secure remote access options are present with user controls.
- Desktop UI can render basic cards and respond to input requests.

---

## Next steps — immediate developer actions

1. Add `memory/daily` support and CLI `jarvis memory` commands (append, list, search).
2. Wire Gateway handshake and session tokens; implement local-only default.
3. Add a minimal skill with manifest to exercise the skill loader and sandbox.
4. Stand up local FAISS + Whoosh proof-of-concept and index 100 test memory items.
5. Implement a small `lobster` REPL that calls one skill and prints the result.

---

## Notes on adoption & evolution

- Start with conservative defaults (local only, manual compaction), then gradually enable automation.
- Expose advanced features behind clear toggles so users can opt-in.
- Document privacy decisions in the UI (what is stored, where, and how to remove it).

---

*If you want, I will now merge this content into your existing RoadMap.md file and create the updated version in the project folder. Tell me to proceed and I will create the file named `RoadMap-Integrated-Moltbot.md` in the repo.*

