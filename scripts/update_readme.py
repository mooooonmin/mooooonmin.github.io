import glob
import os
import re
from collections import defaultdict
import urllib.parse

posts_dir = r"d:\02.프로젝트\mooooonmin.github.io\_posts"
readme_path = r"d:\02.프로젝트\mooooonmin.github.io\README.md"

data = defaultdict(lambda: defaultdict(list))

for filepath in glob.glob(os.path.join(posts_dir, "*.md")):
    filename = os.path.basename(filepath)
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", filename)
    if not match:
        continue
    
    year, month, day, slug = match.groups()
    slug = slug.replace(" ", "-").lower() # Basic slugify
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    title = slug
    category = "미분류"
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            t_match = re.search(r"\ntitle:\s*\"?([^\n\"]+)\"?", fm)
            if t_match:
                title = t_match.group(1).strip()
            c_match = re.search(r"\ncategory:\s*\"?([^\n\"]+)\"?", fm)
            if c_match:
                category = c_match.group(1).strip()

    # Encode URL correctly to prevent markdown parsing issues
    post_url = f"https://mooooonmin.github.io/{year}/{month}/{day}/{urllib.parse.quote(slug)}/"
    
    data[year][category].append({
        "title": title,
        "date": f"{year}-{month}-{day}",
        "url": post_url
    })

readme = """# 📝 기록저장소 (mooooonmin)

## 📚 포스팅 인덱스
"""

for year in sorted(data.keys(), reverse=True):
    total_posts = sum(len(posts) for posts in data[year].values())
    readme += f"\n<details>\n<summary><b>📂 {year} ({total_posts})</b></summary>\n<div markdown=\"1\">\n\n"
    
    # Sort categories alphabetically/numerically
    for category in sorted(data[year].keys()):
        readme += f"<details>\n<summary><b>{category} ({len(data[year][category])})</b></summary>\n<div markdown=\"1\">\n\n"
        # Sort posts by date descending
        posts = sorted(data[year][category], key=lambda x: x["date"], reverse=True)
        for p in posts:
            readme += f"- [{p['date']}] [{p['title']}]({p['url']})\n"
        readme += "\n</div>\n</details>\n\n"
        
    readme += "</div>\n</details>\n"

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README update completed successfully.")
