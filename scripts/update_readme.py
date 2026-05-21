import glob
import os
import re
import urllib.parse
from collections import defaultdict


# README는 저장소 첫 화면에서 전체 글 목록을 확인하기 위한 인덱스다.
# GitHub Actions가 _posts 변경 시 이 스크립트를 실행해 목록을 최신 상태로 맞춘다.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts_dir = os.path.join(base_dir, "_posts")
readme_path = os.path.join(base_dir, "README.md")

data = defaultdict(lambda: defaultdict(list))

category_labels = {
    "docs": "문서",
    "cs": "CS",
    "exam": "자격증",
    "docker-kubernetes": "도커/쿠버네티스",
    "linux": "Linux",
}

category_order = {
    "docs": 0,
    "cs": 1,
    "exam": 2,
    "docker-kubernetes": 3,
    "linux": 4,
}

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

lines = []

for year in sorted(data.keys(), reverse=True):
    # 연도 > 카테고리 > 게시글 순서의 접이식 목록을 만든다.
    total_posts = sum(len(posts) for posts in data[year].values())
    lines.append("<details>")
    lines.append(f"<summary><b>{year} ({total_posts})</b></summary>")
    lines.append('<div markdown="1">')
    lines.append("")

    for category in sorted(data[year].keys(), key=lambda name: (category_order.get(name, 999), str(name))):
        posts = sorted(data[year][category], key=lambda item: item["date"], reverse=True)
        category_label = category_labels.get(category, category)
        lines.append("<details>")
        lines.append(f"<summary><b>{category_label} ({len(posts)})</b></summary>")
        lines.append('<div markdown="1">')
        lines.append("")

        for post in posts:
            lines.append(f"- [{post['date']}] [{post['title']}]({post['url']})")

        lines.append("")
        lines.append("</div>")
        lines.append("</details>")
        lines.append("")

    lines.append("</div>")
    lines.append("</details>")

readme = "\n".join(lines).rstrip() + "\n"

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README update completed successfully.")
