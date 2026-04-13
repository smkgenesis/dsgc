# final_v1 Postmortem

This document records why `final_v1` does not close the paper-facing argument
and why the next run must use a new benchmark version rather than an in-place
patch.

## Status

`final_v1` is a valid historical record and should remain reproducible.

It does support a narrow one-hop base-case signal:

- control regime:
  `retrieval_only ~= dsgc_no_graph ~= dsgc`
- target regime:
  `dsgc > retrieval_only ~= dsgc_no_graph`

However, `final_v1` does not fully support the stronger package needed for the
next paper draft.

## What Worked

1. The benchmark removed the most serious earlier artifacts.
   - no query block was stored in memory
   - no graph-driven recall path remained
   - graph ablation behaved honestly
2. The control/target split was partly successful.
   - `budget_control` behaves like a real control
   - target templates show a graph-dependent gain
3. The no-graph condition behaved as intended.
   - `dsgc_no_graph` tracked `retrieval_only` closely on target templates

## What Failed

### 1. The control family is not clean enough

`permission_control` is too difficult for a retrieval-friendly control.

Observed behavior under `final_v1`:

- `retrieval_only` full-chain retention: `0.4000`
- `dsgc` full-chain retention: `0.4000`

This template is not useful as a paper-facing control because retrieval-only
does not succeed reliably there.

### 2. The budget regime is too tight

The `final_v1` budget grid is:

- `1.0`
- `1.25`
- `1.5`

At the low end, this tests whether the policy barely fits the chain rather
than whether the graph term produces a stable operating advantage.

The result is a regime that can be dominated by rank ties and single-block
displacement.

### 3. The target family is not uniformly structural under stronger encoders

`opaque_profile_target` collapses under the sentence encoder:

- sentence + `retrieval_only`: `0.0000`
- sentence + `dsgc`: `0.0000`

This means the current naming scheme does not survive the encoder-sensitivity
check as a stable structural target.

### 4. The current metrics explain too little about failure

`final_v1` reports success and failure, but it does not explain enough about
the mechanism of failure.

Missing diagnostics include:

- which chain block was displaced
- the rank of each chain block before budget truncation
- the propagation contribution received by each prerequisite block
- which non-chain block replaced the missing prerequisite

### 5. Depth-2 chains are too coarse

With chain depth fixed at `2`, full-chain retention behaves almost like a
binary event. This limits:

- partial-failure analysis
- chain-gradient analysis
- evidence about how propagation behaves as dependency structure deepens

## Why This Requires A New Version

These problems cannot be solved honestly by patching `final_v1` in place.

They require changes to:

- control-template selection
- target-template wording
- budget grid
- chain-depth grid
- honeypot difficulty controls
- diagnostic metric schema

Under [`redesign-policy.md`](./redesign-policy.md), that means a new
versioned redesign.

## final_v2 Objectives

`final_v2` should answer four questions more cleanly than `final_v1`.

1. Where is DSGC's stable operating range as budget increases?
2. Which templates are truly retrieval-friendly controls?
3. Which target templates remain structural under a stronger encoder?
4. When DSGC fails, was the failure caused by budget, ranking, or template
   contamination?

The redesign spec for that next phase is defined in
[`docs/final_v2_design.md`](./final_v2_design.md).
