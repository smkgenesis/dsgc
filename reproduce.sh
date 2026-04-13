#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

.venv/bin/pip install -e .[experiments]

PYTHONPATH=src .venv/bin/python -m experiments.run_final_v2_main
PYTHONPATH=src .venv/bin/python -m experiments.run_final_v3_robustness

echo "Reproduction complete."
echo "See results/final_v2_main_report.md and results/final_v3_robustness_report.md"
