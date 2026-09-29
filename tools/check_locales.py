#!/usr/bin/env python3
"""Validate locale JSON files against the English source file."""

import argparse
import json
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\{[^{}\s]+\}")


def placeholders(value):
    return set(PLACEHOLDER_RE.findall(value))


def load_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        return None, f"could not read file: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"malformed JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"

    if not isinstance(data, dict):
        return None, "top-level JSON value must be an object"

    non_string_keys = [key for key, value in data.items() if not isinstance(value, str)]
    if non_string_keys:
        keys = ", ".join(sorted(non_string_keys))
        return None, f"all values must be strings; non-string values for: {keys}"

    return data, None


def compare_locale(source, locale_data):
    issues = []
    source_keys = set(source)
    locale_keys = set(locale_data)

    for key in sorted(source_keys - locale_keys):
        issues.append(f"missing key: {key}")

    for key in sorted(locale_keys - source_keys):
        issues.append(f"extra key: {key}")

    for key in sorted(source_keys & locale_keys):
        translated_value = locale_data[key]
        if translated_value == "":
            issues.append(f"empty value: {key}")

        expected = placeholders(source[key])
        actual = placeholders(translated_value)
        if expected != actual:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            details = []
            if missing:
                details.append(f"missing {', '.join(missing)}")
            if extra:
                details.append(f"unexpected {', '.join(extra)}")
            issues.append(f"placeholder mismatch: {key} ({'; '.join(details)})")

    return issues


def print_section(name, issues):
    print(f"\n{name}")
    print("-" * len(name))
    if not issues:
        print("OK")
        return

    for issue in issues:
        print(f"- {issue}")


def validate(locales_dir):
    if not locales_dir.exists():
        print(f"ERROR: locales directory does not exist: {locales_dir}", file=sys.stderr)
        return 1
    if not locales_dir.is_dir():
        print(f"ERROR: locales path is not a directory: {locales_dir}", file=sys.stderr)
        return 1

    source_path = locales_dir / "en.json"
    source, error = load_json(source_path)
    if error:
        print(f"ERROR: cannot load source locale {source_path}: {error}", file=sys.stderr)
        return 1

    locale_files = sorted(path for path in locales_dir.glob("*.json") if path.name != "en.json")
    if not locale_files:
        print(f"ERROR: no locale JSON files found in {locales_dir}", file=sys.stderr)
        return 1

    total_issues = 0
    print(f"Locale validation report for {locales_dir}")
    print(f"Source: {source_path.name} ({len(source)} keys)")

    for locale_path in locale_files:
        locale_data, error = load_json(locale_path)
        if error:
            issues = [error]
        else:
            issues = compare_locale(source, locale_data)

        total_issues += len(issues)
        print_section(locale_path.name, issues)

    print(f"\nTotal issues: {total_issues}")
    return 1 if total_issues else 0


def main():
    parser = argparse.ArgumentParser(description="Validate locale files against en.json.")
    parser.add_argument(
        "--locales-dir",
        default="locales",
        type=Path,
        help="directory containing en.json and translated locale JSON files",
    )
    args = parser.parse_args()
    return validate(args.locales_dir)


if __name__ == "__main__":
    raise SystemExit(main())
