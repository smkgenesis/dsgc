# DSGC

This repository is the public artifact for **Dependency-aware Semantic Garbage
Collection (DSGC)**.

It exposes the narrow code and data needed to reproduce the paper-facing
results:

- the final benchmark implementation
- the fixed protocols used in the paper
- the exact experiment runners used for the headline results
- the final result files cited in the manuscript
- the audit trail from `final_v1` through calibration to the frozen main suite

The public `src/` tree is intentionally compact. Shared policy interfaces live
at the source root, while the paper-facing implementation is concentrated in:

- `src/benchmarking/`
- `src/baselines/`
- `src/experiments/`
- `src/core/`

At the repository root, the public artifact is organized into:

- `src/` for executable code
- `protocols/` for frozen paper-facing experiment definitions
- `results/` for headline outputs
- `docs/` for runbooks and release metadata
- `audit/` for redesign history and non-headline records
- `paper/` for the manuscript snapshot

## Quick Start

From the repository root:

```bash
bash reproduce.sh
```

This script creates a local virtual environment if needed, installs the
project, and reruns the final paper-facing experiments:

- `final_v2_main`
- `final_v3_robustness`

## What To Cite

The main experimental evidence for the paper is:

- `results/final_v2_main_summary.json`
- `results/final_v2_main_report.md`
- `results/final_v3_robustness_summary.json`
- `results/final_v3_robustness_report.md`

Citation metadata for software archiving is provided in:

- `CITATION.cff`
- `.zenodo.json`

## Core Source Files

- `src/benchmarking/benchmark_v2.py`
  Final benchmark generator with the selected control/target families.
- `src/benchmarking/policy.py`
  Minimal DSGC policy with one-hop propagation and debug instrumentation.
- `src/baselines/retrieval_only.py`
  Retrieval-only baseline with matching diagnostic hooks.
- `src/baselines/sliding_window.py`
  Sliding-window baseline used in the robustness pack.
- `src/experiments/run_final_v2_main.py`
  Fixed main-suite runner.
- `src/experiments/run_final_v3_robustness.py`
  Final robustness-pack runner.

## Protocols

- `protocols/final_experiment_v2_main.json`
- `protocols/final_experiment_v3_robustness.json`

## Audit Trail

The repository also includes the records that justify the redesign path:

- `audit/results/final_v1_report.md`
- `audit/results/final_v2_calibration_pass1_report.md`
- `audit/docs/final_v1_postmortem.md`
- `audit/docs/final_v2_design.md`
- `audit/protocols/final_experiment_v1.json`
- `audit/protocols/final_experiment_v2_draft.json`

## Runbook And Manifest

See:

- `docs/RUNBOOK.md`
- `docs/RESULT_MANIFEST.json`

## Scope Boundary

This artifact is not a general agent-memory framework. It is a reproducible
research codebase for a narrow claim:

> dependency-aware retention outperforms similarity-only retention when the
> answer depends on structurally necessary but semantically indirect
> prerequisites under a fixed prompt budget

## Paper

The manuscript snapshot lives in:

- `paper/main.tex`
- `paper/main.pdf`

Build instructions:

```bash
cd paper
make pdf
```
