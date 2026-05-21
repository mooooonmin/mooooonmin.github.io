import math
import os
import re
import shutil
from collections import Counter


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts_dir = os.path.join(base_dir, "_posts")
config_path = os.path.join(base_dir, "_config.yml")

category_labels = {
    "docs": "문서",
    "cs": "CS",
    "exam": "자격증",
    "docker-kubernetes": "도커/쿠버네티스",
    "linux": "Linux",
}


def read_paginate():
    with open(config_path, "r", encoding="utf-8") as f:
        config = f.read()
    match = re.search(r"^paginate:\s*(\d+)\s*$", config, re.MULTILINE)
    return int(match.group(1)) if match else 20


def parse_front_matter(content):
    front_matter = {}
    content = content.lstrip("\ufeff")
    if not content.startswith("---"):
        return front_matter

    parts = content.split("---", 2)
    if len(parts) < 3:
        return front_matter

    for line in parts[1].splitlines():
        match = re.match(r'^\s*([A-Za-z_][\w-]*):\s*"?([^"\n]+)"?\s*$', line)
        if match:
            front_matter[match.group(1)] = match.group(2).strip()

    return front_matter


def collect_posts():
    posts = []
    for filename in os.listdir(posts_dir):
        match = re.match(r"^(\d{4})-\d{2}-\d{2}-.+\.md$", filename)
        if not match:
            continue

        filepath = os.path.join(posts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            front_matter = parse_front_matter(f.read())

        year = front_matter.get("date", match.group(1))[:4]
        category = front_matter.get("category", "Uncategorized")
        posts.append({"year": year, "category": category})

    return posts


def write_page(path, layout, title, values):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["---", f"layout: {layout}", f"title: {title}"]
    for key, value in values.items():
        lines.append(f'{key}: "{value}"' if key == "year" else f"{key}: {value}")
    lines.append("---")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def remove_page_dirs(parent_dir):
    if not os.path.isdir(parent_dir):
        return

    for name in os.listdir(parent_dir):
        path = os.path.join(parent_dir, name)
        if os.path.isdir(path) and re.match(r"^page\d+$", name):
            shutil.rmtree(path)


def generate_collection_pages(parent_dir, layout, title, values, count, per_page):
    total_pages = max(1, math.ceil(count / per_page))
    remove_page_dirs(parent_dir)

    write_page(os.path.join(parent_dir, "index.md"), layout, title, values)

    for page_num in range(2, total_pages + 1):
        page_values = dict(values)
        page_values["page_num"] = page_num
        write_page(
            os.path.join(parent_dir, f"page{page_num}", "index.md"),
            layout,
            title,
            page_values,
        )


def main():
    per_page = read_paginate()
    posts = collect_posts()
    years = Counter(post["year"] for post in posts)
    categories = Counter(post["category"] for post in posts)

    for year, count in years.items():
        generate_collection_pages(
            os.path.join(base_dir, year),
            "year",
            year,
            {"year": year},
            count,
            per_page,
        )

    for category, count in categories.items():
        title = category_labels.get(category, category)
        generate_collection_pages(
            os.path.join(base_dir, "category", category),
            "category",
            title,
            {"category": category},
            count,
            per_page,
        )

    print("Year and category pages generated successfully.")


if __name__ == "__main__":
    main()
