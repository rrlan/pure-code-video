"""Prepare a reusable Python environment outside the replaceable Skill directory."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile


def skill_name(root: Path) -> str:
    match = re.search(
        r"^name:\s*([a-z0-9][a-z0-9-]*)\s*$",
        (Path(root) / "SKILL.md").read_text(encoding="utf-8"),
        re.M,
    )
    if not match:
        raise RuntimeError("SKILL.md 缺少有效 name")
    return match.group(1)


def python_at(directory: Path) -> Path:
    return directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def environment_ok(python: Path) -> bool:
    if not python.is_file():
        return False
    code = "import numpy, scipy, soundfile, librosa, matplotlib"
    return (
        subprocess.run(
            [str(python), "-c", code],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def ensure_runtime(root: Path) -> Path:
    root = Path(root).resolve()
    if sys.version_info < (3, 9):
        raise RuntimeError("需要 Python 3.9 或更新版本")
    # If current interpreter already has librosa/soundfile/scipy/matplotlib, reuse it directly
    if environment_ok(Path(sys.executable)):
        return Path(sys.executable)
    requirements = root / "requirements.txt"
    key_input = requirements.read_bytes() + repr(
        (
            sys.version_info[:3],
            getattr(sys, "_base_executable", sys.executable),
            platform.system(),
            platform.machine(),
        )
    ).encode()
    key = hashlib.sha256(key_input).hexdigest()[:24]
    cache = Path(
        os.environ.get("SKILL_RUNTIME_HOME", str(Path.home() / ".cache/rrlan-skill-runtimes"))
    ).expanduser()
    base = cache / skill_name(root)
    base.mkdir(parents=True, exist_ok=True)
    pointer = base / (key + ".json")
    if pointer.is_file():
        try:
            directory = Path(json.loads(pointer.read_text())["directory"])
            if directory.parent == base.resolve() and environment_ok(python_at(directory)):
                return python_at(directory)
        except (OSError, ValueError, KeyError):
            pass
    directory = Path(tempfile.mkdtemp(prefix=key + "-", dir=base)).resolve()
    python = python_at(directory)
    print("正在自动准备音效分析与混音 Python 依赖环境 (librosa/soundfile/scipy/matplotlib)…", flush=True)
    try:
        subprocess.run([sys.executable, "-m", "venv", str(directory)], check=True)
        subprocess.run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(requirements)],
            check=True,
        )
        if not environment_ok(python):
            raise RuntimeError("音效依赖安装后导入检查未通过")
        fd, filename = tempfile.mkstemp(prefix=key, suffix=".tmp", dir=base)
        with os.fdopen(fd, "w") as stream:
            json.dump({"directory": str(directory), "dependency_key": key}, stream)
        os.replace(filename, pointer)
    except BaseException:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    return python
