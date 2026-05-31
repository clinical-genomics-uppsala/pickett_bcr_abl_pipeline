# CGU library harmonization experiment

This note captures the current experiment: make pipeline startup predictable while
moving reference and dataset handling toward a physical `cgu/library` tree.

## Principles

- Keep final pipeline outputs unchanged.
- Treat pipeline installation and run startup as separate steps.
- Prefer a physical cluster library over symlink-only indirection.
- Keep cluster-specific paths small and explicit.
- Make manual restarts use the same commands StackStorm uses.
- Leave enough inline structure for future agents to reason about the pipeline
  without rediscovering every path convention.

## Proposed physical layout

The start scripts now accept `--library-root` and also read
`CGU_LIBRARY_ROOT`. Defaults are intentionally cluster-specific:

- Marvin: `/projects/cgu/library`
- Miarka: `/proj/ngi2024001/nobackup/cgu/library`

The first library copier preserves source paths under the library root. For
example, `/data/ref_genomes/VEP` becomes
`/projects/cgu/library/data/ref_genomes/VEP`. That is conservative and easy to
audit because it avoids renaming reference assets during the first migration.

Longer term, the same manifest can support a nicer semantic layout:

- `genomes/<build>/fasta`
- `genomes/<build>/indices/<tool>`
- `annotations/<build>/<source>/<version>`
- `panels/<assay>/<version>`
- `containers/<pipeline>/<version>`
- `pipelines/<pipeline>/<version>`

The semantic layout should be introduced only after checksums and file counts
prove that copied assets match production inputs.

## Current harmonized start-script scope

The dispatcher in `pipeline_start_scripts/harmonize/start_pipeline.sh` now covers
the previous harmonized scripts plus:

- `wp3_te` / `hastings`: `hastings_rd_wes`
- `wp3_tc` / `marple`: `marple_rd_tc`
- `wp3_hg` / `poirot`: `poirot_rd_wgs` plus `poirot_config`
- `wp1_gms560` / `gms560`: `Twist_DNA_Solid` plus `GMS560_config`
- `wp1_gmsprio` / `gmsprio`: same as `gms560` but with priority profiles

`pipeline_start_scripts/harmonize/pipeline_matrix.yaml` records the current
aliases, repositories, versions, install roots, and library inputs for Pickett,
Fluffy, Poppy, Neville, Hastings, Marple, Poirot, and GMS560/GMSprio. That file
is the handoff point between start-script harmonization and a future
manifest-driven pack/unpack command.

The Marvin library scan is captured in:

- `docs/marvin_library_manifest.json`: full dry-run manifest for 352 likely
  library assets across 12 active Marvin pipeline groups.
- `docs/marvin_library_common.tsv`: compact table of assets shared by multiple
  pipeline groups, useful for prioritizing the first physical `cgu/library`
  copy/verification pass.

The wrappers intentionally do not clone repositories during an analysis run.
They require installed pipeline/config versions to exist and fail early with a
clear preflight error if something is missing. This makes failed runs easier to
restart and makes installation/packing a separate concern for hydra-genetics or
bootstrap tooling.

## Larger follow-up opportunities

- Move tiny reporting utilities that are repeated across pipelines into
  `hydra-genetics/report`.
- Keep project-specific sample transformation scripts inside the pipeline until
  their input/output contracts are stable.
- Consider Rust for high-volume or correctness-sensitive converters only after
  profiling. Good candidates are repeated TSV/VCF/BED converters; small report
  glue is probably better kept in Python.
- Standardize `workflow/rules/*.smk` naming before rewriting logic. Hastings,
  Marple, and Poirot already have overlapping rule names and scripts that can be
  compared mechanically.
- Add a manifest-driven install command that can pack and restore either one
  pipeline or the full CGU pipeline set, including exact config and reference
  checksums.
