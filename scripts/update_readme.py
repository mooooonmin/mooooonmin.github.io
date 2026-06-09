import glob
import os
import re
import urllib.parse
from collections import defaultdict

from category_config import load_category_config


# README는 저장소 첫 화면에서 전체 글 목록을 확인하기 위한 인덱스다.
# GitHub Actions가 _posts 변경 시 이 스크립트를 실행해 목록을 최신 상태로 맞춘다.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts_dir = os.path.join(base_dir, "_posts")
readme_path = os.path.join(base_dir, "README.md")

data = defaultdict(lambda: defaultdict(list))

category_order, category_labels = load_category_config()

for filepath in glob.glob(os.path.join(posts_dir, "*.md")):
    # Jekyll 게시글 파일명 규칙에서 날짜와 URL slug를 가져온다.
    filename = os.path.basename(filepath)
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", filename)
    if not match:
        continue

    year, month, day, slug = match.groups()
    slug = slug.strip()
    slug_url = urllib.parse.quote(slug)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    title = slug
    category = "Uncategorized"

    content_for_front_matter = content.lstrip("\ufeff")

    if content_for_front_matter.startswith("---"):
        # README에는 제목과 카테고리만 필요하므로 front matter에서 필요한 값만 추출한다.
        parts = content_for_front_matter.split("---", 2)
        if len(parts) >= 3:
            front_matter = parts[1]
            title_match = re.search(r'^\s*title:\s*"?([^\n"]+)"?\s*$', front_matter, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
            category_match = re.search(r'^\s*category:\s*"?([^\n"]+)"?\s*$', front_matter, re.MULTILINE)
            if category_match:
                category = category_match.group(1).strip()

    post_url = f"https://mooooonmin.github.io/{year}/{month}/{day}/{slug_url}/"

    data[year][category].append(
        {
            "title": title,
            "date": f"{year}-{month}-{day}",
            "url": post_url,
        }
    )

posts_by_category = defaultdict(list)
for categories in data.values():
    for category, posts in categories.items():
        posts_by_category[category].extend(posts)

lines = []

for category in sorted(posts_by_category.keys(), key=lambda name: (category_order.index(name) if name in category_order else 999, str(name))):
    # 카테고리는 주제 대신 사전식 색인으로만 사용한다.
    posts = sorted(posts_by_category[category], key=lambda item: (item["date"], item["title"]), reverse=True)
    category_label = category_labels.get(category, category)
    lines.append("<details>")
    lines.append(f"<summary><b>{category_label} ({len(posts)})</b></summary>")
    lines.append('<div markdown="1">')
    lines.append("")
    lines.append("| Date | Title |")
    lines.append("|---|---|")

    for post in posts:
        lines.append(f"| {post['date']} | [{post['title']}]({post['url']}) |")

    lines.append("")
    lines.append("</div>")
    lines.append("</details>")
    lines.append("")

readme = "\n".join(lines).rstrip() + "\n"

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README update completed successfully.")
