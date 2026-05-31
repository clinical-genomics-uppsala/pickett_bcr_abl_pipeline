# CGU workflow contract

This contract describes the structure each harmonized CGU pipeline should expose
before deeper refactoring. It is intentionally small: pipelines can differ in
assay logic and Snakefile size, but the same folders and files should mean the
same thing everywhere.

## Goals

- Keep final outputs and rule behavior unchanged during harmonization.
- Make installation, startup, manual restart, and future agent work predictable.
- Keep cluster paths and runtime resources outside workflow logic where possible.
- Prefer physical `cgu/library` assets over symlink-only indirection.
- Move shared helpers into hydra-genetics only after at least two pipelines use
  the same contract.

## Required layout

```text
workflow/
  manifest.yaml
  Snakefile
  Snakefile_references        # only when the pipeline has a reference workflow
  rules/
    common.smk
    results.smk               # preferred location for output manifest/copy logic
    <domain>.smk              # local pipeline rules grouped by workflow domain
  scripts/
    <pipeline-local scripts>
  schemas/
    config.schema.yaml
    resources.schema.yaml
    samples.schema.yaml
    units.schema.yaml
    output_files.schema.yaml
```

## File responsibilities

`workflow/manifest.yaml` is the navigation map for humans and agents. It should
list entrypoints, local rule groups, hydra modules, scripts, and migration
candidates. It should not replace Snakemake config.

`workflow/Snakefile` owns the execution graph: local includes, `rule all`,
module declarations, `use rule` overrides, and rule ordering.

`workflow/rules/common.smk` owns bootstrap logic: config expansion, schema
validation, resource loading, sample/unit/output loading, wildcard constraints,
and very small helpers.

`workflow/rules/results.smk` should own output manifest expansion and generated
copy rules. Some pipelines currently keep this in `common.smk`; those should be
moved gradually when behavior can be preserved.

`workflow/rules/<domain>.smk` should contain local rules grouped by domain, for
example `qc.smk`, `peddy.smk`, `export.smk`, or `varcalling.smk`. Pipeline-
specific biological logic should stay local until it has a stable second user.

`workflow/scripts/` should contain executable helpers used by local rules. Each
manifest should classify scripts as pipeline-specific, shared-tool candidates,
report-module candidates, or cleanup candidates.

## Hydra extraction rules

Move logic into hydra-genetics only when the interface is stable and the same
pattern exists in more than one pipeline.

Good early candidates:

- rule resource/container lookup helpers
- output manifest and generated copy-rule helpers
- repeated report helpers such as sample order, peddy, and results workbook code

Keep local for now:

- assay-specific variant filtering
- caller-specific file reshaping
- one-off clinical report formatting
- scripts that depend on local config shape or naming conventions

## Branching

Pipeline harmonization work should happen on `harmonize` branches based on the
current production branch for that pipeline. For Pickett, the production base is
`Miarka`.
