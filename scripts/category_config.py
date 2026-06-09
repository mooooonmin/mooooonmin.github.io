import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CATEGORY_DATA_PATH = BASE_DIR / "_data" / "categories.json"


def load_category_config():
    with CATEGORY_DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    order = data.get("order", [])
    labels = {name: name.upper() for name in order}
    labels.update(data.get("labels", {}))
    return order, labels
