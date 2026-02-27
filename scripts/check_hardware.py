#!/usr/bin/env python3
"""
JARVIS Hardware Profiler
Detects RAM, CPU, GPU and recommends the appropriate loop tier.
Run: python scripts/check_hardware.py
"""

import platform
import shutil
import subprocess
import sys

# ── Optional imports ──────────────────────────────────────────────────────────
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# ── Helpers ───────────────────────────────────────────────────────────────────

def gb(bytes_: int) -> float:
    return round(bytes_ / (1024 ** 3), 1)


def check_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def get_gpu_info() -> dict:
    info: dict = {"available": False, "name": None, "vram_gb": None}

    # nvidia-smi
    if check_command("nvidia-smi"):
        try:
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total",
                 "--format=csv,noheader,nounits"],
                text=True, timeout=5
            ).strip()
            if out:
                parts = out.split(",")
                info["available"] = True
                info["name"] = parts[0].strip()
                info["vram_gb"] = round(int(parts[1].strip()) / 1024, 1)
        except Exception:
            pass

    # Apple Silicon — unified memory, treat as GPU
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        info["available"] = True
        info["name"] = "Apple Silicon (unified memory)"

    return info


def recommend_tier(ram_gb: float, gpu: dict) -> tuple[str, str]:
    """Returns (tier_name, reason)."""
    if ram_gb < 8:
        return "ECHO", "Less than 8 GB RAM — ECHO only (minimum supported)"
    if ram_gb < 16 and not gpu["available"]:
        return "ECHO", "8–16 GB RAM, no GPU — ECHO recommended for best performance"
    if ram_gb >= 16 and not gpu["available"]:
        return "ATLAS", "16+ GB RAM, no GPU — ATLAS available"
    if gpu["available"] and (gpu.get("vram_gb") or 0) >= 8:
        return "NEXUS", f"GPU detected ({gpu['name']}) — NEXUS available"
    if gpu["available"]:
        return "ATLAS", f"GPU detected ({gpu['name']}) but limited VRAM — ATLAS recommended"
    return "ECHO", "Fallback recommendation"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║            JARVIS Hardware Check                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # ── System ──────────────────────────────────────────────────────────────
    print(f"  OS        : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  Python    : {sys.version.split()[0]}")

    # ── RAM ─────────────────────────────────────────────────────────────────
    if HAS_PSUTIL:
        ram = psutil.virtual_memory()
        ram_total = gb(ram.total)
        ram_avail = gb(ram.available)
        print(f"  RAM       : {ram_total} GB total  ({ram_avail} GB available)")
    else:
        print("  RAM       : psutil not installed — run setup_python_envs.sh first")
        ram_total = 0.0

    # ── CPU ─────────────────────────────────────────────────────────────────
    if HAS_PSUTIL:
        cpu_count = psutil.cpu_count(logical=False)
        cpu_logical = psutil.cpu_count(logical=True)
        print(f"  CPU       : {cpu_count} physical cores, {cpu_logical} logical")

    # ── GPU ─────────────────────────────────────────────────────────────────
    gpu = get_gpu_info()
    if gpu["available"]:
        vram_str = f" ({gpu['vram_gb']} GB VRAM)" if gpu["vram_gb"] else ""
        print(f"  GPU       : ✅  {gpu['name']}{vram_str}")
    else:
        print("  GPU       : ❌  Not detected — CPU-only mode")

    # ── Dependencies ────────────────────────────────────────────────────────
    print()
    print("  ── Tooling ──────────────────────────────────────────────")
    for tool in ["ollama", "node", "pnpm", "python", "git"]:
        found = "✅" if check_command(tool) else "❌ MISSING"
        print(f"  {tool:<14}: {found}")

    # ── Recommendation ──────────────────────────────────────────────────────
    print()
    print("  ── Loop Tier Recommendation ─────────────────────────────")

    tier, reason = recommend_tier(ram_total, gpu)
    tier_colors = {
        "ECHO":   "⚡",
        "ATLAS":  "🔵",
        "NEXUS":  "🟣",
        "QUANTUM":"🌀",
    }
    icon = tier_colors.get(tier, "✅")
    print(f"  {icon}  Recommended tier: {tier}")
    print(f"     Reason: {reason}")
    print()
    print(f"  Set in jarvis.config.yaml:")
    print(f"    loops:")
    print(f"      default_tier: \"{tier.lower()}\"")
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Hardware check complete.                                ║")
    print("║  Next: cp .env.example .env  (then edit .env)            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    main()