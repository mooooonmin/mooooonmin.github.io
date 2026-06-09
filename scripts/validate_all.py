import argparse
import subprocess
import sys


CHECKS = [
    ("Normalize post times", [sys.executable, "scripts/normalize_post_times.py"]),
    ("Update post categories", [sys.executable, "scripts/update_post_categories.py"]),
    ("Generate category pages", [sys.executable, "scripts/generate_pages.py"]),
    ("Update README", [sys.executable, "scripts/update_readme.py"]),
    ("Validate post format", [sys.executable, "scripts/check_post_format.py"]),
    ("Validate code fences", [sys.executable, "scripts/check_code_fences.py"]),
    ("Validate duplicate post times", [sys.executable, "scripts/check_duplicate_post_times.py"]),
    ("Validate whitespace", ["git", "diff", "--check"]),
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the local validation suite used before committing blog changes.",
    )
    parser.add_argument(
        "--include-smoke",
        action="store_true",
        help="Run browser smoke rendering checks after the fast validation steps.",
    )
    parser.add_argument(
        "--skip-browser-if-unavailable",
        action="store_true",
        help="Pass through to smoke_render.py when --include-smoke is used.",
    )
    return parser.parse_args()


def run_step(title, command):
    print(f"\n==> {title}", flush=True)
    print(" ".join(command), flush=True)
    result = subprocess.run(command)
    if result.returncode:
        print(f"\nFAILED: {title}", flush=True)
        print(f"exit_code={result.returncode}", flush=True)
        return result.returncode
    return 0


def main():
    args = parse_args()
    checks = list(CHECKS)

    if args.include_smoke:
        smoke_command = [sys.executable, "scripts/smoke_render.py"]
        if args.skip_browser_if_unavailable:
            smoke_command.append("--skip-browser-if-unavailable")
        checks.append(("Render smoke test", smoke_command))

    # 앞 단계에서 생성 파일을 갱신한 뒤 바로 검증한다.
    # 실패 시 어떤 명령에서 멈췄는지 보이도록 한 단계씩 순차 실행한다.
    for title, command in checks:
        exit_code = run_step(title, command)
        if exit_code:
            return exit_code

    print("\nAll validations passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
