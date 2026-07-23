import argparse
import subprocess
import sys


CHECKS = [
    ("Run automation unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ("Validate site JavaScript", ["node", "--check", "assets/js/site.js"]),
    ("Validate search JavaScript", ["node", "--check", "assets/js/search.js"]),
    ("Validate tag JavaScript", ["node", "--check", "assets/js/tags.js"]),
    ("Validate post format", [sys.executable, "scripts/check_post_format.py"]),
    ("Validate duplicate post times", [sys.executable, "scripts/check_duplicate_post_times.py"]),
    ("Validate source text encoding", [sys.executable, "scripts/check_text_encoding.py"]),
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
        "--include-site-integrity",
        action="store_true",
        help="Validate links, identifiers, and images in an existing generated site.",
    )
    parser.add_argument(
        "--site-dir",
        default="_site",
        help="Generated site directory used by optional render and integrity checks.",
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

    if args.include_site_integrity:
        checks.append(
            (
                "Validate generated site integrity",
                [sys.executable, "scripts/check_site_integrity.py", "--site-dir", args.site_dir],
            ),
        )

    if args.include_smoke:
        smoke_command = [sys.executable, "scripts/smoke_render.py", "--site-dir", args.site_dir]
        if args.skip_browser_if_unavailable:
            smoke_command.append("--skip-browser-if-unavailable")
        checks.append(("Render smoke test", smoke_command))

    for title, command in checks:
        exit_code = run_step(title, command)
        if exit_code:
            return exit_code

    print("\nAll validations passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
