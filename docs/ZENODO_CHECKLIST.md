# Zenodo Checklist

## GitHub side

1. Sign in to Zenodo and enable the GitHub integration.
2. In Zenodo, turn on archiving for `smkgenesis/dsgc`.
3. In GitHub, create a release from tag `v0.1.0`.
4. Use `docs/RELEASE_v0.1.0.md` as the release body.

## Zenodo side

1. Wait for Zenodo to ingest the GitHub release.
2. Verify title, author name, repository URL, and license.
3. Confirm that the generated DOI points to the release archive.
4. Copy the DOI back into:
   - `README.md`
   - `CITATION.cff`
   - `.zenodo.json`
   - the paper text, if the manuscript cites the software DOI directly

## After DOI assignment

Create a small follow-up commit that replaces DOI placeholders or repository-only
references with the final Zenodo DOI, then tag a patch release if needed.
