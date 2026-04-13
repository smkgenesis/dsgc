# final_v2 Main Suite

This document describes the frozen paper-facing suite selected after the
`final_v2_calibration_pass1` audit run.

The executable protocol is:

- `protocols/final_experiment_v2_main.json`

The headline outputs are:

- `results/final_v2_main_raw.json`
- `results/final_v2_main_summary.json`
- `results/final_v2_main_report.md`

## Fixed Settings

- templates:
  - controls: `budget_control`, `numeric_threshold_control_v2`
  - targets: `opaque_role_target_v2`, `opaque_profile_target_v2`
- methods:
  - `retrieval_only`
  - `dsgc_no_graph`
  - `dsgc`
- encoders:
  - `frozen`
  - `sentence`
- seeds:
  - `0..14`
- total blocks:
  - `20`
- honeypot strength:
  - `medium`

## Per-Template Settings

- `budget_control`:
  - chain depth `2`
  - honeypot count `4`
  - budget multiplier `2.0`
- `numeric_threshold_control_v2`:
  - chain depth `2`
  - honeypot count `4`
  - budget multiplier `2.0`
- `opaque_role_target_v2`:
  - chain depth `3`
  - honeypot count `2`
  - budget multiplier `2.0`
- `opaque_profile_target_v2`:
  - chain depth `3`
  - honeypot count `2`
  - budget multiplier `2.0`

## Role In The Paper

`final_v2_main` is the fixed paper-facing suite. Calibration records remain in
`audit/`, while the reproducible headline evidence for the paper lives under
`results/` and is rerun by `reproduce.sh`.
