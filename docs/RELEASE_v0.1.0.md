# DSGC v0.1.0

Initial public artifact release for the DSGC paper.

## Included in this release

- Final public code under `src/`
- Frozen paper-facing protocols under `protocols/`
- Headline result files under `results/`
- Redesign and calibration audit trail under `audit/`
- Manuscript snapshot under `paper/`
- Citation and archiving metadata in `CITATION.cff` and `.zenodo.json`

## Reproduction entrypoints

- `bash reproduce.sh`
- `python -m experiments.run_final_v2_main`
- `python -m experiments.run_final_v3_robustness`

## Main artifact files

- `paper/main.pdf`
- `paper/main.tex`
- `results/final_v2_main_summary.json`
- `results/final_v3_robustness_summary.json`

## Scope

This repository is a paper artifact for a narrow claim about dependency-aware
retention under fixed prompt budgets. It is not presented as a general-purpose
agent memory framework.
