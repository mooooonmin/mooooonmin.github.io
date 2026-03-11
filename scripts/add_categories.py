import os
import glob

posts_dir = r"d:\02.프로젝트\mooooonmin.github.io\_posts"

for filepath in glob.glob(os.path.join(posts_dir, "*.md")):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "\ncategory:" not in content:
        # insert category before date
        if "\ndate:" in content:
            content = content.replace("\ndate:", "\ncategory: 1\ndate:", 1)
        else:
            # fallback: insert right after first ---
            parts = content.split("---", 2)
            if len(parts) >= 3:
                parts[1] = "\ncategory: 1" + parts[1]
                content = "---".join(parts)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
print("카테고리 일괄 추가 완료")
