import math
import os
import re
import shutil
from collections import Counter


# _posts 개수를 기준으로 연도별/카테고리별 목록 페이지를 자동 생성한다.
# 새 글이 추가되어 페이지 수가 바뀌어도 page2, page3 같은 폴더를 직접 만들 필요가 없다.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts_dir = os.path.join(base_dir, "_posts")
config_path = os.path.join(base_dir, "_config.yml")

category_labels = {
    "docs": "Docs",
    "cs": "CS",
    "exam": "Exam",
    "docker-kubernetes": "Docker/Kubernetes",
    "linux": "Linux",
}


def read_paginate():
    # Jekyll 설정의 paginate 값을 읽어 목록 한 페이지에 표시할 글 수를 맞춘다.
    with open(config_path, "r", encoding="utf-8") as f:
        config = f.read()
    match = re.search(r"^paginate:\s*(\d+)\s*$", config, re.MULTILINE)
    return int(match.group(1)) if match else 20


def parse_front_matter(content):
    # 게시글 상단 YAML front matter에서 date/category 같은 목록 생성용 값만 추출한다.
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
    # _posts 파일명 규칙에 맞는 게시글만 순회하고 연도/카테고리를 모은다.
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
    # 실제 목록 내용은 Jekyll layout이 렌더링하므로 생성 파일에는 front matter만 쓴다.
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["---", f"layout: {layout}", f"title: {title}"]
    for key, value in values.items():
        lines.append(f'{key}: "{value}"' if key == "year" else f"{key}: {value}")
    lines.append("---")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def remove_page_dirs(parent_dir):
    # 글 수가 줄어들었을 때 남는 pageN 폴더를 제거해 죽은 페이지가 배포되지 않게 한다.
    if not os.path.isdir(parent_dir):
        return

    for name in os.listdir(parent_dir):
        path = os.path.join(parent_dir, name)
        if os.path.isdir(path) and re.match(r"^page\d+$", name):
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
    # 연도별 아카이브와 카테고리 아카이브를 같은 규칙으로 생성한다.
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
