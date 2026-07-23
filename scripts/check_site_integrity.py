import argparse
import posixpath
import re
import struct
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SITE_DIR = BASE_DIR / "_site"
REFERENCE_ATTRIBUTES = {
    "a": ("href",),
    "form": ("action",),
    "iframe": ("src",),
    "img": ("src",),
    "link": ("href",),
    "script": ("src",),
    "source": ("src",),
}
EXTERNAL_SCHEMES = {"data", "http", "https", "mailto", "tel"}
JPEG_START_OF_FRAME = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}


@dataclass(frozen=True)
class Reference:
    line: int
    tag: str
    attribute: str
    value: str | None


@dataclass(frozen=True)
class ImageElement:
    line: int
    attributes: dict[str, str | None]


@dataclass
class Document:
    path: Path
    ids: dict[str, list[int]] = field(default_factory=dict)
    references: list[Reference] = field(default_factory=list)
    images: list[ImageElement] = field(default_factory=list)
    allows_dynamic_fragments: bool = False


@dataclass
class IntegrityReport:
    html_files: int = 0
    internal_references: int = 0
    images: int = 0
    errors: list[str] = field(default_factory=list)


class InventoryParser(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.document = Document(path=path)

    def handle_starttag(self, tag, attrs):
        line, _ = self.getpos()
        attributes = dict(attrs)

        if "data-dynamic-fragments" in attributes:
            self.document.allows_dynamic_fragments = True

        if "id" in attributes:
            identifier = attributes["id"] or ""
            self.document.ids.setdefault(identifier, []).append(line)

        for attribute in REFERENCE_ATTRIBUTES.get(tag, ()):
            if attribute in attributes:
                self.document.references.append(
                    Reference(line, tag, attribute, attributes[attribute]),
                )

        if tag == "img":
            self.document.images.append(ImageElement(line, attributes))


def format_error(site_dir, path, line, message):
    relative = path.relative_to(site_dir).as_posix()
    return f"{relative}:{line}: {message}"


def parse_document(path):
    parser = InventoryParser(path)
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.document


def resolve_internal_target(site_dir, page_path, url_path):
    decoded_path = unquote(url_path)
    if decoded_path.startswith("/"):
        relative = decoded_path.lstrip("/")
    else:
        page_directory = page_path.relative_to(site_dir).parent.as_posix()
        relative = posixpath.normpath(posixpath.join(page_directory, decoded_path))

    candidate = (site_dir / relative).resolve()
    try:
        candidate.relative_to(site_dir)
    except ValueError:
        return None, "path escapes the generated site directory"

    candidates = []
    if decoded_path.endswith("/"):
        candidates.append(candidate / "index.html")
    else:
        candidates.append(candidate)
        candidates.append(candidate / "index.html")
        if not candidate.suffix:
            candidates.append(candidate.with_suffix(".html"))

    for target in candidates:
        if target.is_file():
            return target, None
    return None, "target does not exist"


def resolve_reference(site_dir, page_path, value):
    if value is None or not value.strip():
        return None, None, "reference is empty"
    value = value.strip()
    if any(ord(character) < 32 for character in value):
        return None, None, "reference contains a control character"
    if "\\" in value:
        return None, None, "reference must use forward slashes"

    try:
        parts = urlsplit(value)
    except ValueError as error:
        return None, None, f"reference is not a valid URL: {error}"

    scheme = parts.scheme.lower()
    if scheme in EXTERNAL_SCHEMES or parts.netloc or value.startswith("//"):
        return None, None, None
    if scheme:
        return None, None, f"unsupported URL scheme: {scheme}"
    if not parts.path and not parts.query and not parts.fragment:
        return None, None, "reference has no path, query, or fragment"

    if parts.path:
        target, error = resolve_internal_target(site_dir, page_path, parts.path)
        if error:
            return None, unquote(parts.fragment), error
    else:
        target = page_path

    return target, unquote(parts.fragment), None


def read_png_size(path):
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("invalid PNG header")
    return struct.unpack(">II", data[16:24])


def read_jpeg_size(path):
    with path.open("rb") as stream:
        if stream.read(2) != b"\xff\xd8":
            raise ValueError("invalid JPEG header")

        while True:
            marker_start = stream.read(1)
            if not marker_start:
                break
            if marker_start != b"\xff":
                continue

            marker = stream.read(1)
            while marker == b"\xff":
                marker = stream.read(1)
            if not marker:
                break
            marker_value = marker[0]
            if marker_value in {0x01, *range(0xD0, 0xD9)}:
                continue

            length_bytes = stream.read(2)
            if len(length_bytes) != 2:
                break
            segment_length = struct.unpack(">H", length_bytes)[0]
            if segment_length < 2:
                raise ValueError("invalid JPEG segment length")

            if marker_value in JPEG_START_OF_FRAME:
                segment = stream.read(segment_length - 2)
                if len(segment) < 5:
                    break
                height, width = struct.unpack(">HH", segment[1:5])
                return width, height
            stream.seek(segment_length - 2, 1)

    raise ValueError("JPEG dimensions were not found")


def read_image_size(path):
    suffix = path.suffix.lower()
    if suffix == ".png":
        return read_png_size(path)
    if suffix in {".jpg", ".jpeg"}:
        return read_jpeg_size(path)
    return None


def parse_positive_dimension(value):
    if value is None or not re.fullmatch(r"[1-9]\d*", value):
        return None
    return int(value)


def validate_image(site_dir, document, image, report):
    attributes = image.attributes
    source = attributes.get("src")
    prefix = format_error(site_dir, document.path, image.line, "")

    if "alt" not in attributes:
        report.errors.append(f"{prefix}image is missing an alt attribute")

    width = parse_positive_dimension(attributes.get("width"))
    height = parse_positive_dimension(attributes.get("height"))
    if width is None or height is None:
        report.errors.append(f"{prefix}image width and height must be positive integers")

    if source is None:
        return
    target, _, error = resolve_reference(site_dir, document.path, source)
    if error or target is None:
        return

    expected_size = read_image_size(target)
    if expected_size:
        if attributes.get("loading") not in {"eager", "lazy"}:
            report.errors.append(f"{prefix}raster image must declare loading=\"lazy\" or loading=\"eager\"")
        if attributes.get("decoding") not in {"async", "auto", "sync"}:
            report.errors.append(f"{prefix}raster image must declare a valid decoding mode")
        if width is not None and height is not None and (width, height) != expected_size:
            report.errors.append(
                f"{prefix}declared image size {width}x{height} does not match {expected_size[0]}x{expected_size[1]}",
            )


def validate_site(site_dir):
    site_dir = Path(site_dir).resolve()
    report = IntegrityReport()
    html_paths = sorted(site_dir.rglob("*.html"))
    documents = {path: parse_document(path) for path in html_paths}
    report.html_files = len(documents)

    for document in documents.values():
        for identifier, lines in document.ids.items():
            if not identifier:
                for line in lines:
                    report.errors.append(format_error(site_dir, document.path, line, "id attribute is empty"))
            elif len(lines) > 1:
                report.errors.append(
                    format_error(
                        site_dir,
                        document.path,
                        lines[1],
                        f'duplicate id "{identifier}" appears on lines {", ".join(map(str, lines))}',
                    ),
                )

        for reference in document.references:
            target, fragment, error = resolve_reference(site_dir, document.path, reference.value)
            if error:
                report.errors.append(
                    format_error(
                        site_dir,
                        document.path,
                        reference.line,
                        f"{reference.tag}[{reference.attribute}] {error}: {reference.value!r}",
                    ),
                )
                continue
            if target is None:
                continue

            report.internal_references += 1
            if fragment:
                target_document = documents.get(target)
                if (
                    target_document is not None
                    and not target_document.allows_dynamic_fragments
                    and fragment not in target_document.ids
                ):
                    report.errors.append(
                        format_error(
                            site_dir,
                            document.path,
                            reference.line,
                            f'fragment "#{fragment}" does not exist in {target.relative_to(site_dir).as_posix()}',
                        ),
                    )

        report.images += len(document.images)
        for image in document.images:
            try:
                validate_image(site_dir, document, image, report)
            except (OSError, ValueError) as error:
                report.errors.append(format_error(site_dir, document.path, image.line, f"cannot inspect image: {error}"))

    report.errors.sort()
    return report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate generated HTML links, identifiers, and image metadata without external network requests.",
    )
    parser.add_argument(
        "--site-dir",
        default=str(DEFAULT_SITE_DIR),
        help="Generated static site directory. Default: _site",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    site_dir = Path(args.site_dir).resolve()
    if not (site_dir / "index.html").is_file():
        print(f"{site_dir} does not contain index.html. Build the site before validating it.")
        return 2

    report = validate_site(site_dir)
    if report.errors:
        print("\n".join(report.errors))
        print(f"Site integrity validation failed with {len(report.errors)} error(s).")
        return 1

    print(
        "Site integrity validation passed. "
        f"html={report.html_files} internal_references={report.internal_references} images={report.images}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
