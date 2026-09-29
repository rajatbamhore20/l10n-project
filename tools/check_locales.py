#!/usr/bin/env python3
"""Check translated locale files against locales/en.json."""

import argparse
import json
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\{[^{}\s]+\}")


def load_json(path):
    # Keep this small safety check so bad JSON prints a clean error, not a traceback.
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle), None
    except OSError as exc:
        return None, f"could not read file: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"malformed JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"


def placeholders(text):
    return set(PLACEHOLDER_RE.findall(text))


def main():
    parser = argparse.ArgumentParser(description="Validate locale files against en.json.")
    parser.add_argument("--locales-dir", default="locales", type=Path)
    args = parser.parse_args()

    locales_dir = args.locales_dir
    english, error = load_json(locales_dir / "en.json")
    if error:
        print(f"ERROR: cannot load en.json: {error}", file=sys.stderr)
        return 1

    locale_files = sorted(path for path in locales_dir.glob("*.json") if path.name != "en.json")
    total_issues = 0

    print(f"Locale validation report for {locales_dir}")
    print(f"Source: en.json ({len(english)} keys)")

    for locale_file in locale_files:
        print(f"\n{locale_file.name}")
        print("-" * len(locale_file.name))

        translated, error = load_json(locale_file)
        issues = []

        if error:
            issues.append(error)
        else:
            english_keys = set(english)
            translated_keys = set(translated)

            # 1. Keys that exist in English but are missing from the translation.
            for key in sorted(english_keys - translated_keys):
                issues.append(f"missing key: {key}")

            # 2. Keys that exist in the translation but not in English.
            for key in sorted(translated_keys - english_keys):
                issues.append(f"extra key: {key}")

            # 3. Empty values and placeholder mismatches for shared keys.
            for key in sorted(english_keys & translated_keys):
                if translated[key] == "":
                    issues.append(f"empty value: {key}")

                expected = placeholders(english[key])
                actual = placeholders(translated[key])
                if expected != actual:
                    missing = sorted(expected - actual)
                    extra = sorted(actual - expected)
                    detail_parts = []
                    if missing:
                        detail_parts.append(f"missing {', '.join(missing)}")
                    if extra:
                        detail_parts.append(f"unexpected {', '.join(extra)}")
                    issues.append(f"placeholder mismatch: {key} ({'; '.join(detail_parts)})")

        if issues:
            for issue in issues:
                print(f"- {issue}")
        else:
            print("OK")

        total_issues += len(issues)

    print(f"\nTotal issues: {total_issues}")
    return 1 if total_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
