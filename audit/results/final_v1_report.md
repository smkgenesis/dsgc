# final_v1 Report

## Scope

This report covers the preregistered four-view suite:

1. Template-stratified comparison
2. Graph ablation
3. Pooled comparison
4. Encoder sensitivity

## Experiment 1: Template-Stratified

| template | regime | method | prereq_retention | full_chain_retention | answer_acc | failures |
| --- | --- | --- | --- | --- | --- | --- |
| budget_control | control | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 0 |
| opaque_profile_target | target | dsgc | 1.0000 +- 0.0000 | 0.4000 +- 0.4983 | 0.4000 +- 0.4983 | 18 |
| opaque_role_target | target | dsgc | 1.0000 +- 0.0000 | 0.1333 +- 0.3457 | 0.1333 +- 0.3457 | 26 |
| permission_control | control | dsgc | 1.0000 +- 0.0000 | 0.4000 +- 0.4983 | 0.4000 +- 0.4983 | 18 |
| budget_control | control | dsgc_no_graph | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 0 |
| opaque_profile_target | target | dsgc_no_graph | 0.1333 +- 0.3457 | 0.1333 +- 0.3457 | 0.1333 +- 0.3457 | 26 |
| opaque_role_target | target | dsgc_no_graph | 0.9333 +- 0.2537 | 0.0667 +- 0.2537 | 0.0667 +- 0.2537 | 28 |
| permission_control | control | dsgc_no_graph | 1.0000 +- 0.0000 | 0.4000 +- 0.4983 | 0.4000 +- 0.4983 | 18 |
| budget_control | control | retrieval_only | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 0 |
| opaque_profile_target | target | retrieval_only | 0.1333 +- 0.3457 | 0.1333 +- 0.3457 | 0.1333 +- 0.3457 | 26 |
| opaque_role_target | target | retrieval_only | 0.9333 +- 0.2537 | 0.0667 +- 0.2537 | 0.0667 +- 0.2537 | 28 |
| permission_control | control | retrieval_only | 1.0000 +- 0.0000 | 0.4000 +- 0.4983 | 0.4000 +- 0.4983 | 18 |
| budget_control | control | sliding_window | 0.3000 +- 0.4661 | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 | 30 |
| opaque_profile_target | target | sliding_window | 0.2000 +- 0.4068 | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 | 30 |
| opaque_role_target | target | sliding_window | 0.1000 +- 0.3051 | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 | 30 |
| permission_control | control | sliding_window | 0.1333 +- 0.3457 | 0.0333 +- 0.1826 | 0.0333 +- 0.1826 | 29 |

## Experiment 2: Graph Ablation

| template | retrieval_only | dsgc_no_graph | dsgc | dsgc-retrieval | dsgc-no_graph |
| --- | --- | --- | --- | --- | --- |
| opaque_profile_target | 0.1333 | 0.1333 | 0.4000 | 0.2667 | 0.2667 |
| opaque_role_target | 0.0667 | 0.0667 | 0.1333 | 0.0666 | 0.0666 |

## Experiment 3: Pooled Comparison

### Overall

| method | prereq_retention | full_chain_retention | answer_acc |
| --- | --- | --- | --- |
| dsgc | 1.0000 +- 0.0000 | 0.4833 +- 0.5018 | 0.4833 +- 0.5018 |
| dsgc_no_graph | 0.7667 +- 0.4247 | 0.4000 +- 0.4920 | 0.4000 +- 0.4920 |
| retrieval_only | 0.7667 +- 0.4247 | 0.4000 +- 0.4920 | 0.4000 +- 0.4920 |
| sliding_window | 0.1833 +- 0.3886 | 0.0083 +- 0.0913 | 0.0083 +- 0.0913 |

### By Regime

| regime | method | prereq_retention | full_chain_retention | answer_acc |
| --- | --- | --- | --- | --- |
| control | dsgc | 1.0000 +- 0.0000 | 0.7000 +- 0.4621 | 0.7000 +- 0.4621 |
| target | dsgc | 1.0000 +- 0.0000 | 0.2667 +- 0.4459 | 0.2667 +- 0.4459 |
| control | dsgc_no_graph | 1.0000 +- 0.0000 | 0.7000 +- 0.4621 | 0.7000 +- 0.4621 |
| target | dsgc_no_graph | 0.5333 +- 0.5031 | 0.1000 +- 0.3025 | 0.1000 +- 0.3025 |
| control | retrieval_only | 1.0000 +- 0.0000 | 0.7000 +- 0.4621 | 0.7000 +- 0.4621 |
| target | retrieval_only | 0.5333 +- 0.5031 | 0.1000 +- 0.3025 | 0.1000 +- 0.3025 |
| control | sliding_window | 0.2167 +- 0.4155 | 0.0167 +- 0.1291 | 0.0167 +- 0.1291 |
| target | sliding_window | 0.1500 +- 0.3601 | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 |

## Experiment 4: Encoder Sensitivity

| template | regime | encoder | method | full_chain_retention | answer_acc |
| --- | --- | --- | --- | --- | --- |
| budget_control | control | frozen | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| opaque_profile_target | target | frozen | dsgc | 0.4000 +- 0.4983 | 0.4000 +- 0.4983 |
| opaque_role_target | target | frozen | dsgc | 0.1333 +- 0.3457 | 0.1333 +- 0.3457 |
| permission_control | control | frozen | dsgc | 0.4000 +- 0.4983 | 0.4000 +- 0.4983 |
| budget_control | control | frozen | dsgc_no_graph | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| opaque_profile_target | target | frozen | dsgc_no_graph | 0.1333 +- 0.3457 | 0.1333 +- 0.3457 |
| opaque_role_target | target | frozen | dsgc_no_graph | 0.0667 +- 0.2537 | 0.0667 +- 0.2537 |
| permission_control | control | frozen | dsgc_no_graph | 0.4000 +- 0.4983 | 0.4000 +- 0.4983 |
| budget_control | control | frozen | retrieval_only | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| opaque_profile_target | target | frozen | retrieval_only | 0.1333 +- 0.3457 | 0.1333 +- 0.3457 |
| opaque_role_target | target | frozen | retrieval_only | 0.0667 +- 0.2537 | 0.0667 +- 0.2537 |
| permission_control | control | frozen | retrieval_only | 0.4000 +- 0.4983 | 0.4000 +- 0.4983 |
| budget_control | control | sentence | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| opaque_profile_target | target | sentence | dsgc | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 |
| opaque_role_target | target | sentence | dsgc | 0.2667 +- 0.4498 | 0.2667 +- 0.4498 |
| permission_control | control | sentence | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| budget_control | control | sentence | dsgc_no_graph | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| opaque_profile_target | target | sentence | dsgc_no_graph | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 |
| opaque_role_target | target | sentence | dsgc_no_graph | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 |
| permission_control | control | sentence | dsgc_no_graph | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| budget_control | control | sentence | retrieval_only | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| opaque_profile_target | target | sentence | retrieval_only | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 |
| opaque_role_target | target | sentence | retrieval_only | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 |
| permission_control | control | sentence | retrieval_only | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |

## Prediction vs Outcome

- Control prediction: retrieval_only ~= dsgc_no_graph ~= dsgc; sliding_window weaker
  outcome: dsgc-retrieval_only=0.0000, dsgc-no_graph=0.0000, dsgc-sliding_window=0.6833
- Target prediction: dsgc > retrieval_only ~= dsgc_no_graph; sliding_window weakest
  outcome: dsgc-retrieval_only=0.1667, dsgc-no_graph=0.1667, dsgc-sliding_window=0.2667
- Graph ablation prediction: removing propagation removes most or all target-template gain
  opaque_profile_target: dsgc-retrieval_only=0.2667, dsgc-no_graph=0.2667
  opaque_role_target: dsgc-retrieval_only=0.0666, dsgc-no_graph=0.0666
- Encoder sensitivity prediction: true structural targets retain a DSGC advantage under stronger encoders
  opaque_role_target (frozen): dsgc-retrieval_only=0.0666, dsgc-no_graph=0.0666
  opaque_role_target (sentence): dsgc-retrieval_only=0.2667, dsgc-no_graph=0.2667
  opaque_profile_target (frozen): dsgc-retrieval_only=0.2667, dsgc-no_graph=0.2667
  opaque_profile_target (sentence): dsgc-retrieval_only=0.0000, dsgc-no_graph=0.0000

## Answer Accuracy Diagnostic

- Frozen runs answer/full-chain disagreement count: 0 over 480 runs.
- Encoder-sensitivity runs answer/full-chain disagreement count: 0 over 720 runs.
- Frozen equivalence flag: True
- Encoder-sensitivity equivalence flag: True

## Failure Analysis

- The encoder-sensitivity prediction is only partially supported. The following target templates lose the DSGC advantage under the stronger encoder:
  - opaque_profile_target: retrieval_only=0.0000, dsgc=0.0000, dsgc-retrieval_only=0.0000
- This means the current target family is not uniformly structural under the stronger encoder and should be discussed template-by-template in the paper.

## Output Files

- `results/final_v1_template_stratified_raw.json`
- `results/final_v1_template_stratified_summary.json`
- `results/final_v1_graph_ablation_raw.json`
- `results/final_v1_graph_ablation_summary.json`
- `results/final_v1_encoder_sensitivity_raw.json`
- `results/final_v1_encoder_sensitivity_summary.json`
- `results/final_v1_report.md`
