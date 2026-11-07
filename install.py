#!/usr/bin/env python3
"""Local install/update helper; delegates Skill placement to skills@1.7.2."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def skill_name(root: Path) -> str:
    match = re.search(
        r"^name:\s*([a-z0-9][a-z0-9-]*)\s*$",
        (root / "SKILL.md").read_text(encoding="utf-8"),
        re.M,
    )
    if not match:
        raise RuntimeError("SKILL.md 缺少有效 name")
    return match.group(1)


def main():
    parser = argparse.ArgumentParser(description="自动安装 pure-code-video Skill 并执行自检。默认 Codex 个人范围。")
    parser.add_argument("--project", type=Path, help="改为项目范围，指定项目目录")
    parser.add_argument("--setup-only", action="store_true", help="仅运行当前 Skill 自检，不复制 Skill")
    parser.add_argument("--update", action="store_true", help="更新已登记的在线来源并检查")
    parser.add_argument("--with-api", action="store_true", help="兼容统一安装器参数（本 Skill 零外部生图 API）")
    args = parser.parse_args()
    if args.setup_only and args.update:
        parser.error("--setup-only 和 --update 不能同时使用")
    name = skill_name(ROOT)
    if args.setup_only:
        subprocess.run([sys.executable, str(ROOT / "run.py"), "doctor"], check=True)
        print("自检通过。")
        return
    npx = shutil.which("npx.cmd" if os.name == "nt" else "npx")
    if not npx:
        raise RuntimeError("未找到 Node.js/npm（npx）。请先安装 Node.js，再重试本命令。")
    scope = args.project.expanduser().resolve() if args.project else Path.home()
    scope.mkdir(parents=True, exist_ok=True)
    target = scope / ".agents/skills" / name
    if target.is_symlink():
        raise RuntimeError("目标是现有软链接，请先按现有管理方式处理；不会自动接管。")
    env = dict(os.environ, DISABLE_TELEMETRY="1")
    with tempfile.TemporaryDirectory(prefix="skill-install-") as temp:
        temp = Path(temp)
        source = temp / name
        shutil.copytree(
            ROOT,
            source,
            ignore=shutil.ignore_patterns(
                ".git", ".venv", "__pycache__", "*.pyc", ".pytest_cache", ".env", ".env.*", "assets"
            ),
        )
        if not args.update:
            subprocess.run([sys.executable, str(source / "run.py"), "doctor"], check=True)
        if args.project:
            lock = scope / "skills-lock.json"
        elif os.environ.get("XDG_STATE_HOME"):
            lock = Path(os.environ["XDG_STATE_HOME"]) / "skills/.skill-lock.json"
        else:
            lock = scope / ".agents/.skill-lock.json"
        if args.update:
            if not lock.is_file():
                raise RuntimeError("没有在线安装来源记录；收包用户请运行新版包的 install.py。")
            entry = json.loads(lock.read_text()).get("skills", {}).get(name, {})
            if entry.get("sourceType") not in ("github", "git", "gitlab"):
                raise RuntimeError("当前不是受支持的在线来源；请用新版安装包更新。")
        old_lock = lock.read_bytes() if lock.is_file() else None
        backup = temp / "previous"
        if target.exists():
            shutil.copytree(target, backup, symlinks=True)
        cmd = [npx, "--yes", "skills@1.7.2"]
        if args.update:
            cmd += ["update", name, "-p" if args.project else "-g", "-y"]
        else:
            cmd += ["add", str(source), "--skill", name, "--agent", "codex", "--copy", "-y"]
            if not args.project:
                cmd.append("-g")
        try:
            subprocess.run(cmd, cwd=scope, env=env, check=True)
            if not (target / "SKILL.md").is_file():
                raise RuntimeError("安装后未找到目标 Skill")
            subprocess.run([sys.executable, str(target / "run.py"), "doctor"], check=True)
        except BaseException:
            if target.exists():
                shutil.rmtree(target)
            if backup.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(backup, target, symlinks=True)
            if old_lock is None:
                lock.unlink(missing_ok=True)
            else:
                lock.parent.mkdir(parents=True, exist_ok=True)
                lock.write_bytes(old_lock)
            raise
    print("安装与自检完成：" + str(target))
    print('使用入口：python3 "' + str(target / "run.py") + '" doctor')


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("安装失败：" + str(error), file=sys.stderr)
        raise SystemExit(1)
