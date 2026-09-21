# Building the offline Miarka package

Run the build on Marvin, where the source reference files and the tested
container images are available. The resulting archive contains the pipeline,
a relocatable Python environment, pinned Hydra modules, Snakemake wrappers,
the Miarka profile, containers and references. The launcher remains separately
versioned in `pipeline_start_scripts` and is not part of this package.

The pipeline itself is cloned by the build script into a temporary directory;
it does not need to be installed below `/projects/bin/wp2_abl` first. Local
pipeline-owned reference URLs are rewritten to that temporary checkout during
the build. The external reference sources under `/data` and `/projects/wp2`
and the container cache still need to be readable on Marvin.

```bash
module load miniconda3

bash build/build_pickett_package.sh \
  --pipeline-ref Miarka \
  --package-version v0.3.0-rc1 \
  --work-dir /projects/wp2/nobackup/pickett-build-work \
  --output-dir "$PWD/build-output"
```

Choose a `--work-dir` on a filesystem with enough free space for the unpacked
references, Python environment, containers and build caches. The script also
directs Python, Hydra, conda and pip temporary data there. The filesystem used
by `--output-dir` must separately have room for the final compressed archive.

For the final release, use an immutable Git tag or commit for `--pipeline-ref`
and use the same release name for `--package-version`.

The build refuses to continue if a required reference, checksum, module
revision, profile or container is missing. Existing output archives are never
overwritten. Local reference sources are checked for existence and read access
before the Python environment or large reference trees are built; Hydra then
performs the checksum validation while materializing the references.

## Install on Miarka

Verify and extract the package:

```bash
sha256sum -c pickett_v0.3.0-rc1_miarka_offline.tar.gz.sha256

INSTALL_ROOT=/proj/ngi2024001/nobackup/bin/wp2_abl
mkdir -p "$INSTALL_ROOT"
tar -xzf pickett_v0.3.0-rc1_miarka_offline.tar.gz -C "$INSTALL_ROOT"
"$INSTALL_ROOT/v0.3.0-rc1/venv_pickett/bin/conda-unpack"
```

Use the separately installed launcher from the `pipeline_start_scripts/miarka`
directory.

Smoke-test the installation before processing data:

```bash
bash /path/to/pipeline_start_scripts/miarka/start_wp2_abl.sh \
  --bin-path "$INSTALL_ROOT" \
  --pickett-version v0.3.0-rc1 \
  --inbox-path /path/to/a/test/run \
  --analysis-path /path/to/a/new/test/analysis \
  --dry-run
```
