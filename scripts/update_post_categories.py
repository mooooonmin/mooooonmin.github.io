import re
from collections import Counter

from post_repository import POSTS_DIR, iter_posts


# 포스트의 주제 분류는 tags가 담당하고, category는 사전식 탐색을 위한 색인으로만 사용한다.
# 제목에 영문자나 숫자가 있으면 그 값을 우선 사용하고, 한글 제목처럼 색인 문자가 없으면 파일명과 태그를 보조 기준으로 사용한다.
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
    changed = 0

    for post in iter_posts(POSTS_DIR):
        category = category_for_post(post.title, post.slug, post.tags)
        counts[category] += 1

        new_lines = rewrite_front_matter(post.front_matter_lines, category)
        new_text = "---\n" + "\n".join(new_lines).rstrip() + "\n---\n\n" + post.body

        if new_text != post.raw_text.replace("\r\n", "\n"):
            post.path.write_text(new_text, encoding="utf-8", newline="\n")
            changed += 1

    print(f"Post categories updated successfully. changed={changed}")
    for category, count in sorted(counts.items(), key=lambda item: (item[0] == "0-9", item[0])):
        print(f"{category}: {count}")


if __name__ == "__main__":
    main()
