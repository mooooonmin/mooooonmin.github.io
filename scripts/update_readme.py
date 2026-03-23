import glob
import os
import re
from collections import defaultdict


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts_dir = os.path.join(base_dir, "_posts")
readme_path = os.path.join(base_dir, "README.md")

year_counts = defaultdict(int)

for filepath in glob.glob(os.path.join(posts_dir, "*.md")):
    filename = os.path.basename(filepath)
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", filename)
    if not match:
        continue

    year = match.group(1)
    year_counts[year] += 1

lines = []

for year in sorted(year_counts.keys(), reverse=True):
    count = year_counts[year]
    lines.append(f"<details>")
    lines.append(f"<summary><b>{year} ({count})</b></summary>")
    lines.append(f"</details>")

readme = "\n".join(lines).strip() + "\n"

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README update completed successfully.")
