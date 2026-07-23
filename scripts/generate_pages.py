import math
import os
import re
import shutil
from collections import Counter

from category_config import load_category_config
from post_repository import POSTS_DIR, iter_posts


# _posts 개수를 기준으로 알파벳/숫자 카테고리별 목록 페이지를 자동 생성한다.
# 새 글이 추가되어 페이지 수가 바뀌어도 page2, page3 같은 폴더를 직접 만들 필요가 없다.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(base_dir, "_config.yml")
category_dir = os.path.join(base_dir, "category")
generated_marker = "generated_by: scripts/generate_pages.py"

category_order, category_labels = load_category_config()


def read_paginate():
    # Jekyll 설정의 paginate 값을 읽어 목록 한 페이지에 표시할 글 수를 맞춘다.
    with open(config_path, "r", encoding="utf-8") as f:
        config = f.read()
    match = re.search(r"^paginate:\s*(\d+)\s*$", config, re.MULTILINE)
    return int(match.group(1)) if match else 20


def collect_posts():
    return list(iter_posts(POSTS_DIR))


def write_page(path, layout, title, values):
    lines = ["---", generated_marker, f"layout: {layout}", f"title: {title}"]
    for key, value in values.items():
        lines.append(f'{key}: "{value}"' if key == "year" else f"{key}: {value}")
    lines.append("---")
    lines.append("")
    content = "\n".join(lines)

    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read() == content:
                return False

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return True


def is_generated_dir(path):
    index_path = os.path.join(path, "index.md")
    if not os.path.isfile(index_path):
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        return generated_marker in f.read()


def remove_page_dirs(parent_dir):
    if not os.path.isdir(parent_dir):
        return

    for name in os.listdir(parent_dir):
        path = os.path.join(parent_dir, name)
        if (
            os.path.isdir(path)
            and re.match(r"^page\d+$", name)
            and is_generated_dir(path)
        ):
            shutil.rmtree(path)


def remove_stale_category_dirs(active_categories):
    if not os.path.isdir(category_dir):
        return

    for name in os.listdir(category_dir):
        path = os.path.join(category_dir, name)
        if (
            os.path.isdir(path)
            and name not in active_categories
            and is_generated_dir(path)
        ):
            shutil.rmtree(path)


def generate_collection_pages(parent_dir, layout, title, values, count, per_page):
    # 첫 페이지는 index.md, 두 번째 페이지부터 page2/index.md 형식으로 만든다.
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
    categories = Counter(post.category for post in posts)
    remove_stale_category_dirs(set(categories.keys()))

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

    print("Category pages generated successfully.")


if __name__ == "__main__":
    main()
