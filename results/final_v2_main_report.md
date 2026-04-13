# final_v2_main Report

## Fixed Suite

- Controls: budget_control, numeric_threshold_control_v2
- Targets: opaque_role_target_v2, opaque_profile_target_v2
- Methods: retrieval_only, dsgc_no_graph, dsgc
- Encoders: frozen, sentence
- Seeds: 15

## Per Template

| encoder | template | regime | method | prereq_retention | full_chain_retention | answer_acc |
| --- | --- | --- | --- | --- | --- | --- |
| frozen | budget_control | control | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| frozen | numeric_threshold_control_v2 | control | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| frozen | opaque_profile_target_v2 | target | dsgc | 0.9000 +- 0.2070 | 0.8000 +- 0.4140 | 0.8000 +- 0.4140 |
| frozen | opaque_role_target_v2 | target | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| frozen | budget_control | control | dsgc_no_graph | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| frozen | numeric_threshold_control_v2 | control | dsgc_no_graph | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| frozen | opaque_profile_target_v2 | target | dsgc_no_graph | 0.1333 +- 0.2968 | 0.0667 +- 0.2582 | 0.0667 +- 0.2582 |
| frozen | opaque_role_target_v2 | target | dsgc_no_graph | 0.5000 +- 0.0000 | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 |
| frozen | budget_control | control | retrieval_only | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| frozen | numeric_threshold_control_v2 | control | retrieval_only | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| frozen | opaque_profile_target_v2 | target | retrieval_only | 0.1333 +- 0.2968 | 0.0667 +- 0.2582 | 0.0667 +- 0.2582 |
| frozen | opaque_role_target_v2 | target | retrieval_only | 0.5000 +- 0.0000 | 0.0000 +- 0.0000 | 0.0000 +- 0.0000 |
| sentence | budget_control | control | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| sentence | numeric_threshold_control_v2 | control | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| sentence | opaque_profile_target_v2 | target | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| sentence | opaque_role_target_v2 | target | dsgc | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| sentence | budget_control | control | dsgc_no_graph | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| sentence | numeric_threshold_control_v2 | control | dsgc_no_graph | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| sentence | opaque_profile_target_v2 | target | dsgc_no_graph | 0.6667 +- 0.2440 | 0.3333 +- 0.4880 | 0.3333 +- 0.4880 |
| sentence | opaque_role_target_v2 | target | dsgc_no_graph | 0.5667 +- 0.1759 | 0.1333 +- 0.3519 | 0.1333 +- 0.3519 |
| sentence | budget_control | control | retrieval_only | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| sentence | numeric_threshold_control_v2 | control | retrieval_only | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 | 1.0000 +- 0.0000 |
| sentence | opaque_profile_target_v2 | target | retrieval_only | 0.6667 +- 0.2440 | 0.3333 +- 0.4880 | 0.3333 +- 0.4880 |
| sentence | opaque_role_target_v2 | target | retrieval_only | 0.5667 +- 0.1759 | 0.1333 +- 0.3519 | 0.1333 +- 0.3519 |

## By Regime

| encoder | regime | method | full_chain_retention |
| --- | --- | --- | --- |
| frozen | control | dsgc | 1.0000 +- 0.0000 |
| frozen | target | dsgc | 0.9000 +- 0.3051 |
| frozen | control | dsgc_no_graph | 1.0000 +- 0.0000 |
| frozen | target | dsgc_no_graph | 0.0333 +- 0.1826 |
| frozen | control | retrieval_only | 1.0000 +- 0.0000 |
| frozen | target | retrieval_only | 0.0333 +- 0.1826 |
| sentence | control | dsgc | 1.0000 +- 0.0000 |
| sentence | target | dsgc | 1.0000 +- 0.0000 |
| sentence | control | dsgc_no_graph | 1.0000 +- 0.0000 |
| sentence | target | dsgc_no_graph | 0.2333 +- 0.4302 |
| sentence | control | retrieval_only | 1.0000 +- 0.0000 |
| sentence | target | retrieval_only | 0.2333 +- 0.4302 |

## Prediction vs Outcome

- Controls prediction: retrieval_only >= 0.90 and dsgc ~= retrieval_only
  frozen / budget_control: dsgc-retrieval_only=0.0000, dsgc-no_graph=0.0000
  frozen / numeric_threshold_control_v2: dsgc-retrieval_only=0.0000, dsgc-no_graph=0.0000
  sentence / budget_control: dsgc-retrieval_only=0.0000, dsgc-no_graph=0.0000
  sentence / numeric_threshold_control_v2: dsgc-retrieval_only=0.0000, dsgc-no_graph=0.0000
- Targets prediction: dsgc > dsgc_no_graph and dsgc > retrieval_only
  frozen / opaque_profile_target_v2: dsgc-retrieval_only=0.7333, dsgc-no_graph=0.7333
  frozen / opaque_role_target_v2: dsgc-retrieval_only=1.0000, dsgc-no_graph=1.0000
  sentence / opaque_profile_target_v2: dsgc-retrieval_only=0.6667, dsgc-no_graph=0.6667
  sentence / opaque_role_target_v2: dsgc-retrieval_only=0.8667, dsgc-no_graph=0.8667
- Strongest target prediction: opaque_role_target_v2 should remain the cleanest target
- Encoder robustness prediction: opaque_profile_target_v2 should keep a positive DSGC advantage under sentence

## Output Files

- `results/final_v2_main_raw.json`
- `results/final_v2_main_summary.json`
- `results/final_v2_main_report.md`
