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
from check_post_format import check_post
from front_matter import FrontMatterError, parse_inline_list, read_front_matter, split_front_matter
from post_repository import load_post


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

    def test_supports_nested_multiline_and_quoted_list_values(self):
        text = (
            "---\n"
            "title: |\n"
            "  Linux: Basics\n"
            "tags: ['linux, shell', yaml]\n"
            "date: 2026-01-01 00:00:00 +0900\n"
            "author:\n"
            "  name: Moon\n"
            "---\n\n"
            "Body\n"
        )

        front_matter, body = read_front_matter(text)

        self.assertEqual(front_matter["title"], "Linux: Basics\n")
        self.assertEqual(parse_inline_list(front_matter["tags"]), ["linux, shell", "yaml"])
        self.assertEqual(front_matter["date"], "2026-01-01 00:00:00 +0900")
        self.assertEqual(front_matter["author"], {"name": "Moon"})
        self.assertEqual(body, "Body\n")

    def test_requires_front_matter_delimiters_on_separate_lines(self):
        lines, body = split_front_matter("---not-metadata\ntitle: Example\n---\nBody")

        self.assertIsNone(lines)
        self.assertEqual(body, "---not-metadata\ntitle: Example\n---\nBody")

    def test_rejects_non_mapping_yaml_metadata(self):
        with self.assertRaises(FrontMatterError):
            read_front_matter("---\n- invalid\n- metadata\n---\nBody\n")


class PostRepositoryTests(unittest.TestCase):
    def test_loads_normalized_post_metadata_and_url(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "2026-01-02-Linux Guide.md"
            path.write_text(
                "---\n"
                "title: Linux Guide\n"
                "category: l\n"
                "date: 2026-01-02 03:04:05 +0900\n"
                "tags: [linux, 'shell, cli']\n"
                "---\n\n"
                "Body\n",
                encoding="utf-8",
            )

            post = load_post(path)

            self.assertEqual(post.filename_date, "2026-01-02")
            self.assertEqual(post.title, "Linux Guide")
            self.assertEqual(post.category, "l")
            self.assertEqual(post.tags, ("linux", "shell, cli"))
            self.assertEqual(post.date, "2026-01-02 03:04:05 +0900")
            self.assertEqual(post.url, "/2026/01/02/Linux%20Guide/")


class PostFormatTests(unittest.TestCase):
    def test_rejects_duplicate_tags_case_insensitively(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "2026-01-02-Exam.md"
            path.write_text(
                "---\n"
                "title: Exam\n"
                "category: e\n"
                "date: 2026-01-02 03:04:05 +0900\n"
                "tags: [exam, security, Exam]\n"
                "---\n\n"
                "Body\n",
                encoding="utf-8",
            )

            errors = check_post(load_post(path))

            self.assertIn((5, "중복 태그가 있습니다: exam"), errors)


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
