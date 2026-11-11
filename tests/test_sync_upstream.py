"""Offline regression tests for the incremental upstream sync."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import sync_upstream


class SyncUpstreamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.opus = self.base / "opus"
        self.lemo = self.base / "lemo"
        self.core = [{"id": "existing-core", "title_zh": "已有风格"}]
        self.cases = [{"id": "opus55-existing", "title_zh": "已有案例"}]
        self.write_json(self.root / "recipes/core-styles.json", self.core)
        self.write_json(self.root / "recipes/community-cases.json", self.cases)
        self.prefix = "<!doctype html>\n<script>\n"
        self.suffix = ';\n\nconst SFX_ITEMS = [{"id":"keep-sound"}];\n</script>\n'
        self.html = (
            self.prefix
            + "const CORE_STYLES = " + json.dumps(self.core)
            + ";\nconst COMMUNITY_CASES = " + json.dumps(self.cases)
            + self.suffix
        )
        (self.root / "index.html").write_text(self.html, encoding="utf-8")
        root_patch = patch.object(sync_upstream, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    @staticmethod
    def write_json(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def add_style(self, folder="watercolor", slug="watercolor", poster=True):
        style = self.lemo / "styles" / folder
        self.write_json(style / "style.json", {
            "slug": slug, "cn": "水彩", "en": "Watercolor",
            "category_cn": "手绘与绘画", "uses": ["科普", "故事"],
            "line_cn": "手绘风格", "film": "样片",
        })
        (style / "STYLE.md").write_text("# 水彩\n配方内容", encoding="utf-8")
        if poster:
            (style / "poster.jpg").write_bytes(b"poster-fixture")

    def add_cases(self, cases=None, still=True):
        self.write_json(self.opus / "data/cases.json", {
            "styles": [{"id": "watercolor", "zh": "水彩", "recipe": "配方"}],
            "cases": cases if cases is not None else [
                {"id": "new", "style": "watercolor", "title_zh": "新增案例"},
                {"id": "existing", "style": "watercolor"},
            ],
        })
        if still:
            target = self.opus / "assets/stills/new.jpg"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"still-fixture")

    def snapshot(self):
        return {
            str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in self.root.rglob("*") if p.is_file()
        }

    def read_catalogs(self):
        return tuple(
            json.loads((self.root / "recipes" / name).read_text(encoding="utf-8"))
            for name in ("core-styles.json", "community-cases.json")
        )

    def test_adds_both_sources_and_keeps_gallery_in_sync(self):
        self.add_style()
        self.add_cases()
        self.assertEqual(sync_upstream.sync_from_dirs(self.opus, self.lemo), 2)
        core, cases = self.read_catalogs()
        self.assertEqual(core[0], self.core[0])
        self.assertEqual(cases[0], self.cases[0])
        self.assertEqual(core[1]["id"], "opuscar-watercolor")
        self.assertIn("# 水彩\n配方内容", core[1]["recipe"])
        self.assertEqual(cases[1]["id"], "opus55-new")
        self.assertEqual(cases[1]["recipe"], "配方")
        self.assertEqual(cases[1]["media_url"], "./assets/community/new.jpg")
        self.assertEqual((self.root / "assets/lemo/watercolor.jpg").read_bytes(), b"poster-fixture")
        self.assertEqual((self.root / "assets/community/new.jpg").read_bytes(), b"still-fixture")
        html = (self.root / "index.html").read_text(encoding="utf-8")
        expected = (
            self.prefix + "const CORE_STYLES = " + json.dumps(core, ensure_ascii=False)
            + ";\nconst COMMUNITY_CASES = " + json.dumps(cases, ensure_ascii=False)
            + self.suffix
        )
        self.assertEqual(html, expected)

    def test_repeated_sync_does_not_rewrite_or_duplicate_any_files(self):
        self.add_style()
        self.add_cases()
        sync_upstream.sync_from_dirs(self.opus, self.lemo)
        before = self.snapshot()
        self.assertEqual(sync_upstream.sync_from_dirs(self.opus, self.lemo), 0)
        self.assertEqual(self.snapshot(), before)

    def test_no_sources_leaves_repository_unchanged(self):
        before = self.snapshot()
        self.assertEqual(sync_upstream.sync_from_dirs(None, None), 0)
        self.assertEqual(self.snapshot(), before)

    def test_skips_hidden_styles_missing_posters_and_duplicate_ids(self):
        self.add_style(folder="_template", slug="template")
        self.add_style(folder="no-poster", slug="no-poster", poster=False)
        self.add_style(folder="watercolor-a")
        self.add_style(folder="watercolor-b")
        case = {"id": "new", "style": "watercolor"}
        self.add_cases(cases=[case, case])
        self.assertEqual(sync_upstream.sync_from_dirs(self.opus, self.lemo), 2)
        core, cases = self.read_catalogs()
        self.assertEqual(len(core), 2)
        self.assertEqual(len(cases), 2)
        self.assertEqual(len(list((self.root / "assets/lemo").glob("*.jpg"))), 1)

    def test_case_without_still_or_known_style_uses_fallbacks(self):
        self.add_cases(cases=[{"id": "new", "style": "unknown", "title_en": "New case"}], still=False)
        self.assertEqual(sync_upstream.sync_from_dirs(self.opus, None), 1)
        _, cases = self.read_catalogs()
        self.assertEqual(cases[1]["media_url"], "")
        self.assertEqual(cases[1]["title_zh"], "New case")
        self.assertEqual(cases[1]["style_zh"], "unknown")
        self.assertEqual(cases[1]["recipe"], "")

    def test_invalid_gallery_boundaries_fail_before_any_file_changes(self):
        self.add_style()
        self.add_cases()
        for name in ("CORE_STYLES", "COMMUNITY_CASES", "SFX_ITEMS"):
            with self.subTest(missing=name):
                (self.root / "index.html").write_text(self.html.replace(name, "MISSING"), encoding="utf-8")
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, "data boundaries"):
                    sync_upstream.sync_from_dirs(self.opus, self.lemo)
                self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
