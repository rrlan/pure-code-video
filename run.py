#!/usr/bin/env python3
"""Run pure-code-video CLI commands (doctor, search, recipe, gallery)."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    cmd = [sys.executable, str(ROOT / "scripts/codevid.py"), *(sys.argv[1:] or ["doctor"])]
    raise SystemExit(subprocess.run(cmd).returncode)
