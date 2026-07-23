import re
from collections import defaultdict
from datetime import datetime, timedelta

from post_repository import BASE_DIR, POSTS_DIR, iter_posts


# 같은 날짜에 작성된 게시글들이 동일한 시간을 갖지 않도록 front matter의 date 시간을 정규화한다.
# 날짜는 파일명(YYYY-MM-DD-...)을 기준으로 삼고, 같은 날짜 안에서는 기존 시간과 파일명 순서대로 10초씩 증가시킨다.
TIME_STEP_SECONDS = 10

DATE_LINE_RE = re.compile(
    r"^(date:\s*)(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2}:\d{2})\s+([+-]\d{4})\s*$",
    re.MULTILINE,
)


def parse_time(value):
    # 과거 글 중 3:00:00처럼 시간이 한 자리인 경우도 있어 %H 파싱으로 함께 처리한다.
    return datetime.strptime(value, "%H:%M:%S").time()


def collect_posts():
    posts_by_date = defaultdict(list)

    for post in iter_posts(POSTS_DIR):
        filename_date = post.filename_date
        content = post.raw_text
        date_match = DATE_LINE_RE.search(content)
        if not date_match:
            continue

        _, _front_matter_date, time_value, timezone = date_match.groups()
        posts_by_date[filename_date].append(
            {
                "post": post,
                "content": content,
                "date_match": date_match,
                "time": parse_time(time_value),
                "timezone": timezone,
            }
        )

    return posts_by_date


def normalize_group(posts):
    # 기존 시간이 있으면 그 순서를 우선 유지하고, 시간이 같으면 파일명으로 순서를 고정한다.
    normalized = []
    for index, post in enumerate(sorted(posts, key=lambda item: (item["time"], item["post"].path.name))):
        new_time = (datetime(2000, 1, 1) + timedelta(seconds=index * TIME_STEP_SECONDS)).strftime("%H:%M:%S")
        normalized.append((post, new_time))
    return normalized


def update_post(post, new_time):
    filename_date = post["post"].filename_date
    prefix = post["date_match"].group(1)
    timezone = post["timezone"]
    new_date_line = f"{prefix}{filename_date} {new_time} {timezone}"

    start, end = post["date_match"].span()
    content = post["content"][:start] + new_date_line + post["content"][end:]

    if content != post["content"]:
        post["post"].path.write_text(content, encoding="utf-8", newline="\n")
        return True
    return False


def main():
    posts_by_date = collect_posts()
    changed = []

    for posts in posts_by_date.values():
        if len(posts) <= 1:
            continue

        for post, new_time in normalize_group(posts):
            if update_post(post, new_time):
                changed.append(post["post"].path)

    print(f"Post times normalized successfully. changed={len(changed)}")
    for path in changed:
        print(path.relative_to(BASE_DIR).as_posix())


if __name__ == "__main__":
    main()
