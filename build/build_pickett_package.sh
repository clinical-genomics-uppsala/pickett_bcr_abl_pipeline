#!/usr/bin/env bash
set -euo pipefail

# Do not let packages from the build user's ~/.local directory or PYTHONPATH
# leak into the relocatable pipeline environment.
export PYTHONNOUSERSITE=1
unset PYTHONHOME PYTHONPATH PIP_PREFIX PIP_TARGET PIP_USER

pipeline_repo="https://github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline.git"
pipeline_ref="Miarka"
package_version=""
output_dir="$(pwd)/build-output"
python_version="3.9"
container_source="/projects/bin/wp2_abl/apptainer_cache"
start_scripts_repo="https://github.com/clinical-genomics-uppsala/pipeline_start_scripts.git"
start_scripts_ref="pickett"
keep_build=false

usage() {
    cat <<EOF
Usage: $(basename "$0") --package-version VERSION [options]

Build a complete Pickett package on Marvin for installation on Miarka.

Required:
  --package-version VERSION  Installation directory name, for example v0.3.0.

Options:
  --pipeline-ref REF         Git tag, branch or commit to package. Default: Miarka.
  --pipeline-repo URL        Pipeline repository URL.
  --output-dir DIR           Artifact directory. Default: ./build-output.
  --container-cache DIR      Working Marvin container cache.
                             Default: /projects/bin/wp2_abl/apptainer_cache.
  --python-version VERSION   Conda Python version. Default: 3.9.
  --start-scripts-ref REF    pipeline_start_scripts ref. Default: pickett.
  --keep-build               Preserve the temporary build directory.
  -h, --help                 Show this help.
EOF
}

die() {
    echo "ERROR: $*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

require_option_value() {
    [[ -n "${2:-}" && "$2" != --* ]] || die "$1 requires a value"
}

checkout_detached_ref() {
    local repository_path="$1"
    local requested_ref="$2"
    local commit

    if commit="$(git -C "$repository_path" rev-parse --verify "${requested_ref}^{commit}" 2>/dev/null)"; then
        :
    elif commit="$(git -C "$repository_path" rev-parse --verify "refs/remotes/origin/${requested_ref}^{commit}" 2>/dev/null)"; then
        :
    else
        die "Git ref not found in ${repository_path}: ${requested_ref}"
    fi

    git -C "$repository_path" checkout --detach "$commit"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --package-version)
            require_option_value "$1" "${2:-}"
            package_version="$2"
            shift 2
            ;;
        --pipeline-ref)
            require_option_value "$1" "${2:-}"
            pipeline_ref="$2"
            shift 2
            ;;
        --pipeline-repo)
            require_option_value "$1" "${2:-}"
            pipeline_repo="$2"
            shift 2
            ;;
        --output-dir)
            require_option_value "$1" "${2:-}"
            output_dir="$2"
            shift 2
            ;;
        --container-cache)
            require_option_value "$1" "${2:-}"
            container_source="$2"
            shift 2
            ;;
        --python-version)
            require_option_value "$1" "${2:-}"
            python_version="$2"
            shift 2
            ;;
        --start-scripts-ref)
            require_option_value "$1" "${2:-}"
            start_scripts_ref="$2"
            shift 2
            ;;
        --keep-build)
            keep_build=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage
            die "Unknown option: $1"
            ;;
    esac
done

[[ -n "$package_version" ]] || { usage; die "--package-version is required"; }
[[ "$package_version" =~ ^[A-Za-z0-9._-]+$ ]] || die "Invalid package version: $package_version"
[[ -d "$container_source" ]] || die "Container cache missing: $container_source"

for command in git conda conda-pack tar python3 sha256sum; do
    require_command "$command"
done

mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"
archive="${output_dir}/pickett_${package_version}_miarka_offline.tar.gz"
archive_checksum="${archive}.sha256"
[[ ! -e "$archive" && ! -e "$archive_checksum" ]] || \
    die "Output already exists; move it or choose another --output-dir: $archive"

build_root="$(mktemp -d "${TMPDIR:-/tmp}/pickett-package.XXXXXX")"
package_root="${build_root}/package"
environment_path="${build_root}/conda-env"

cleanup() {
    if [[ "$keep_build" == true ]]; then
        echo "Temporary build preserved at: $build_root"
    else
        rm -rf -- "$build_root"
    fi
}
trap cleanup EXIT

echo "Building Pickett ${package_version} from ${pipeline_ref}"
mkdir -p \
    "${package_root}/${package_version}" \
    "${package_root}/hydra-genetics" \
    "${package_root}/apptainer_cache" \
    "${package_root}/design_and_ref_files" \
    "${package_root}/snakemake-profiles" \
    "${package_root}/start_scripts/miarka"

pipeline_path="${package_root}/${package_version}/pickett_bcr_abl_pipeline"
# Fetch the repository without checking out its default branch.  The requested
# ref may be a branch, tag, or commit, so resolve it explicitly below.
git clone --no-checkout "$pipeline_repo" "$pipeline_path"
checkout_detached_ref "$pipeline_path" "$pipeline_ref"
pipeline_commit="$(git -C "$pipeline_path" rev-parse HEAD)"

echo "Creating relocatable Python environment"
eval "$(conda shell.bash hook)"
conda create --prefix "$environment_path" "python=${python_version}" pip -y
"${environment_path}/bin/python" -s -m pip install -r "${pipeline_path}/requirements.txt"

packed_environment="${build_root}/venv_pickett.tar.gz"
conda-pack --prefix "$environment_path" --output "$packed_environment"
mkdir -p "${package_root}/${package_version}/venv_pickett"
tar -xzf "$packed_environment" -C "${package_root}/${package_version}/venv_pickett"

echo "Cloning pinned Hydra modules"
while IFS=$'\t' read -r module revision; do
    module_path="${package_root}/hydra-genetics/${module}"
    git clone "https://github.com/hydra-genetics/${module}.git" "$module_path"
    git -C "$module_path" cat-file -e "${revision}^{commit}" || \
        die "hydra-genetics/${module} does not contain revision ${revision}"
done < <("${environment_path}/bin/python" - "$pipeline_path" <<'PY'
import pathlib
import sys
import yaml

config = yaml.safe_load((pathlib.Path(sys.argv[1]) / "config/config.yaml").read_text())
for module, revision in config["modules"].items():
    print(f"{module}\t{revision}")
PY
)

profile_source="${pipeline_path}/profiles/miarka"
[[ -f "${profile_source}/config.yaml" ]] || die "Miarka profile missing: ${profile_source}/config.yaml"

echo "Cloning Snakemake wrappers and packaging the Miarka profile"
git clone https://github.com/snakemake/snakemake-wrappers.git \
    "${package_root}/snakemake-wrappers"
cp -a "${profile_source}/." "${package_root}/snakemake-profiles/"

start_scripts_checkout="${build_root}/pipeline_start_scripts"
# Resolve the requested start-script ref separately for the same reason as the
# pipeline ref above.
git clone --no-checkout "$start_scripts_repo" "$start_scripts_checkout"
checkout_detached_ref "$start_scripts_checkout" "$start_scripts_ref"
cp "${start_scripts_checkout}/miarka/start_wp2_abl.sh" \
    "${package_root}/start_scripts/miarka/start_wp2_abl.sh"

# Keep the packaged config and launcher self-identifying even when an RC is
# built from a branch before the final release tag exists.
"${environment_path}/bin/python" - \
    "$package_version" \
    "${pipeline_path}/config/config.yaml" \
    "${package_root}/start_scripts/miarka/start_wp2_abl.sh" <<'PY'
import pathlib
import re
import sys

version = sys.argv[1]
config_path = pathlib.Path(sys.argv[2])
launcher_path = pathlib.Path(sys.argv[3])

config = config_path.read_text()
config, config_count = re.subn(
    r"(?m)^PIPELINE_VERSION:.*$", f"PIPELINE_VERSION: {version}", config, count=1
)
launcher = launcher_path.read_text()
launcher, launcher_count = re.subn(
    r'(?m)^pickett_version="[^"]*"$', f'pickett_version="{version}"', launcher, count=1
)
if config_count != 1 or launcher_count != 1:
    raise SystemExit("Could not update packaged pipeline version")
config_path.write_text(config)
launcher_path.write_text(launcher)
PY

echo "Downloading and validating references with Hydra Genetics"
build_reference_config="${build_root}/reference_files_marvin.yaml"
"${environment_path}/bin/python" - \
    "${pipeline_path}/config/reference_files/reference_files_marvin.yaml" \
    "$pipeline_path" \
    "$build_reference_config" <<'PY'
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
pipeline_path = pathlib.Path(sys.argv[2]).resolve()
destination = pathlib.Path(sys.argv[3])

content = source.read_text()
old_pipeline_url = (
    "file:/projects/bin/wp2_abl/pickett_bcr_abl/"
    "v0.2.2/pickett_bcr_abl_pipeline"
)
content = content.replace(old_pipeline_url, pipeline_path.as_uri())
destination.write_text(content)
PY
"${environment_path}/bin/hydra-genetics" --debug references download \
    -o "${package_root}/design_and_ref_files" \
    -v "$build_reference_config"

echo "Copying the exact container images required by config.yaml"
while IFS= read -r container_name; do
    [[ -n "$container_name" ]] || continue
    source_container="${container_source%/}/${container_name}"
    [[ -f "$source_container" ]] || die "Required container missing: $source_container"
    cp -a "$source_container" "${package_root}/apptainer_cache/${container_name}"
done < <("${environment_path}/bin/python" - "$pipeline_path" <<'PY'
import pathlib
import re
import sys
import yaml

config = yaml.safe_load((pathlib.Path(sys.argv[1]) / "config/config.yaml").read_text())
names = set()

def visit(value):
    if isinstance(value, dict):
        for child in value.values():
            visit(child)
    elif isinstance(value, list):
        for child in value:
            visit(child)
    elif isinstance(value, str):
        for match in re.findall(r"\{\{APPTAINER_CACHE\}\}/([^\s\"']+)", value):
            names.add(match)

visit(config)
print("\n".join(sorted(names)))
PY
)

echo "Validating completed package"
"${environment_path}/bin/python" "${pipeline_path}/build/validate_offline_package.py" \
    --package-root "$package_root" \
    --version "$package_version"

printf '%s\n' \
    "package_version=${package_version}" \
    "pipeline_ref=${pipeline_ref}" \
    "pipeline_commit=${pipeline_commit}" \
    "python_version=${python_version}" \
    "start_scripts_ref=${start_scripts_ref}" \
    "created_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    > "${package_root}/PACKAGE-METADATA.txt"

echo "Writing package checksums"
(
    cd "$package_root"
    find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
)

echo "Creating ${archive}"
tar -czf "$archive" -C "$package_root" .
(
    cd "$output_dir"
    sha256sum "$(basename "$archive")" > "$(basename "$archive_checksum")"
)

echo
echo "Package complete:"
echo "  $archive"
echo "  $archive_checksum"
echo
echo "Install into a new Miarka root with:"
echo "  mkdir -p /proj/ngi2024001/nobackup/bin/wp2_abl"
echo "  tar -xzf $(basename "$archive") -C /proj/ngi2024001/nobackup/bin/wp2_abl"
echo "  /proj/ngi2024001/nobackup/bin/wp2_abl/${package_version}/venv_pickett/bin/conda-unpack"
