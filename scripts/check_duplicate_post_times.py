import re
from collections import defaultdict

from post_repository import POSTS_DIR, iter_posts

DATE_PATTERN = re.compile(
    r"^date:\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+([+-]\d{4})\s*$",
    re.MULTILINE,
)


def main():
    # Jekyll은 같은 날짜의 포스트가 많아도 처리할 수 있지만, 같은 초까지 겹치면 정렬 순서가 모호해진다.
    # 새 글 작성 자동화가 00:00:10처럼 시간을 밀어 넣는 규칙을 지키는지 여기서 검증한다.
    seen = defaultdict(list)
    for post in iter_posts(POSTS_DIR):
        match = DATE_PATTERN.search(post.raw_text)
        if match:
            date, time, _timezone = match.groups()
            seen[(date, time)].append(str(post.path))

    duplicates = {key: paths for key, paths in seen.items() if len(paths) > 1}
    if duplicates:
        for (date, time), paths in duplicates.items():
            print(date, time)
            print("\n".join(paths))
        raise SystemExit(1)

    print("No duplicate post date-time values found.")


if __name__ == "__main__":
    main()
