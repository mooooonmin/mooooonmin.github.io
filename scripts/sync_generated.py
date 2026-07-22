import subprocess
import sys


GENERATORS = [
    ("Normalize post times", [sys.executable, "scripts/normalize_post_times.py"]),
    ("Update post categories", [sys.executable, "scripts/update_post_categories.py"]),
    ("Generate category pages", [sys.executable, "scripts/generate_pages.py"]),
    ("Update README", [sys.executable, "scripts/update_readme.py"]),
]


def main():
    for title, command in GENERATORS:
        print(f"\n==> {title}", flush=True)
        result = subprocess.run(command)
        if result.returncode:
            return result.returncode

    print("\nGenerated content synchronized.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
