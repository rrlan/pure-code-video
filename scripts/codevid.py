#!/usr/bin/env python3
"""CLI entry for pure-code-video: doctor, search, recipe, sfx-list, sound-pass, gallery."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from skill_runtime import ensure_runtime

GALLERY_URL = "https://rrlan.github.io/pure-code-video/"


def load_catalog():
    core_p = ROOT / "recipes/core-styles.json"
    comm_p = ROOT / "recipes/community-cases.json"
    if not core_p.is_file() or not comm_p.is_file():
        raise RuntimeError("缺少 recipes 索引文件")
    core = json.loads(core_p.read_text(encoding="utf-8"))
    comm = json.loads(comm_p.read_text(encoding="utf-8"))
    return core, comm


def load_sfx_manifest():
    man_p = ROOT / "sfx/manifest.json"
    if not man_p.is_file():
        raise RuntimeError("缺少 sfx/manifest.json 音效清单")
    return json.loads(man_p.read_text(encoding="utf-8"))


def cmd_doctor(_args):
    core, comm = load_catalog()
    sfx_man = load_sfx_manifest()
    bundled_sfx = sfx_man.get("bundled", [])
    default_kit = sfx_man.get("default_kit", [])
    for entry in bundled_sfx:
        if not (ROOT / "sfx" / entry["file"]).is_file():
            raise RuntimeError(f"缺少内置 CC0 音效文件: sfx/{entry['file']}")
    he_tpl = ROOT / "templates/high-energy-html/render.mjs"
    hd_tpl = ROOT / "templates/handdrawn-explainer/handdrawn-leafcutter-21s.mjs"
    hd_lib = ROOT / "templates/handdrawn-explainer/lib/pen.mjs"
    sp_py = ROOT / "scripts/sound_pass.py"
    if not (he_tpl.is_file() and hd_tpl.is_file() and hd_lib.is_file() and sp_py.is_file()):
        raise RuntimeError("缺少核心渲染模板、手绘笔刷库或 sound_pass.py")
    info = {
        "status": "ok",
        "skill": "pure-code-video",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").is_file() else "1.1.0",
        "core_styles": len(core),
        "community_cases": len(comm),
        "total_recipes": len(core) + len(comm),
        "bundled_cc0_sfx": len(bundled_sfx),
        "default_sfx_kit": len(default_kit),
        "node": bool(shutil.which("node")),
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "gallery_url": GALLERY_URL,
    }
    print(json.dumps(info, ensure_ascii=False))
    return 0


def cmd_search(args):
    core, comm = load_catalog()
    q = args.query.strip().lower()
    hits = []
    for item in core:
        hay = f"{item['id']} {item['title_zh']} {item['title_en']} {item['category']} {item['desc']} {' '.join(item.get('tags', []))}".lower()
        if q in hay:
            hits.append({"type": "core", "id": item["id"], "title": item["title_zh"], "category": item["category"], "desc": item["desc"]})
    for item in comm:
        hay = f"{item['id']} {item['title_zh']} {item['title_en']} {item['style_zh']} {item.get('prompt', '')}".lower()
        if q in hay:
            hits.append({"type": "community", "id": item["id"], "title": item["title_zh"], "category": item["style_zh"], "desc": item["prompt"][:100]})
    print(json.dumps({"query": args.query, "count": len(hits), "results": hits[: args.limit]}, ensure_ascii=False, indent=2))
    return 0


def cmd_recipe(args):
    core, comm = load_catalog()
    target = args.style_id.strip().lower()
    for item in core:
        if item["id"].lower() == target or target in item["id"].lower():
            print(json.dumps(item, ensure_ascii=False, indent=2))
            return 0
    for item in comm:
        if item["id"].lower() == target or item.get("case_id", "").lower() == target:
            print(json.dumps(item, ensure_ascii=False, indent=2))
            return 0
    print(f"未找到风格 ID: {args.style_id}", file=sys.stderr)
    return 1


def cmd_sfx_list(args):
    man = load_sfx_manifest()
    bundled = man.get("bundled", [])
    if args.category:
        cat = args.category.strip().lower()
        bundled = [x for x in bundled if x.get("category", "").lower() == cat]
    out = {
        "default_kit": man.get("default_kit", []),
        "category_map": man.get("category_map", {}),
        "bundled_count": len(bundled),
        "bundled": bundled[: args.limit],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_sound_pass(args):
    python_bin = ensure_runtime(ROOT)
    manifest_path = str(ROOT / "sfx/manifest.json")
    forward = list(args.sound_pass_args)
    if "--manifest" not in forward:
        forward = ["--manifest", manifest_path, *forward]
    cmd = [str(python_bin), str(ROOT / "scripts/sound_pass.py"), *forward]
    return subprocess.run(cmd).returncode



def cmd_voice_trim(args):
    cmd = [sys.executable, str(ROOT / "scripts/voice_trim.py"), *args.voice_args]
    return subprocess.run(cmd).returncode


def cmd_voice_align(args):
    cmd = [sys.executable, str(ROOT / "scripts/timestamps_cpu.py"), *args.voice_args]
    return subprocess.run(cmd).returncode


def cmd_voice_clone(args):
    cmd = [sys.executable, str(ROOT / "scripts/tts_fishaudio.py"), *args.voice_args]
    return subprocess.run(cmd).returncode


def cmd_gallery(_args):
    local_html = ROOT / "index.html"
    target = local_html.as_uri() if local_html.is_file() else GALLERY_URL
    print("打开选片台:", target)
    webbrowser.open(target)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="pure-code-video 风格检索、音效库与混音工具")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor", help="检查 530 款风格配方、109 个 CC0 音效与渲染模板完整性")
    p_search = sub.add_parser("search", help="按关键词搜索风格或案例")
    p_search.add_argument("query", help="搜索词，如：水彩 / 3b1b / 像素 / 等轴")
    p_search.add_argument("--limit", type=int, default=15)
    p_recipe = sub.add_parser("recipe", help="按风格 ID 查看完整配方与 Prompt")
    p_recipe.add_argument("style_id", help="例如 claude-textured-editorial 或 mg-05-cel-boil")
    p_sfx = sub.add_parser("sfx-list", help="查看内置的 109 个 CC0 实录音效与默认音效包")
    p_sfx.add_argument("--category", help="按分类筛选，如 whoosh / click / pop / riser / impact / tick / glitch")
    p_sfx.add_argument("--limit", type=int, default=30)
    p_sp = sub.add_parser("sound-pass", help="运行节拍网格检测、CC0 音效挂载与 -16 LUFS 响度对齐混音")
    p_sp.add_argument("sound_pass_args", nargs=argparse.REMAINDER, help="透传给 sound_pass.py 的参数（自动附带 --manifest）")
    p_vt = sub.add_parser("voice-trim", help="真人录音预剪（自动剔除口水词、结巴重说与过长气口）")
    p_vt.add_argument("voice_args", nargs=argparse.REMAINDER)
    p_va = sub.add_parser("voice-align", help="将你自己的录音或克隆音频与文稿做本机 CPU 逐字时间戳对齐")
    p_va.add_argument("voice_args", nargs=argparse.REMAINDER)
    p_vc = sub.add_parser("voice-clone", help="使用自定义克隆音色 ID (Fish Audio) 按文稿合成你自己的声音与逐字时间戳")
    p_vc.add_argument("voice_args", nargs=argparse.REMAINDER)
    sub.add_parser("gallery", help="在浏览器中打开可视化选片台")
    args = parser.parse_args(argv)
    if args.cmd == "doctor":
        return cmd_doctor(args)
    if args.cmd == "search":
        return cmd_search(args)
    if args.cmd == "recipe":
        return cmd_recipe(args)
    if args.cmd == "sfx-list":
        return cmd_sfx_list(args)
    if args.cmd == "sound-pass":
        return cmd_sound_pass(args)
    if args.cmd == "voice-trim":
        return cmd_voice_trim(args)
    if args.cmd == "voice-align":
        return cmd_voice_align(args)
    if args.cmd == "voice-clone":
        return cmd_voice_clone(args)
    if args.cmd == "gallery":
        return cmd_gallery(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
