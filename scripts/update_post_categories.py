import os
import re
from collections import Counter


# 포스트의 주제 분류는 tags가 담당하고, category는 사전식 탐색을 위한 색인으로만 사용한다.
# 제목에 영문자나 숫자가 있으면 그 값을 우선 사용하고, 한글 제목처럼 색인 문자가 없으면 파일명과 태그를 보조 기준으로 사용한다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(BASE_DIR, "_posts")


def split_front_matter(text):
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return None, None

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, None

    return parts[1].strip("\n").splitlines(), parts[2].lstrip("\n")


def parse_front_matter(lines):
    front_matter = {}
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        front_matter[key.strip()] = value.strip().strip('"')
    return front_matter


def parse_tags(value):
    value = value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        return []
    return [tag.strip().strip('"').strip("'") for tag in value[1:-1].split(",") if tag.strip()]


def category_from_text(text):
    match = re.search(r"[A-Za-z0-9]", text)
    if not match:
        return None

    char = match.group(0).lower()
    return "0-9" if char.isdigit() else char


def category_for_post(title, slug, tags):
    for value in [title, slug, *tags]:
        category = category_from_text(value)
        if category:
            return category
    return "0-9"


def rewrite_front_matter(lines, category):
    rewritten = []
    category_written = False

    for line in lines:
        if re.match(r"^\s*category\s*:", line):
            rewritten.append(f"category: {category}")
            category_written = True
        else:
            rewritten.append(line)

    if not category_written:
        insert_at = 1 if rewritten else 0
        rewritten.insert(insert_at, f"category: {category}")

    return rewritten


def main():
    counts = Counter()

    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith(".md"):
            continue

        match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", filename)
        if not match:
            continue

        path = os.path.join(POSTS_DIR, filename)
        with open(path, "r", encoding="utf-8-sig") as f:
            text = f.read()

        lines, body = split_front_matter(text)
        if lines is None:
            continue

        front_matter = parse_front_matter(lines)
        title = front_matter.get("title", match.group(1))
        tags = parse_tags(front_matter.get("tags", "[]"))
        category = category_for_post(title, match.group(1), tags)
        counts[category] += 1

        new_lines = rewrite_front_matter(lines, category)
        new_text = "---\n" + "\n".join(new_lines).rstrip() + "\n---\n\n" + body

        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_text)

    print("Post categories updated successfully.")
    for category, count in sorted(counts.items(), key=lambda item: (item[0] == "0-9", item[0])):
        print(f"{category}: {count}")


if __name__ == "__main__":
    main()
