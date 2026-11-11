#!/usr/bin/env python3
"""Incrementally sync new community cases and styles from upstream GitHub repos into pure-code-video."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent


def sync_from_dirs(opus_dir: Path | None, lemo_dir: Path | None) -> int:
    core_path = ROOT / "recipes/core-styles.json"
    comm_path = ROOT / "recipes/community-cases.json"
    idx_path = ROOT / "index.html"

    core_styles = json.loads(core_path.read_text(encoding="utf-8"))
    comm_cases = json.loads(comm_path.read_text(encoding="utf-8"))
    existing_core_ids = {x["id"] for x in core_styles}
    existing_comm_ids = {x["id"] for x in comm_cases}
    added = 0

    # Validate the gallery boundaries before copying assets or changing catalogs.
    html = idx_path.read_text(encoding="utf-8")
    s1 = html.find("const CORE_STYLES = ")
    s2 = html.find(";\nconst COMMUNITY_CASES = ", max(s1, 0))
    e2 = html.find(";\n\nconst SFX_ITEMS = ", max(s2, 0))
    if not (0 <= s1 < s2 < e2):
        raise ValueError("index.html is missing the expected style/case data boundaries")

    if lemo_dir and (lemo_dir / "styles").is_dir():
        cat_map = {
            "剪辑与纪实": "商业数据 / 纪实调查",
            "实证影像": "商业数据 / 纪实调查",
            "手绘与绘画": "手绘与绘画",
            "东方传统": "东方与古典艺术",
            "印刷与版画": "拼贴与版画",
            "图形与排版": "图形与排版",
            "信息与发布": "产品发布 / 高能快剪",
            "卡通与动画": "科普图解 / 手绘水彩",
            "游戏": "极客 / 像素 / 复古",
            "电影与时代": "极客 / 像素 / 复古",
            "材质与 3D": "3D 与等距",
        }
        for sj in sorted((lemo_dir / "styles").glob("*/style.json")):
            if sj.parent.name.startswith("_"):
                continue
            meta = json.loads(sj.read_text(encoding="utf-8"))
            slug = meta["slug"]
            sid = f"opuscar-{slug}"
            if sid in existing_core_ids:
                continue
            poster = sj.parent / "poster.jpg"
            style_md = sj.parent / "STYLE.md"
            if not poster.exists():
                continue
            dst_jpg = ROOT / "assets/lemo" / f"{slug}.jpg"
            dst_jpg.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(poster, dst_jpg)
            md_txt = style_md.read_text(encoding="utf-8", errors="ignore")[:1200].strip() if style_md.exists() else meta.get("line_cn", "")
            core_styles.append({
                "id": sid,
                "title_zh": f"{meta['cn']} ({meta['en']})",
                "title_en": meta["en"],
                "library": "Lemo-Opuscar 代码电影库",
                "category": cat_map.get(meta.get("category_cn", ""), "图形与排版"),
                "media_type": "image",
                "media_url": f"./assets/lemo/{slug}.jpg",
                "poster_url": f"./assets/lemo/{slug}.jpg",
                "desc": f"【{meta.get('category_cn','')} · 样片《{meta.get('film','')}》】{meta.get('line_cn','')}",
                "recipe": f"适用场景：{', '.join(meta.get('uses', []))}\n\n{md_txt}",
                "source_ref": f"lemomo-ai/lemo-opuscar/styles/{slug}/STYLE.md",
                "tags": ["Lemo-Opuscar", meta.get("category_cn", ""), slug] + meta.get("uses", [])[:2],
            })
            existing_core_ids.add(sid)
            added += 1

    if opus_dir and (opus_dir / "data/cases.json").is_file():
        opus_data = json.loads((opus_dir / "data/cases.json").read_text(encoding="utf-8"))
        opus_style_map = {s["id"]: s for s in opus_data.get("styles", [])}
        for c in opus_data.get("cases", []):
            cid = str(c["id"])
            full_id = f"opus55-{cid}"
            if full_id in existing_comm_ids:
                continue
            still = opus_dir / "assets/stills" / f"{cid}.jpg"
            rel_still = ""
            if still.exists():
                dst_still = ROOT / "assets/community" / f"{cid}.jpg"
                dst_still.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(still, dst_still)
                rel_still = f"./assets/community/{cid}.jpg"
            st_info = opus_style_map.get(c["style"], {"zh": c["style"], "recipe": ""})
            comm_cases.append({
                "id": full_id,
                "case_id": cid,
                "title_zh": c.get("title_zh") or c.get("title_en") or cid,
                "title_en": c.get("title_en", ""),
                "style_id": c["style"],
                "style_zh": st_info["zh"],
                "recipe": st_info.get("recipe", ""),
                "author": c.get("author", ""),
                "likes": c.get("likes_2026_09_29", 0),
                "post_url": c.get("post_url", ""),
                "media_url": rel_still,
                "prompt": c.get("prompt", ""),
            })
            existing_comm_ids.add(full_id)
            added += 1

    if added > 0:
        core_path.write_text(json.dumps(core_styles, ensure_ascii=False, indent=2), encoding="utf-8")
        comm_path.write_text(json.dumps(comm_cases, ensure_ascii=False, indent=2), encoding="utf-8")
        html = (
            html[:s1]
            + "const CORE_STYLES = "
            + json.dumps(core_styles, ensure_ascii=False)
            + ";\nconst COMMUNITY_CASES = "
            + json.dumps(comm_cases, ensure_ascii=False)
            + html[e2:]
        )
        idx_path.write_text(html, encoding="utf-8")
    print(f"Sync complete: {added} new styles/cases added (core={len(core_styles)}, community={len(comm_cases)}).")
    return added


def main():
    ap = argparse.ArgumentParser(description="增量同步上游社区新增纯代码视频风格与案例")
    ap.add_argument("--opus-dir", type=Path, help="awesome-opus-5-5-video-styles 目录")
    ap.add_argument("--lemo-dir", type=Path, help="lemo-opuscar 目录")
    args = ap.parse_args()
    sync_from_dirs(args.opus_dir, args.lemo_dir)


if __name__ == "__main__":
    main()
