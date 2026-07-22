import json
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_pages
import generate_search_index
from front_matter import parse_inline_list, read_front_matter, split_front_matter


class FrontMatterTests(unittest.TestCase):
    def test_reads_bom_quotes_colon_and_inline_list(self):
        text = '\ufeff---\ntitle: "Linux: Basics"\ntags: ["linux", shell]\n---\n\nBody\n'
        front_matter, body = read_front_matter(text)

        self.assertEqual(front_matter["title"], "Linux: Basics")
        self.assertEqual(parse_inline_list(front_matter["tags"]), ["linux", "shell"])
        self.assertEqual(body, "Body\n")

    def test_returns_original_body_without_front_matter(self):
        lines, body = split_front_matter("Plain body")

        self.assertIsNone(lines)
        self.assertEqual(body, "Plain body")


class GeneratedPageSafetyTests(unittest.TestCase):
    def test_removes_only_marked_stale_category(self):
        with tempfile.TemporaryDirectory() as temporary:
            category_root = Path(temporary) / "category"
            manual = category_root / "manual"
            generated = category_root / "generated"
            manual.mkdir(parents=True)
            generated.mkdir()
            (manual / "index.md").write_text("---\ntitle: Manual\n---\n", encoding="utf-8")
            (generated / "index.md").write_text(
                f"---\n{generate_pages.generated_marker}\n---\n",
                encoding="utf-8",
            )

            original_category_dir = generate_pages.category_dir
            generate_pages.category_dir = str(category_root)
            try:
                generate_pages.remove_stale_category_dirs(set())
            finally:
                generate_pages.category_dir = original_category_dir

            self.assertTrue(manual.exists())
            self.assertFalse(generated.exists())

    def test_page_write_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "category" / "a" / "index.md"
            values = {"category": "a"}

            self.assertTrue(generate_pages.write_page(str(output), "category", "A", values))
            self.assertFalse(generate_pages.write_page(str(output), "category", "A", values))
            self.assertIn(generate_pages.generated_marker, output.read_text(encoding="utf-8"))


class SearchIndexTests(unittest.TestCase):
    def test_indexes_full_body_and_keeps_compact_documents(self):
        with tempfile.TemporaryDirectory() as temporary:
            posts_dir = Path(temporary)
            (posts_dir / "2026-01-01-Linux.md").write_text(
                "---\n"
                "title: Linux Guide\n"
                "date: 2026-01-01 00:00:00 +0900\n"
                "tags: [linux, shell]\n"
                "---\n\n"
                "A deployment command appears only in the full body.\n",
                encoding="utf-8",
            )
            documents = generate_search_index.collect_documents(posts_dir)
            index = generate_search_index.build_index(documents)

            self.assertEqual(len(index["documents"]), 1)
            self.assertEqual(index["terms"]["deployment"], [0])
            self.assertEqual(index["documents"][0][1], "/2026/01/01/Linux/")
            self.assertLessEqual(
                len(index["documents"][0][3]),
                generate_search_index.EXCERPT_LENGTH,
            )
            json.dumps(index, ensure_ascii=False)

    def test_markdown_cleanup_preserves_link_text(self):
        cleaned = generate_search_index.clean_markdown(
            "## 제목\n[공식 문서](https://example.com)와 **설명**"
        )

        self.assertIn("공식 문서", cleaned)
        self.assertNotIn("https://example.com", cleaned)


if __name__ == "__main__":
    unittest.main()
