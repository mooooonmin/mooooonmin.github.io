from pathlib import Path


CHECK_PATHS = [
    Path("_layouts"),
    Path("_sass"),
    Path("scripts"),
    Path("docs"),
    Path("Gemfile"),
    Path("_config.yml"),
    Path("search.html"),
]

MOJIBAKE_CODEPOINTS = [
    0xFFFD,  # replacement character
    0x91C9,
    0x81FE,
    0x5A9B,
    0x745C,
]
MOJIBAKE_TOKENS = [chr(codepoint) for codepoint in MOJIBAKE_CODEPOINTS]


def iter_files():
    for path in CHECK_PATHS:
        if path.is_file():
            yield path
            continue

        if not path.exists():
            continue

        for child in path.rglob("*"):
            if child.is_file() and child.suffix in {".html", ".scss", ".py", ".md", ".yml"}:
                yield child


def main():
    # 코드, 설정, 내부 문서에서 깨진 한글 주석이 다시 들어오지 않도록 대표 mojibake 문자를 검출한다.
    # 포스트 본문은 사용자가 입력한 원문과 시험 문제를 보존해야 하므로 검사 대상에서 제외한다.
    bad = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(token in line for token in MOJIBAKE_TOKENS):
                bad.append(f"{path}:{line_number}: {line}")

    if bad:
        print("\n".join(item.encode("unicode_escape").decode("ascii") for item in bad))
        raise SystemExit(1)

    print("No mojibake text found in source comments/docs.")


if __name__ == "__main__":
    main()
