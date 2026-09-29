#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "ERROR: Python is required, but neither python3 nor python was found on PATH." >&2
  exit 127
fi

LOCALES_ARG="${1:-locales}"
if [[ "${LOCALES_ARG}" = /* ]]; then
  LOCALES_DIR="${LOCALES_ARG}"
else
  LOCALES_DIR="${REPO_ROOT}/${LOCALES_ARG}"
fi

REPORT_DIR="${REPO_ROOT}/reports"
REPORT_PATH="${REPORT_DIR}/locale-report.txt"
mkdir -p "${REPORT_DIR}"

"${PYTHON_BIN}" - "${LOCALES_DIR}" <<'PY'
import json
import sys
from pathlib import Path

locales_dir = Path(sys.argv[1])
source_path = locales_dir / "en.json"

try:
    with source_path.open(encoding="utf-8") as handle:
        source = json.load(handle)
except Exception as exc:
    raise SystemExit(f"ERROR: cannot count source keys in {source_path}: {exc}")

locale_count = len([path for path in locales_dir.glob("*.json") if path.name != "en.json"])
print(f"Source keys in en.json: {len(source)}")
print(f"Locale files found: {locale_count}")
PY

set +e
"${PYTHON_BIN}" "${REPO_ROOT}/tools/check_locales.py" --locales-dir "${LOCALES_DIR}" | tee "${REPORT_PATH}"
validator_status=${PIPESTATUS[0]}
set -e

echo "Report written to ${REPORT_PATH}"
exit "${validator_status}"
