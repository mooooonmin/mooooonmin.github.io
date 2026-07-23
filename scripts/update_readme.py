from collections import defaultdict
from pathlib import Path

from category_config import load_category_config
from front_matter import parse_yaml_mapping
from post_repository import POSTS_DIR, iter_posts


BASE_DIR = Path(__file__).resolve().parent.parent
README_PATH = BASE_DIR / "README.md"
CONFIG_PATH = BASE_DIR / "_config.yml"


def get_site_prefix():
    config = parse_yaml_mapping(CONFIG_PATH.read_text(encoding="utf-8"))
    site_url = config.get("url", "").rstrip("/")
    baseurl = config.get("baseurl", "").strip("/")
    if not site_url:
        raise ValueError("_config.yml must define url")
    return site_url + (f"/{baseurl}" if baseurl else "")


def collect_posts(site_prefix):
    posts_by_category = defaultdict(list)
    for post in iter_posts(POSTS_DIR):
        posts_by_category[post.category].append(
            {
                "title": post.title,
                "date": post.filename_date,
                "url": site_prefix + post.url,
            }
        )
    return posts_by_category


def render_readme(posts_by_category, category_order, category_labels):
    category_rank = {name: index for index, name in enumerate(category_order)}
    lines = []
    for category in sorted(
        posts_by_category,
        key=lambda name: (category_rank.get(name, len(category_rank)), str(name)),
    ):
        posts = sorted(
            posts_by_category[category],
            key=lambda item: (item["date"], item["title"]),
            reverse=True,
        )
        category_label = category_labels.get(category, category)
        lines.extend(
            [
                "<details>",
                f"<summary><b>{category_label} ({len(posts)})</b></summary>",
                '<div markdown="1">',
                "",
                "| Date | Title |",
                "|---|---|",
            ]
        )
        for post in posts:
            lines.append(f"| {post['date']} | [{post['title']}]({post['url']}) |")
        lines.extend(["", "</div>", "</details>", ""])
    return "\n".join(lines).rstrip() + "\n"


def main():
    category_order, category_labels = load_category_config()
    readme = render_readme(
        collect_posts(get_site_prefix()),
        category_order,
        category_labels,
    )
    current = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    if readme == current:
        print("README is already up to date.")
        return 0

    README_PATH.write_text(readme, encoding="utf-8", newline="\n")
    print("README update completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
