import re
import sys

from post_repository import BASE_DIR, POSTS_DIR, iter_posts


SUMMARY_TITLES = {"요약", "핵심 정리", "전체 정리와 주의점"}
SOURCE_TITLES = {"참고 자료", "참고자료"}
H3_NUMBER_PATTERNS = [
    re.compile(r"^\d+[\.)]\s+"),
    re.compile(r"^Step\s+\d+[\.)]?\s+", re.IGNORECASE),
    re.compile(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*"),
]


def is_exam_post(tags):
    return "exam" in set(tags)


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


def check_post(post):
    lines = post.body.splitlines()

    if is_exam_post(post.tags):
        if post.body.count("```") % 2:
            return [(len(lines), "닫히지 않은 코드블록이 있습니다.")]
        return []

    errors = []
    in_fence = False
    h2_seen = False
    has_summary = False
    has_source = False

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
            if title == "정리":
                has_summary = True
            if title == "출처":
                has_source = True

            if title not in {"정리", "출처"} and not re.match(r"^\d+\.\s+", title):
                errors.append((line_no, "일반 H2 제목은 `## 1. 제목` 형식을 사용해야 합니다."))

            if h2_seen and previous_nonblank(lines, index) != "---":
                errors.append((line_no, "H2 섹션 사이는 `---`로 구분해야 합니다."))
            h2_seen = True

            if next_blank_count(lines, index) != 1:
                errors.append((line_no, "제목 아래에는 빈 줄을 정확히 1줄 둡니다."))

            normalized = re.sub(r"^\d+\.\s+", "", title)
            if title != "정리" and (normalized in SUMMARY_TITLES or normalized.endswith("의 정리")):
                errors.append((line_no, "마지막 요약 제목은 `## 정리`로 통일합니다."))
            if title != "출처" and normalized in SOURCE_TITLES:
                errors.append((line_no, "출처 섹션 제목은 `## 출처`로 통일합니다."))

    if in_fence:
        errors.append((len(lines), "닫히지 않은 코드블록이 있습니다."))

    if not has_summary:
        errors.append((len(lines), "일반 포스트에는 `## 정리` 섹션이 필요합니다."))
    if not has_source:
        errors.append((len(lines), "일반 포스트에는 `## 출처` 섹션이 필요합니다."))

    return errors


def main():
    all_errors = []
    for post in iter_posts(POSTS_DIR):
        for line_no, message in check_post(post):
            relative_path = post.path.relative_to(BASE_DIR)
            all_errors.append(f"{relative_path}:{line_no}: {message}")

    if all_errors:
        print("\n".join(all_errors))
        return 1

    print("Post format check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
