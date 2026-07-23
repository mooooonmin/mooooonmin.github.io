from collections.abc import Mapping
from copy import deepcopy

import yaml


class FrontMatterError(ValueError):
    pass


class FrontMatterLoader(yaml.SafeLoader):
    """Safe YAML loader that keeps date-like scalars as strings."""


FrontMatterLoader.yaml_implicit_resolvers = deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)
for first_character, resolvers in FrontMatterLoader.yaml_implicit_resolvers.items():
    FrontMatterLoader.yaml_implicit_resolvers[first_character] = [
        (tag, pattern)
        for tag, pattern in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]


def split_front_matter(text):
    normalized = text.lstrip("\ufeff")
    lines = normalized.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return None, normalized

    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.rstrip("\r\n") in {"---", "..."}
        ),
        None,
    )
    if closing_index is None:
        return None, normalized

    front_matter = "".join(lines[1:closing_index]).strip("\r\n").splitlines()
    body = "".join(lines[closing_index + 1 :]).lstrip("\r\n")
    return front_matter, body


def parse_yaml_mapping(text):
    try:
        values = yaml.load(text, Loader=FrontMatterLoader)
    except yaml.YAMLError as error:
        raise FrontMatterError(f"invalid YAML: {error}") from error

    if values is None:
        return {}
    if not isinstance(values, Mapping):
        raise FrontMatterError("YAML metadata must be a mapping")
    return dict(values)


def parse_front_matter(lines):
    return parse_yaml_mapping("\n".join(lines or []))


def read_front_matter(text):
    lines, body = split_front_matter(text)
    return parse_front_matter(lines), body


def parse_inline_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if item is not None]
    if not isinstance(value, str):
        return []

    value = value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        return []
    parsed = yaml.load(value, Loader=FrontMatterLoader)
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if item is not None]
