import struct
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import check_site_integrity


def write_png(path, width=1, height=1):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
    )


class SiteIntegrityTests(unittest.TestCase):
    def test_accepts_valid_internal_references_and_image_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            (site / "about").mkdir()
            (site / "assets").mkdir()
            (site / "index.html").write_text(
                '<a href="/about/#details">About</a>'
                '<img src="/images/pixel.png" alt="Pixel" width="2" height="3" loading="lazy" decoding="async">'
                '<script src="/assets/app.js"></script>',
                encoding="utf-8",
            )
            (site / "about" / "index.html").write_text('<h1 id="details">Details</h1>', encoding="utf-8")
            (site / "assets" / "app.js").write_text("", encoding="utf-8")
            write_png(site / "images" / "pixel.png", 2, 3)

            report = check_site_integrity.validate_site(site)

            self.assertEqual(report.errors, [])
            self.assertEqual(report.html_files, 2)
            self.assertEqual(report.images, 1)

    def test_allows_fragments_on_an_explicit_dynamic_fragment_page(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            (site / "tags").mkdir()
            (site / "index.html").write_text('<a href="/tags/#linux">Linux</a>', encoding="utf-8")
            (site / "tags" / "index.html").write_text(
                '<main data-dynamic-fragments></main>',
                encoding="utf-8",
            )

            report = check_site_integrity.validate_site(site)

            self.assertEqual(report.errors, [])

    def test_reports_broken_links_fragments_ids_and_image_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            (site / "index.html").write_text(
                '<a href="">Empty</a>'
                '<a href="/missing/">Missing</a>'
                '<a href="#unknown">Unknown fragment</a>'
                '<div id="duplicate"></div><div id="duplicate"></div>'
                '<img src="/images/pixel.png" width="4" height="3">',
                encoding="utf-8",
            )
            write_png(site / "images" / "pixel.png", 2, 3)

            report = check_site_integrity.validate_site(site)
            messages = "\n".join(report.errors)

            self.assertIn("reference is empty", messages)
            self.assertIn("target does not exist", messages)
            self.assertIn('fragment "#unknown" does not exist', messages)
            self.assertIn('duplicate id "duplicate"', messages)
            self.assertIn("image is missing an alt attribute", messages)
            self.assertIn("raster image must declare loading", messages)
            self.assertIn("raster image must declare a valid decoding mode", messages)
            self.assertIn("declared image size 4x3 does not match 2x3", messages)


if __name__ == "__main__":
    unittest.main()
