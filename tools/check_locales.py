#!/usr/bin/env python3
"""Validate locale JSON files against the English source file."""

import argparse
import json
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\{[^{}\s]+\}")


def find_placeholders(text):
    """Return placeholders such as {count}, {percent}, or {year}."""
    return set(PLACEHOLDER_RE.findall(text))


def load_json(path):
    """Read a JSON file and return either its data or a readable error."""
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


def check_locale(source_strings, translated_strings):
    """Compare one translated locale against en.json."""
    issues = []
    source_keys = set(source_strings)
    translated_keys = set(translated_strings)

    # Keys present in English must exist in every translation.
    for key in sorted(source_keys - translated_keys):
        issues.append(f"missing key: {key}")

    # Extra keys usually mean the translation is stale or has a typo.
    for key in sorted(translated_keys - source_keys):
        issues.append(f"extra key: {key}")

    # Only compare values for keys that exist in both files.
    for key in sorted(source_keys & translated_keys):
        english_value = source_strings[key]
        translated_value = translated_strings[key]

        if translated_value == "":
            issues.append(f"empty value: {key}")

        # Placeholder names must stay unchanged so app formatting still works.
        english_placeholders = find_placeholders(english_value)
        translated_placeholders = find_placeholders(translated_value)
        if english_placeholders != translated_placeholders:
            missing = sorted(english_placeholders - translated_placeholders)
            extra = sorted(translated_placeholders - english_placeholders)
            details = []

            if missing:
                details.append(f"missing {', '.join(missing)}")
            if extra:
                details.append(f"unexpected {', '.join(extra)}")
            issues.append(f"placeholder mismatch: {key} ({'; '.join(details)})")

    return issues


def print_section(name, issues):
    """Print the result for one locale file."""
    print(f"\n{name}")
    print("-" * len(name))
    if not issues:
        print("OK")
        return

    for issue in issues:
        print(f"- {issue}")


def validate(locales_dir):
    """Validate every locale JSON file in the selected directory."""
    if not locales_dir.exists():
        print(f"ERROR: locales directory does not exist: {locales_dir}", file=sys.stderr)
        return 1
    if not locales_dir.is_dir():
        print(f"ERROR: locales path is not a directory: {locales_dir}", file=sys.stderr)
        return 1

    source_path = locales_dir / "en.json"
    source_strings, error = load_json(source_path)
    if error:
        print(f"ERROR: cannot load source locale {source_path}: {error}", file=sys.stderr)
        return 1

    # Check every JSON file except en.json, because en.json is the source of truth.
    locale_files = sorted(path for path in locales_dir.glob("*.json") if path.name != "en.json")
    if not locale_files:
        print(f"ERROR: no locale JSON files found in {locales_dir}", file=sys.stderr)
        return 1

    total_issues = 0
    print(f"Locale validation report for {locales_dir}")
    print(f"Source: {source_path.name} ({len(source_strings)} keys)")

    for locale_path in locale_files:
        translated_strings, error = load_json(locale_path)
        if error:
            issues = [error]
        else:
            issues = check_locale(source_strings, translated_strings)

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
