import os
import re
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(BASE_DIR, "_posts")

SUMMARY_TITLES = {"정리", "요약", "핵심 정리", "전체 정리와 주의점"}
SOURCE_TITLES = {"참고 자료", "참고자료"}
H3_NUMBER_PATTERNS = [
    re.compile(r"^\d+[\.)]\s+"),
    re.compile(r"^Step\s+\d+[\.)]?\s+", re.IGNORECASE),
    re.compile(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*"),
]


def split_front_matter(text):
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text.splitlines()

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text.splitlines()

    front_matter = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        front_matter[key.strip()] = value.strip()
    return front_matter, parts[2].splitlines()


def is_exam_post(front_matter):
    tags = front_matter.get("tags", "")
    return "exam" in {tag.strip().strip('"').strip("'") for tag in tags.strip("[]").split(",")}


def previous_nonblank(lines, index):
    for i in range(index - 1, -1, -1):
        if lines[i].strip():
            return lines[i].strip()
    return None


def next_blank_count(lines, index):
    count = 0
    for i in range(index + 1, len(lines)):
        if lines[i].strip():
            break
        count += 1
    return count


def check_post(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        front_matter, lines = split_front_matter(f.read())

    if is_exam_post(front_matter):
        return []

    errors = []
    in_fence = False
    h2_seen = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        line_no = index + 1

        if re.match(r"^\s*\*\s+", line):
            errors.append((line_no, "설명 목록은 `*` 대신 `-`를 사용해야 합니다."))

        if line.startswith("### ") or line.startswith("#### "):
            heading = line.lstrip("#").strip()
            if any(pattern.match(heading) for pattern in H3_NUMBER_PATTERNS):
                errors.append((line_no, "H3/H4 제목에는 번호를 붙이지 않습니다."))

        if line.startswith("## "):
            title = line[3:].strip()
            if title not in {"핵심 정리", "출처"} and not re.match(r"^\d+\.\s+", title):
                errors.append((line_no, "일반 H2 제목은 `## 1. 제목` 형식을 사용해야 합니다."))

            if h2_seen and previous_nonblank(lines, index) != "---":
                errors.append((line_no, "H2 섹션 사이는 `---`로 구분해야 합니다."))
            h2_seen = True

            if next_blank_count(lines, index) != 1:
                errors.append((line_no, "제목 아래에는 빈 줄을 정확히 1줄 둡니다."))

            normalized = re.sub(r"^\d+\.\s+", "", title)
            if title != "핵심 정리" and (normalized in SUMMARY_TITLES or normalized.endswith("의 핵심 정리")):
                errors.append((line_no, "마지막 요약 제목은 `## 핵심 정리`로 통일합니다."))
            if title != "출처" and normalized in SOURCE_TITLES:
                errors.append((line_no, "출처 섹션 제목은 `## 출처`로 통일합니다."))

    if in_fence:
        errors.append((len(lines), "닫히지 않은 코드블록이 있습니다."))

    return errors


def main():
    all_errors = []
    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(POSTS_DIR, filename)
        for line_no, message in check_post(path):
            all_errors.append(f"{os.path.relpath(path, BASE_DIR)}:{line_no}: {message}")

    if all_errors:
        print("\n".join(all_errors))
        return 1

    print("Post format check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
