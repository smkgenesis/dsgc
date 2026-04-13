# Redesign Policy

This note records the repository policy used when a benchmark revision changes
the paper-facing claim materially enough that an in-place patch would blur the
scientific record.

## Rule

Create a new versioned redesign whenever a change affects any of the following:

- benchmark template selection
- evaluation protocol
- budget regime
- chain-depth regime
- distractor construction
- metric schema
- interpretation of the paper-facing claim

## Rationale

The repository keeps failed or superseded experiment generations as auditable
records rather than silently rewriting them into the latest benchmark. That is
why `final_v1`, calibration, and the frozen `final_v2_main` suite are kept as
separate records.

## Consequence

When this threshold is crossed:

- the old run remains preserved under `audit/`
- the redesign is documented in `audit/docs/`
- the next paper-facing suite is versioned separately under `protocols/` and
  `results/`
