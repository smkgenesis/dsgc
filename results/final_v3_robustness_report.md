# final_v3_robustness Report

## Top-Line Findings

- `lambda_pi` sensitivity is mild in the selected range. Target gains remain positive at `0.5, 1.0, 2.0`.
- The budget curve confirms a strong mid-budget DSGC advantage and shows retrieval/no-graph catching up only as budget loosens.
- `sliding_window` remains a weak target baseline across the budget sweep.
- Scale robustness is mixed. Controls remain clean at `total_blocks=50`, but frozen target performance drops at scale while sentence-target DSGC remains strong.
- Frozen `opaque_profile_target_v2` failures are traceable to `c1` displacement rather than a hidden code inconsistency.

## Lambda Sweep

| template | encoder | method | lambda_pi | full_chain_retention |
| --- | --- | --- | --- | --- |
| budget_control | frozen | dsgc | 0.5 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc | 1.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc | 2.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc_no_graph | 1.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | retrieval_only | 1.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 0.5 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 1.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 2.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc_no_graph | 1.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | retrieval_only | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 0.5 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 2.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc_no_graph | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | retrieval_only | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 0.5 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 2.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc_no_graph | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | retrieval_only | 1.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | dsgc | 0.5 | 0.6667 +- 0.4880 |
| opaque_profile_target_v2 | frozen | dsgc | 1.0 | 0.8000 +- 0.4140 |
| opaque_profile_target_v2 | frozen | dsgc | 2.0 | 0.8667 +- 0.3519 |
| opaque_profile_target_v2 | frozen | dsgc_no_graph | 1.0 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | frozen | retrieval_only | 1.0 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | sentence | dsgc | 0.5 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc | 1.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc | 2.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc_no_graph | 1.0 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | sentence | retrieval_only | 1.0 | 0.3333 +- 0.4880 |
| opaque_role_target_v2 | frozen | dsgc | 0.5 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc | 1.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc | 2.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc_no_graph | 1.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | retrieval_only | 1.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc | 0.5 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc | 1.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc | 2.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc_no_graph | 1.0 | 0.1333 +- 0.3519 |
| opaque_role_target_v2 | sentence | retrieval_only | 1.0 | 0.1333 +- 0.3519 |

## Budget Curve

| template | encoder | method | budget | full_chain_retention |
| --- | --- | --- | --- | --- |
| budget_control | frozen | dsgc | 1.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc | 1.5 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc | 2.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc | 3.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc | 5.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc_no_graph | 1.0 | 0.4667 +- 0.5164 |
| budget_control | frozen | dsgc_no_graph | 1.5 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc_no_graph | 2.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc_no_graph | 3.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc_no_graph | 5.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | retrieval_only | 1.0 | 0.4667 +- 0.5164 |
| budget_control | frozen | retrieval_only | 1.5 | 1.0000 +- 0.0000 |
| budget_control | frozen | retrieval_only | 2.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | retrieval_only | 3.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | retrieval_only | 5.0 | 1.0000 +- 0.0000 |
| budget_control | frozen | sliding_window | 1.0 | 0.0000 +- 0.0000 |
| budget_control | frozen | sliding_window | 1.5 | 0.0000 +- 0.0000 |
| budget_control | frozen | sliding_window | 2.0 | 0.0667 +- 0.2582 |
| budget_control | frozen | sliding_window | 3.0 | 0.1333 +- 0.3519 |
| budget_control | frozen | sliding_window | 5.0 | 0.2000 +- 0.4140 |
| budget_control | sentence | dsgc | 1.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 1.5 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 2.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 3.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 5.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc_no_graph | 1.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc_no_graph | 1.5 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc_no_graph | 2.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc_no_graph | 3.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc_no_graph | 5.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | retrieval_only | 1.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | retrieval_only | 1.5 | 1.0000 +- 0.0000 |
| budget_control | sentence | retrieval_only | 2.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | retrieval_only | 3.0 | 1.0000 +- 0.0000 |
| budget_control | sentence | retrieval_only | 5.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 1.5 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 2.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 3.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 5.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc_no_graph | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc_no_graph | 1.5 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc_no_graph | 2.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc_no_graph | 3.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc_no_graph | 5.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | retrieval_only | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | retrieval_only | 1.5 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | retrieval_only | 2.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | retrieval_only | 3.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | retrieval_only | 5.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | sliding_window | 1.0 | 0.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | sliding_window | 1.5 | 0.0667 +- 0.2582 |
| numeric_threshold_control_v2 | frozen | sliding_window | 2.0 | 0.0667 +- 0.2582 |
| numeric_threshold_control_v2 | frozen | sliding_window | 3.0 | 0.1333 +- 0.3519 |
| numeric_threshold_control_v2 | frozen | sliding_window | 5.0 | 0.2000 +- 0.4140 |
| numeric_threshold_control_v2 | sentence | dsgc | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 1.5 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 2.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 3.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 5.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc_no_graph | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc_no_graph | 1.5 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc_no_graph | 2.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc_no_graph | 3.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc_no_graph | 5.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | retrieval_only | 1.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | retrieval_only | 1.5 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | retrieval_only | 2.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | retrieval_only | 3.0 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | retrieval_only | 5.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | dsgc | 1.0 | 0.5333 +- 0.5164 |
| opaque_profile_target_v2 | frozen | dsgc | 1.5 | 0.4000 +- 0.5071 |
| opaque_profile_target_v2 | frozen | dsgc | 2.0 | 0.8000 +- 0.4140 |
| opaque_profile_target_v2 | frozen | dsgc | 3.0 | 0.9333 +- 0.2582 |
| opaque_profile_target_v2 | frozen | dsgc | 5.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | dsgc_no_graph | 1.0 | 0.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | dsgc_no_graph | 1.5 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | frozen | dsgc_no_graph | 2.0 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | frozen | dsgc_no_graph | 3.0 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | frozen | dsgc_no_graph | 5.0 | 0.6000 +- 0.5071 |
| opaque_profile_target_v2 | frozen | retrieval_only | 1.0 | 0.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | retrieval_only | 1.5 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | frozen | retrieval_only | 2.0 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | frozen | retrieval_only | 3.0 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | frozen | retrieval_only | 5.0 | 0.6000 +- 0.5071 |
| opaque_profile_target_v2 | frozen | sliding_window | 1.0 | 0.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | sliding_window | 1.5 | 0.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | sliding_window | 2.0 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | frozen | sliding_window | 3.0 | 0.1333 +- 0.3519 |
| opaque_profile_target_v2 | frozen | sliding_window | 5.0 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | sentence | dsgc | 1.0 | 0.2667 +- 0.4577 |
| opaque_profile_target_v2 | sentence | dsgc | 1.5 | 0.6667 +- 0.4880 |
| opaque_profile_target_v2 | sentence | dsgc | 2.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc | 3.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc | 5.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc_no_graph | 1.0 | 0.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc_no_graph | 1.5 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | sentence | dsgc_no_graph | 2.0 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | sentence | dsgc_no_graph | 3.0 | 0.2667 +- 0.4577 |
| opaque_profile_target_v2 | sentence | dsgc_no_graph | 5.0 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | retrieval_only | 1.0 | 0.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | retrieval_only | 1.5 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | sentence | retrieval_only | 2.0 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | sentence | retrieval_only | 3.0 | 0.2667 +- 0.4577 |
| opaque_profile_target_v2 | sentence | retrieval_only | 5.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc | 1.0 | 0.4000 +- 0.5071 |
| opaque_role_target_v2 | frozen | dsgc | 1.5 | 0.8667 +- 0.3519 |
| opaque_role_target_v2 | frozen | dsgc | 2.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc | 3.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc | 5.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc_no_graph | 1.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc_no_graph | 1.5 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc_no_graph | 2.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc_no_graph | 3.0 | 0.4000 +- 0.5071 |
| opaque_role_target_v2 | frozen | dsgc_no_graph | 5.0 | 0.2667 +- 0.4577 |
| opaque_role_target_v2 | frozen | retrieval_only | 1.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | retrieval_only | 1.5 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | retrieval_only | 2.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | retrieval_only | 3.0 | 0.4000 +- 0.5071 |
| opaque_role_target_v2 | frozen | retrieval_only | 5.0 | 0.2667 +- 0.4577 |
| opaque_role_target_v2 | frozen | sliding_window | 1.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | sliding_window | 1.5 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | sliding_window | 2.0 | 0.0667 +- 0.2582 |
| opaque_role_target_v2 | frozen | sliding_window | 3.0 | 0.1333 +- 0.3519 |
| opaque_role_target_v2 | frozen | sliding_window | 5.0 | 0.2000 +- 0.4140 |
| opaque_role_target_v2 | sentence | dsgc | 1.0 | 0.7333 +- 0.4577 |
| opaque_role_target_v2 | sentence | dsgc | 1.5 | 0.8000 +- 0.4140 |
| opaque_role_target_v2 | sentence | dsgc | 2.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc | 3.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc | 5.0 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc_no_graph | 1.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc_no_graph | 1.5 | 0.0667 +- 0.2582 |
| opaque_role_target_v2 | sentence | dsgc_no_graph | 2.0 | 0.1333 +- 0.3519 |
| opaque_role_target_v2 | sentence | dsgc_no_graph | 3.0 | 0.2667 +- 0.4577 |
| opaque_role_target_v2 | sentence | dsgc_no_graph | 5.0 | 0.4667 +- 0.5164 |
| opaque_role_target_v2 | sentence | retrieval_only | 1.0 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | retrieval_only | 1.5 | 0.0667 +- 0.2582 |
| opaque_role_target_v2 | sentence | retrieval_only | 2.0 | 0.1333 +- 0.3519 |
| opaque_role_target_v2 | sentence | retrieval_only | 3.0 | 0.2667 +- 0.4577 |
| opaque_role_target_v2 | sentence | retrieval_only | 5.0 | 0.4667 +- 0.5164 |

## Scale Robustness

| template | encoder | method | total_blocks | full_chain_retention |
| --- | --- | --- | --- | --- |
| budget_control | frozen | dsgc | 20 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc | 50 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc_no_graph | 20 | 1.0000 +- 0.0000 |
| budget_control | frozen | dsgc_no_graph | 50 | 1.0000 +- 0.0000 |
| budget_control | frozen | retrieval_only | 20 | 1.0000 +- 0.0000 |
| budget_control | frozen | retrieval_only | 50 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 20 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc | 50 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc_no_graph | 20 | 1.0000 +- 0.0000 |
| budget_control | sentence | dsgc_no_graph | 50 | 1.0000 +- 0.0000 |
| budget_control | sentence | retrieval_only | 20 | 1.0000 +- 0.0000 |
| budget_control | sentence | retrieval_only | 50 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 20 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc | 50 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc_no_graph | 20 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | dsgc_no_graph | 50 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | retrieval_only | 20 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | frozen | retrieval_only | 50 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 20 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc | 50 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc_no_graph | 20 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | dsgc_no_graph | 50 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | retrieval_only | 20 | 1.0000 +- 0.0000 |
| numeric_threshold_control_v2 | sentence | retrieval_only | 50 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | dsgc | 20 | 0.8000 +- 0.4140 |
| opaque_profile_target_v2 | frozen | dsgc | 50 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | frozen | dsgc_no_graph | 20 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | frozen | dsgc_no_graph | 50 | 0.0000 +- 0.0000 |
| opaque_profile_target_v2 | frozen | retrieval_only | 20 | 0.0667 +- 0.2582 |
| opaque_profile_target_v2 | frozen | retrieval_only | 50 | 0.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc | 20 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc | 50 | 1.0000 +- 0.0000 |
| opaque_profile_target_v2 | sentence | dsgc_no_graph | 20 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | sentence | dsgc_no_graph | 50 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | sentence | retrieval_only | 20 | 0.3333 +- 0.4880 |
| opaque_profile_target_v2 | sentence | retrieval_only | 50 | 0.3333 +- 0.4880 |
| opaque_role_target_v2 | frozen | dsgc | 20 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc | 50 | 0.7333 +- 0.4577 |
| opaque_role_target_v2 | frozen | dsgc_no_graph | 20 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | dsgc_no_graph | 50 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | retrieval_only | 20 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | frozen | retrieval_only | 50 | 0.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc | 20 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc | 50 | 1.0000 +- 0.0000 |
| opaque_role_target_v2 | sentence | dsgc_no_graph | 20 | 0.1333 +- 0.3519 |
| opaque_role_target_v2 | sentence | dsgc_no_graph | 50 | 0.1333 +- 0.3519 |
| opaque_role_target_v2 | sentence | retrieval_only | 20 | 0.1333 +- 0.3519 |
| opaque_role_target_v2 | sentence | retrieval_only | 50 | 0.1333 +- 0.3519 |

## Opaque Profile Frozen Failures

| seed | chain ranks | propagation | top non-chain | displaced |
| --- | --- | --- | --- | --- |
| 3 | `{'c1': 10, 'c2': 1, 'c3': 2}` | `{'c1': 0.022991, 'c2': 0.095935, 'c3': 0.0}` | `h1` (0.088885) | `['c1']` |
| 8 | `{'c1': 6, 'c2': 1, 'c3': 2}` | `{'c1': 0.032382, 'c2': 0.092593, 'c3': 0.0}` | `f9` (0.072649) | `['c1']` |
| 14 | `{'c1': 6, 'c2': 1, 'c3': 2}` | `{'c1': 0.02656, 'c2': 0.110828, 'c3': 0.0}` | `f3` (0.096421) | `['c1']` |

## Output Files

- `results/final_v3_robustness_raw.json`
- `results/final_v3_robustness_summary.json`
- `results/final_v3_robustness_report.md`
