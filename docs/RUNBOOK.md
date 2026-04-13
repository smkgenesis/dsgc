# Runbook

This document lists the exact commands used for the paper-facing experiments.

## Environment

Recommended setup:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .[experiments]
```

## final_v2 Main Suite

```bash
PYTHONPATH=src .venv/bin/python -m experiments.run_final_v2_main
```

Expected outputs:

- `results/final_v2_main_raw.json`
- `results/final_v2_main_summary.json`
- `results/final_v2_main_report.md`

## final_v3 Robustness Pack

```bash
PYTHONPATH=src .venv/bin/python -m experiments.run_final_v3_robustness
```

Expected outputs:

- `results/final_v3_robustness_raw.json`
- `results/final_v3_robustness_summary.json`
- `results/final_v3_robustness_report.md`

## Historical Audit Trail

The public bundle also ships the historical redesign records referenced by the
paper:

- `audit/results/final_v1_report.md`
- `audit/results/final_v2_calibration_pass1_report.md`
- `audit/docs/final_v1_postmortem.md`
- `audit/docs/final_v2_design.md`
- `audit/protocols/final_experiment_v1.json`
- `audit/protocols/final_experiment_v2_draft.json`

## Notes

- The executable paper-facing runs remain `final_v2_main` and
  `final_v3_robustness`.
- The historical records are included for transparency and auditability rather
  than as additional headline experiments.
