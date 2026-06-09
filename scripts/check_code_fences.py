from pathlib import Path


POST_DIR = Path("_posts")


def main():
    # 마크다운 코드블록은 ```가 여는 기호와 닫는 기호로 한 쌍을 이뤄야 한다.
    # 개수가 홀수면 특정 포스트에서 코드블록이 닫히지 않아 이후 본문이 전부 코드처럼 렌더링될 수 있다.
    bad_posts = [
        str(path)
        for path in POST_DIR.glob("*.md")
        if path.read_text(encoding="utf-8").count("```") % 2
    ]

    if bad_posts:
        print("\n".join(bad_posts))
        raise SystemExit(1)

    print("All post code fences are balanced.")


if __name__ == "__main__":
    main()
