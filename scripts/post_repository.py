import re
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from front_matter import FrontMatterError, parse_inline_list, parse_front_matter, split_front_matter


BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "_posts"
POST_FILENAME = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$")


@dataclass(frozen=True)
class Post:
    path: Path
    raw_text: str
    front_matter_lines: tuple[str, ...]
    front_matter: dict
    body: str
    year: str
    month: str
    day: str
    slug: str

    @property
    def filename_date(self):
        return f"{self.year}-{self.month}-{self.day}"

    @property
    def title(self):
        return str(self.front_matter.get("title") or self.slug)

    @property
    def category(self):
        return str(self.front_matter.get("category") or "Uncategorized")

    @property
    def tags(self):
        return tuple(parse_inline_list(self.front_matter.get("tags")))

    @property
    def date(self):
        return str(self.front_matter.get("date") or self.filename_date)

    @property
    def url(self):
        encoded_slug = urllib.parse.quote(self.slug.strip())
        return f"/{self.year}/{self.month}/{self.day}/{encoded_slug}/"


def load_post(path):
    path = Path(path)
    match = POST_FILENAME.fullmatch(path.name)
    if not match:
        raise ValueError(f"invalid post filename: {path.name}")

    raw_text = path.read_text(encoding="utf-8-sig")
    front_matter_lines, body = split_front_matter(raw_text)
    if front_matter_lines is None:
        raise FrontMatterError(f"{path}: front matter delimiters are missing")

    try:
        front_matter = parse_front_matter(front_matter_lines)
    except FrontMatterError as error:
        raise FrontMatterError(f"{path}: {error}") from error
    year, month, day, slug = match.groups()
    return Post(
        path=path,
        raw_text=raw_text,
        front_matter_lines=tuple(front_matter_lines),
        front_matter=front_matter,
        body=body,
        year=year,
        month=month,
        day=day,
        slug=slug,
    )


def iter_posts(posts_dir=POSTS_DIR):
    posts_dir = Path(posts_dir)
    for path in sorted(posts_dir.glob("*.md")):
        if POST_FILENAME.fullmatch(path.name):
            yield load_post(path)
