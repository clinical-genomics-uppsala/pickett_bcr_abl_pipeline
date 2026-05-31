#!/usr/bin/env python3
"""Copy Marvin reference/library assets into a traceable cgu/library tree.

The script scans known Marvin start scripts and pipeline config files for
absolute reference/data paths, writes an audit manifest, and optionally copies
the discovered assets into a new library root while preserving the original
source path under the destination.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


DEFAULT_REPO_ROOT = Path("/Users/olwal516/dev/cgu_pipelines")
PIPELINE_GLOBS: dict[str, list[str]] = {
    "wp1_gms560": [
        "miarka/pipeline_start_scripts/marvin/start_wp1_gms560.sh",
        "GMS560_config/config/Marvin/**/*.yaml",
        "GMS560_config/profiles/Marvin/**/*.yaml",
        "Twist_DNA_Solid/config/**/*.yaml",
    ],
    "wp1_gms560_plasma": [
        "miarka/pipeline_start_scripts/marvin/start_wp1_gms560-plasma.sh",
        "GMS560_config/config/Marvin/**/*.yaml",
        "GMS560_config/profiles/Marvin/**/*.yaml",
        "Twist_DNA_Solid/config/**/*.yaml",
    ],
    "wp1_gmsprio": [
        "miarka/pipeline_start_scripts/marvin/start_wp1_gmsprio.sh",
        "GMS560_config/config/Marvin/**/*.yaml",
        "GMS560_config/profiles/Marvin/**/*.yaml",
        "Twist_DNA_Solid/config/**/*.yaml",
    ],
    "wp1_sera": [
        "miarka/pipeline_start_scripts/marvin/start_wp1_sera.sh",
    ],
    "wp2_abl": [
        "miarka/pipeline_start_scripts/marvin/start_wp2_abl.sh",
        "wp2/WP2_smallscripts/snakemake-profiles/pickett_bcr_abl/marvin_config/*.yaml",
        "wp2/pickett_bcr_abl_pipeline/config/site_configs/*marvin*.yaml",
        "wp2/pickett_bcr_abl_pipeline/config/reference_files/*marvin*.yaml",
    ],
    "wp2_iht": [
        "miarka/pipeline_start_scripts/marvin/start_wp2_iht.sh",
        "wp2/fluffy_hematology_wgs/config/site_configs/*marvin*.yaml",
        "wp2/fluffy_hematology_wgs/config/reference_files/*marvin*.yaml",
    ],
    "wp3_iht": [
        "miarka/pipeline_start_scripts/marvin/start_wp3_iht.sh",
        "wp2/fluffy_hematology_wgs/config/site_configs/*marvin*.yaml",
        "wp2/fluffy_hematology_wgs/config/reference_files/*marvin*.yaml",
    ],
    "wp2_tm": [
        "miarka/pipeline_start_scripts/marvin/start_wp2_tm.sh",
        "wp2/poppy_uppsala/config/site_configs/*marvin*.yaml",
        "wp2/poppy_uppsala/config/reference_files/*marvin*.yaml",
        "wp2/poppy_uppsala_config/config/marvin/**/*.yaml",
        "wp2/poppy_uppsala_config/profiles/marvin/**/*.yaml",
    ],
    "wp2_neville": [
        "wp2/neville_mx_amplicon/config/site_configs/*marvin*.yaml",
        "wp2/neville_mx_amplicon/config/reference_files/*marvin*.yaml",
    ],
    "wp3_hg": [
        "miarka/pipeline_start_scripts/marvin/start_wp3_hg.sh",
        "poirot_rd_wgs/config/**/*.yaml",
        "poirot_config/config/**/*",
        "poirot_config/profiles/**/*",
    ],
    "wp3_tc": [
        "miarka/pipeline_start_scripts/marvin/start_wp3_tc.sh",
        "marple_rd_tc/config/**/*.yaml",
        "marple_config/config/**/*",
        "marple_config/profiles/**/*",
    ],
    "wp3_te": [
        "miarka/pipeline_start_scripts/marvin/start_wp3_te.sh",
        "hastings_rd_wes/config/**/*.yaml",
        "hastings_rd_wes/profiles/**/*.yaml",
    ],
}

OPTIONAL_PIPELINE_GLOBS: dict[str, list[str]] = {
    "fada": ["fada/config/**/*.yaml", "fada/profiles/**/*.yaml"],
    "twimm": ["TwiMM/config/**/*.yaml", "TwiMM/profiles/**/*.yaml"],
}

ABSOLUTE_PATH_RE = re.compile(
    r"(?:file:)?"
    r"(/(?:data|projects|beegfs-storage|beegfs-archive|proj|scratch)"
    r"/[^\s\"'`<>{}\[\]();]+)"
)

RUNTIME_PATH_PARTS = (
    "/analysis/",
    "/fastq",
    "/inbox",
    "/logs",
    "/nobackup/outbox/",
    "/scratch/",
    "/tmp",
    "/venv",
    "/Workarea/",
    "/workspace/",
)

TOOL_PATH_PARTS = (
    "/apptainer_cache",
    "/hydra-genetics",
    "/singularity_cache",
    "/snakemake-wrappers",
)

PIPELINE_INSTALL_PARTS = (
    "/projects/bin/wp1_gms560",
    "/projects/bin/wp2_abl",
    "/projects/bin/wp2_iht",
    "/projects/bin/wp2_tm",
    "/projects/bin/wp3_hg",
    "/projects/bin/wp3_tc",
    "/projects/bin/wp3_te",
)

REFERENCE_HINTS = (
    "/Bed",
    "/bed",
    "/DATA",
    "/data/ref_",
    "/database",
    "/design",
    "/fasta",
    "/gene",
    "/genome",
    "/indexes",
    "/interval",
    "/panel",
    "/ref",
    "/Ref",
    "/reference",
    "/Reference",
    "/VEP",
)

BROAD_REFERENCE_ROOTS = {
    "/beegfs-storage/data/ref_data",
    "/beegfs-storage/data/ref_genomes",
    "/beegfs-storage/data/ref_genomes/GRCh38",
    "/data/ref_data",
    "/data/ref_genomes",
    "/data/ref_genomes/GRCh38",
    "/projects/wp1/nobackup",
    "/projects/wp2/nobackup",
    "/projects/wp3/nobackup",
}


@dataclass
class Asset:
    source_path: str
    pipelines: set[str] = field(default_factory=set)
    source_files: set[str] = field(default_factory=set)

    def target_path(self, library_root: Path) -> Path:
        return library_root / self.source_path.lstrip("/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan Marvin pipeline configs for reference/data paths and copy "
            "them into a cgu/library tree."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument(
        "--library-root",
        type=Path,
        required=True,
        help="Destination cgu/library directory, for example /projects/cgu/library.",
    )
    parser.add_argument(
        "--pipeline",
        action="append",
        choices=sorted(set(PIPELINE_GLOBS) | set(OPTIONAL_PIPELINE_GLOBS)),
        help="Pipeline to scan. Repeatable. Defaults to active Marvin start-script pipelines.",
    )
    parser.add_argument(
        "--include-optional",
        action="append",
        choices=sorted(OPTIONAL_PIPELINE_GLOBS),
        help="Add an optional pipeline to the default Marvin scan set.",
    )
    parser.add_argument("--manifest", type=Path, default=Path("marvin_library_manifest.json"))
    parser.add_argument("--common-report", type=Path, default=Path("marvin_library_common.tsv"))
    parser.add_argument("--execute", action="store_true", help="Actually copy assets. Default is dry-run.")
    parser.add_argument("--include-containers", action="store_true", help="Include .sif/.simg container files.")
    parser.add_argument("--include-tools", action="store_true", help="Include wrappers, hydra modules, and cache paths.")
    parser.add_argument("--checksum", action="store_true", help="Add sha256 checksums for copied or existing files.")
    parser.add_argument("--rsync", action="store_true", help="Use rsync -a for copying when available.")
    parser.add_argument("--fail-on-missing", action="store_true", help="Return non-zero if any source path is missing.")
    return parser.parse_args()


def selected_pipeline_globs(
    selected: list[str] | None,
    include_optional: list[str] | None,
) -> dict[str, list[str]]:
    if selected:
        merged = {**PIPELINE_GLOBS, **OPTIONAL_PIPELINE_GLOBS}
        return {name: merged[name] for name in selected}
    globs = dict(PIPELINE_GLOBS)
    for name in include_optional or []:
        globs[name] = OPTIONAL_PIPELINE_GLOBS[name]
    return globs


def expand_input_files(repo_root: Path, globs_by_pipeline: dict[str, list[str]]) -> dict[Path, set[str]]:
    files: dict[Path, set[str]] = defaultdict(set)
    for pipeline, patterns in globs_by_pipeline.items():
        for pattern in patterns:
            for match in glob.glob(str(repo_root / pattern), recursive=True):
                path = Path(match)
                if path.is_file():
                    files[path].add(pipeline)
    return files


def clean_candidate(raw_path: str) -> str:
    path = raw_path.rstrip(".,:)]}")
    if "," in path:
        path = path.split(",", 1)[0]
    return path.rstrip("/")


def looks_like_asset(path: str, *, include_containers: bool, include_tools: bool) -> bool:
    if path in BROAD_REFERENCE_ROOTS:
        return False
    if any(part in path for part in RUNTIME_PATH_PARTS):
        return False
    if not include_tools and any(part in path for part in TOOL_PATH_PARTS):
        return False
    if not include_tools and any(part in path for part in PIPELINE_INSTALL_PARTS):
        return path.startswith("/projects/bin/data/")
    if not include_containers and path.endswith((".sif", ".simg")):
        return False
    if "/nobackup/" in path and not any(hint in path for hint in REFERENCE_HINTS):
        return False
    return True


def discover_assets(input_files: dict[Path, set[str]], args: argparse.Namespace) -> dict[str, Asset]:
    assets: dict[str, Asset] = {}
    for file_path, pipelines in sorted(input_files.items()):
        try:
            text = file_path.read_text(errors="ignore")
        except OSError as exc:
            print(f"warning: could not read {file_path}: {exc}", file=sys.stderr)
            continue
        for match in ABSOLUTE_PATH_RE.finditer(text):
            source_path = clean_candidate(match.group(1))
            if not looks_like_asset(
                source_path,
                include_containers=args.include_containers,
                include_tools=args.include_tools,
            ):
                continue
            asset = assets.setdefault(source_path, Asset(source_path=source_path))
            asset.pipelines.update(pipelines)
            asset.source_files.add(str(file_path))
    return assets


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_type(path: Path) -> str:
    if path.is_dir():
        return "directory"
    if path.is_file():
        return "file"
    if path.is_symlink():
        return "symlink"
    return "missing"


def copy_asset(source: Path, target: Path, *, execute: bool, use_rsync: bool) -> str:
    if not source.exists():
        return "missing"
    if not execute:
        return "dry_run"
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        target.mkdir(parents=True, exist_ok=True)
        if use_rsync and shutil.which("rsync"):
            subprocess.run(["rsync", "-a", f"{source}/", f"{target}/"], check=True)
        else:
            shutil.copytree(source, target, dirs_exist_ok=True, symlinks=True)
        return "copied"
    shutil.copy2(source, target)
    return "copied"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_common_report(path: Path, manifest_items: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["pipeline_count\tpipelines\tsource_path\ttarget_path\n"]
    common = [item for item in manifest_items if len(item["pipelines"]) > 1]
    for item in sorted(common, key=lambda i: (-len(i["pipelines"]), i["source_path"])):
        lines.append(
            f"{len(item['pipelines'])}\t"
            f"{','.join(item['pipelines'])}\t"
            f"{item['source_path']}\t"
            f"{item['target_path']}\n"
        )
    path.write_text("".join(lines))


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    library_root = args.library_root.expanduser()
    globs_by_pipeline = selected_pipeline_globs(args.pipeline, args.include_optional)
    input_files = expand_input_files(repo_root, globs_by_pipeline)
    assets = discover_assets(input_files, args)

    manifest_items = []
    missing = 0
    copied = 0
    for source_path, asset in sorted(assets.items()):
        source = Path(source_path)
        target = asset.target_path(library_root)
        status = copy_asset(source, target, execute=args.execute, use_rsync=args.rsync)
        if status == "missing":
            missing += 1
        if status == "copied":
            copied += 1
        item = {
            "source_path": source_path,
            "target_path": str(target),
            "source_type": path_type(source),
            "status": status,
            "pipelines": sorted(asset.pipelines),
            "source_files": sorted(asset.source_files),
        }
        if args.checksum and source.is_file():
            item["source_sha256"] = sha256_file(source)
        manifest_items.append(item)

    payload = {
        "repo_root": str(repo_root),
        "library_root": str(library_root),
        "dry_run": not args.execute,
        "pipeline_count": len(globs_by_pipeline),
        "input_file_count": len(input_files),
        "asset_count": len(manifest_items),
        "copied_count": copied,
        "missing_count": missing,
        "pipelines": sorted(globs_by_pipeline),
        "assets": manifest_items,
    }
    write_json(args.manifest, payload)
    write_common_report(args.common_report, manifest_items)

    print(f"Scanned {len(input_files)} input files across {len(globs_by_pipeline)} pipelines.")
    print(f"Discovered {len(manifest_items)} likely library assets.")
    print(f"Missing on this host: {missing}")
    print(f"Copied: {copied}")
    print(f"Manifest: {args.manifest}")
    print(f"Common report: {args.common_report}")
    if not args.execute:
        print("Dry-run only. Add --execute to copy into the library root.")
    if missing and args.fail_on_missing:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
