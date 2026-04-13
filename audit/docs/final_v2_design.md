# final_v2 Design

This document defines the redesign target for the next paper-facing phase
after `final_v1`.

`final_v2` is not an in-place patch. It is a new benchmark and protocol
version motivated by the observed `final_v1` failures.

Current implementation entrypoint for the calibration stage:

- `PYTHONPATH=src python3 -m experiments.run_final_v2_calibration`

Completed repository calibration record so far:

- `audit/results/final_v2_calibration_pass1_summary.json`
- `audit/results/final_v2_calibration_pass1_report.md`

The fixed suite selected from that calibration is:

- [`../../docs/final_v2_main_suite.md`](../../docs/final_v2_main_suite.md)
- [`../../protocols/final_experiment_v2_main.json`](../../protocols/final_experiment_v2_main.json)
- `../../results/final_v2_main_summary.json`
- `../../results/final_v2_main_report.md`

## Core Position

`final_v2` should be split into two stages:

1. calibration
2. paper-facing main suite

The calibration stage exists to identify a defensible operating regime.
The paper-facing main suite exists to test a fixed preregistered hypothesis
inside that regime.

## Why final_v2 Exists

`final_v1` showed a real one-hop signal, but it left five unresolved issues:

1. one control template was not a clean control
2. the budget grid was too tight
3. target-template behavior under a stronger encoder was inconsistent
4. depth-2 chains were too coarse
5. failure diagnostics were too weak

`final_v2` is designed specifically to resolve those issues.

## final_v2 Design Principles

1. Control templates must be retrieval-friendly in practice, not only by
   intention.
2. Target templates must remain structurally indirect under both `frozen` and
   `sentence` encoders, or else be labeled as encoder-dependent targets.
3. The benchmark must expose an operating curve, not a single knife-edge
   budget point.
4. Failure analysis must identify which block lost, why it lost, and which
   distractor displaced it.
5. Calibration and headline experiments must not be conflated.

## Stage 1: Calibration

Calibration is exploratory by design, but it must still be committed in the
repository and not silently rewritten after inspection.

Calibration goals:

1. verify which templates qualify as controls
2. verify which templates qualify as structural targets
3. locate the DSGC operating range across budget
4. choose a depth and honeypot regime where the mechanism is visible and not
   saturated

Calibration outputs should not be used as headline paper tables.

### Calibration axes

- templates:
  - candidate controls
  - candidate targets
- budget multipliers:
  - `1.0, 1.5, 2.0, 3.0, 5.0`
- chain depths:
  - `2, 3`
- honeypot counts:
  - `2, 4, 6`
- total blocks:
  - `20, 32`
- encoders:
  - `frozen`
  - `sentence`
- methods:
  - `retrieval_only`
  - `dsgc_no_graph`
  - `dsgc`

### Calibration acceptance criteria

A control template passes calibration only if:

- `retrieval_only` full-chain retention is at least `0.90` in the intended
  operating regime
- `dsgc - retrieval_only` is small enough that the control still behaves like
  a retrieval-friendly case

A target template passes calibration only if:

- `dsgc > dsgc_no_graph` in the intended operating regime
- the gain is stable across multiple seeds
- the template does not collapse into a lexical artifact under the stronger
  encoder unless it is explicitly labeled as encoder-dependent

## Stage 2: final_v2 Main Suite

The paper-facing suite should be small.

It should use only the calibrated subset chosen in Stage 1.

Recommended shape:

- control templates:
  - `budget_control`
  - one new numeric or lexical control that genuinely passes calibration
- target templates:
  - `opaque_role_target_v2`
  - `opaque_profile_target_v2` only if it passes encoder calibration
- methods:
  - `retrieval_only`
  - `dsgc_no_graph`
  - `dsgc`
- chain depth:
  - one calibrated value from `{2, 3}`
- budget multipliers:
  - a calibrated subset that spans the DSGC operating range
- honeypot counts:
  - one or two calibrated settings
- seeds:
  - `15`

`sliding_window` may remain in calibration and appendix reporting, but it does
not need to dominate the main mechanism comparison.

## Template Redesign Requirements

### Controls

`permission_control` should not remain a paper-facing control in its current
form.

Two acceptable paths:

1. weaken its honeypots until retrieval-only succeeds reliably
2. replace it with a new control template and demote the old one

Recommended new control family:

- a simple numeric threshold or lookup task
- strong lexical overlap with the query
- honeypots that do not match the query as strongly as the true chain blocks

### Targets

The target family should be revised to separate two ideas:

1. structurally indirect targets
2. encoder-dependent opaque-token targets

`opaque_*_v2` should use identifiers that remain distinguishable under the
sentence encoder.

Examples of acceptable naming patterns:

- `role_7e3f`
- `clearance_alpha_29`
- `profile_relay_delta_12`

The goal is not realism. The goal is controlled distinguishability across
encoders.

## Diagnostic Metrics

`final_v2` should retain the `final_v1` metrics and add mechanism-facing
diagnostics.

Required additional diagnostics:

- `chain_block_ranks`
- `chain_block_scores`
- `chain_block_propagation`
- `top_non_chain_score`
- `top_non_chain_id`
- `displaced_chain_blocks`
- `selected_honeypot_count`

Recommended raw schema shape:

```json
{
  "chain_block_ranks": {"c1": 3, "c2": 1},
  "chain_block_scores": {"c1": 0.142, "c2": 0.201},
  "chain_block_propagation": {"c1": 0.120, "c2": 0.000},
  "top_non_chain_score": 0.155,
  "top_non_chain_id": "h2",
  "displaced_chain_blocks": ["c1"],
  "selected_honeypot_count": 2
}
```

These diagnostics are needed to distinguish:

- budget failure
- ranking failure
- propagation failure
- template contamination

## Honeypot Parameterization

`final_v2` should not rely on a single fixed distractor recipe.

Each template family should support parameterized honeypots by:

1. count
2. lexical overlap strength

Suggested difficulty buckets:

- easy:
  one shared query token
- medium:
  two to three shared query tokens
- hard:
  four or more shared query tokens

The paper-facing suite does not need all buckets, but calibration should test
them.

## Budget-Curve Focus

`final_v2` should explicitly characterize two budget landmarks:

1. transition point:
   the first budget where DSGC becomes stably successful
2. crossover point:
   the budget where retrieval-only catches up

The interval between those points is DSGC's effective operating range.

This is a stronger argument than a single budget comparison.

## Pre-Registration Targets For final_v2

The next preregistered paper-facing suite should test predictions of this form.

### P1. Clean control prediction

On the chosen controls:

- `retrieval_only >= 0.90`
- `dsgc_no_graph ~= retrieval_only`
- `dsgc ~= retrieval_only`

### P2. Graph mechanism prediction

On the chosen targets:

- `dsgc > dsgc_no_graph`
- `dsgc > retrieval_only`

### P3. Budget-curve prediction

There exists a budget interval in which:

- `dsgc` is stably above `retrieval_only`
- `retrieval_only` has not yet saturated

### P4. Depth prediction

If chain depth increases from `2` to `3` in the calibrated target family, the
DSGC advantage should remain visible or increase.

### P5. Encoder prediction

For target templates intended to be structural rather than lexical:

- `dsgc` should retain a positive advantage under the sentence encoder

If that prediction fails, the target should be labeled encoder-dependent or
removed from the main suite.

## What final_v2 Should Not Do

`final_v2` should not:

- turn calibration sweeps into headline tables
- mix failed control templates into the final control pool
- silently relabel encoder-sensitive failures as structural wins
- explode the main suite into an unreadable multi-axis grid

The point is to get cleaner evidence, not to get more numbers.
