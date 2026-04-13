# final_v2 Calibration Pass 1

Run command:

- `PYTHONPATH=src .venv/bin/python -m experiments.run_final_v2_calibration --protocol-id final_v2_calibration_pass1 --raw-output audit/results/final_v2_calibration_pass1_raw.json --summary-output audit/results/final_v2_calibration_pass1_summary.json --seed-count 6 --total-blocks 20 --budget-multipliers 1.0 1.5 2.0 3.0 5.0 --chain-depths 2 3 --honeypot-counts 2 4 6 --honeypot-strength medium`

## Top-Line Decisions

- Keep as main-suite control candidates: `budget_control`, `numeric_threshold_control_v2`.
- Do not prioritize `permission_control_v2` as a main control after this pass.
- Keep as main-suite target candidates: `opaque_role_target_v2`, `opaque_profile_target_v2`.
- Prefer `chain_depth=3` for target templates. The strongest graph signal is concentrated there.
- Prefer a mid-budget regime around `budget_multiplier=2.0`. It preserves a large DSGC gap without immediate retrieval saturation.

## Selected Control Candidates

| template | depth | honeypots | budget | frozen retrieval | sentence retrieval | max |dsgc-retrieval| |
| --- | --- | --- | --- | --- | --- | --- |
| budget_control | 2 | 4 | 2.0 | 1.0000 | 1.0000 | 0.0000 |
| numeric_threshold_control_v2 | 2 | 4 | 2.0 | 1.0000 | 1.0000 | 0.0000 |

## Selected Target Candidates

| template | depth | honeypots | budget | frozen retrieval | frozen dsgc | sentence retrieval | sentence dsgc | min dsgc gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| opaque_role_target_v2 | 3 | 2 | 2.0 | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| opaque_profile_target_v2 | 3 | 2 | 2.0 | 0.0000 | 0.8333 | 0.3333 | 1.0000 | 0.6667 |

## Notable Findings

- `budget_control` and `numeric_threshold_control_v2` behave like real controls under both encoders in the selected regime.
- `opaque_role_target_v2` is the cleanest target. At `depth=3, honeypots=2, budget=2.0`, retrieval-only and no-graph are both `0.0000` while DSGC is `1.0000` under both encoders.
- `opaque_profile_target_v2` now survives the sentence encoder. At `depth=3, honeypots=2, budget=2.0`, frozen gives `0.0000 -> 0.8333` and sentence gives `0.3333 -> 1.0000` for retrieval-only to DSGC.
- Depth matters. The strongest robust cross-encoder target settings are concentrated at `chain_depth=3` rather than `2`.
- High budgets such as `5.0` begin to move some target settings toward saturation; `2.0` is a better main-suite candidate.

## Representative Failure Diagnostics

| template | encoder | depth | honeypots | budget | chain ranks | top non-chain | displaced |
| --- | --- | --- | --- | --- | --- | --- | --- |
| opaque_role_target_v2 | frozen | 2 | 2 | 1.0 | `{'c1': 1, 'c2': 3}` | `f12` | `['c2']` |
| opaque_role_target_v2 | frozen | 2 | 4 | 1.0 | `{'c1': 1, 'c2': 4}` | `h4` | `['c2']` |
| opaque_role_target_v2 | frozen | 2 | 6 | 1.0 | `{'c1': 2, 'c2': 6}` | `h6` | `['c2']` |
| opaque_role_target_v2 | frozen | 3 | 2 | 1.0 | `{'c1': 1, 'c2': 18, 'c3': 3}` | `f12` | `['c2', 'c3']` |
| opaque_role_target_v2 | frozen | 3 | 4 | 1.0 | `{'c1': 1, 'c2': 17, 'c3': 4}` | `h4` | `['c2', 'c3']` |
| opaque_role_target_v2 | frozen | 3 | 6 | 1.0 | `{'c1': 1, 'c2': 16, 'c3': 6}` | `h6` | `['c2', 'c3']` |
| opaque_role_target_v2 | frozen | 2 | 2 | 1.5 | `{'c1': 1, 'c2': 4}` | `h2` | `['c2']` |
| opaque_role_target_v2 | frozen | 2 | 4 | 1.5 | `{'c1': 1, 'c2': 4}` | `h4` | `['c2']` |

## Output Files

- `audit/results/final_v2_calibration_pass1_raw.json`
- `audit/results/final_v2_calibration_pass1_summary.json`
- `audit/results/final_v2_calibration_pass1_report.md`
