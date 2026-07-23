import html
import json
import re
from collections import defaultdict
from pathlib import Path

from post_repository import POSTS_DIR, iter_posts


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "assets" / "data" / "search-index.json"
SEARCH_TERM = re.compile(r"[0-9A-Za-z가-힣_+#]{2,}")
MARKDOWN_LINK = re.compile(r"!?\[([^]]*)\]\([^)]*\)")
HTML_TAG = re.compile(r"<[^>]+>")
MARKDOWN_MARKER = re.compile(r"(?:^|\s)[#>*_~`-]+(?=\s|$)")
WHITESPACE = re.compile(r"\s+")
EXCERPT_LENGTH = 180


def clean_markdown(value):
    value = MARKDOWN_LINK.sub(r"\1", value)
    value = HTML_TAG.sub(" ", value)
    value = MARKDOWN_MARKER.sub(" ", value)
    return WHITESPACE.sub(" ", html.unescape(value)).strip()


def collect_documents(posts_dir=POSTS_DIR):
    documents = []
    for post in iter_posts(posts_dir):
        tags = " ".join(post.tags)
        content = clean_markdown(post.body)
        documents.append(
            {
                "date": post.date,
                "title": post.title,
                "url": post.url,
                "tags": tags,
                "content": content,
            }
        )
    return sorted(documents, key=lambda item: item["date"], reverse=True)


def build_index(documents):
    postings = defaultdict(list)
    compact_documents = []
    for document_id, document in enumerate(documents):
        searchable = " ".join(
            [document["title"], document["tags"], document["content"]]
        ).lower()
        for term in sorted(set(SEARCH_TERM.findall(searchable))):
            postings[term].append(document_id)
        compact_documents.append(
            [
                document["title"],
                document["url"],
                document["tags"],
                document["content"][:EXCERPT_LENGTH],
            ]
        )
    return {"documents": compact_documents, "terms": dict(sorted(postings.items()))}


def render_index(documents):
    return json.dumps(
        build_index(documents),
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n"


def main():
    content = render_index(collect_documents())
    current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    if content == current:
        print("Search index is already up to date.")
        return 0
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"Search index updated. bytes={len(content.encode('utf-8'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
