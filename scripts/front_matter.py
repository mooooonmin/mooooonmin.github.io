def split_front_matter(text):
    normalized = text.lstrip("\ufeff")
    if not normalized.startswith("---"):
        return None, normalized

    parts = normalized.split("---", 2)
    if len(parts) < 3:
        return None, normalized

    return parts[1].strip("\r\n").splitlines(), parts[2].lstrip("\r\n")


def parse_front_matter(lines):
    values = {}
    for line in lines or []:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def read_front_matter(text):
    lines, body = split_front_matter(text)
    return parse_front_matter(lines), body


def parse_inline_list(value):
    value = value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        return []
    return [
        item.strip().strip('"').strip("'")
        for item in value[1:-1].split(",")
        if item.strip()
    ]
