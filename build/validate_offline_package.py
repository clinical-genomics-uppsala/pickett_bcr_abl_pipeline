#!/usr/bin/env python3
"""Validate the filesystem layout of a built Pickett offline package."""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

import yaml


def md5(path):
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def registry_entries(value, prefix=""):
    if not isinstance(value, dict):
        return
    if "path" in value:
        yield prefix, value
        return
    for key, child in value.items():
        name = f"{prefix}.{key}" if prefix else key
        yield from registry_entries(child, name)


def strings(value, prefix=""):
    if isinstance(value, dict):
        for key, child in value.items():
            name = f"{prefix}.{key}" if prefix else key
            yield from strings(child, name)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from strings(child, f"{prefix}[{index}]")
    elif isinstance(value, str):
        yield prefix, value


def fail(errors, message):
    errors.append(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    root = args.package_root.resolve()
    pipeline = root / args.version / "pickett_bcr_abl_pipeline"
    config_file = pipeline / "config/config.yaml"
    registry_file = pipeline / "config/reference_files/reference_files_marvin.yaml"
    reference_root = root / "design_and_ref_files"
    pickett_references = reference_root / "pickett"
    container_root = root / "apptainer_cache"
    errors = []

    for required in (
        config_file,
        registry_file,
        pipeline / "workflow/Snakefile",
        root / args.version / "venv_pickett/bin/hydra-genetics",
        root / args.version / "venv_pickett/bin/snakemake",
        root / "snakemake-profiles/config.yaml",
    ):
        if not required.exists():
            fail(errors, f"missing package component: {required.relative_to(root)}")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1

    config = yaml.safe_load(config_file.read_text())
    registry = yaml.safe_load(registry_file.read_text())
    if config.get("PIPELINE_VERSION") != args.version:
        fail(
            errors,
            f"config PIPELINE_VERSION is {config.get('PIPELINE_VERSION')}, expected {args.version}",
        )

    # Validate every registry target and all declared checksums.
    for name, entry in registry_entries(registry):
        target = reference_root / entry["path"]
        expected_type = entry.get("type")
        if expected_type == "file" and not target.is_file():
            fail(errors, f"{name}: missing reference file {target.relative_to(root)}")
            continue
        if expected_type == "folder" and not target.is_dir():
            fail(errors, f"{name}: missing reference folder {target.relative_to(root)}")
            continue
        if "checksum" in entry and target.is_file():
            actual = md5(target)
            if actual != entry["checksum"]:
                fail(errors, f"{name}: md5 {actual}, expected {entry['checksum']}")
        for relative, expected in (entry.get("content_checksum") or {}).items():
            child = target / relative
            if not child.is_file():
                fail(errors, f"{name}: missing archive member {child.relative_to(root)}")
            else:
                actual = md5(child)
                if actual != expected:
                    fail(errors, f"{name}/{relative}: md5 {actual}, expected {expected}")

    context = {
        "REFERENCE_DATA": str(pickett_references),
        "APPTAINER_CACHE": str(container_root),
        "PATH_TO_REPO": str(root / args.version),
        "CONFIG_DIR": str(pipeline / "config"),
        "ANNOTATIONS": str(pipeline / "config/annotations_hg19"),
    }

    def resolve(text):
        for _ in range(10):
            previous = text
            for key, value in context.items():
                text = text.replace("{{" + key + "}}", value)
            if text == previous:
                break
        return text

    # Check all paths generated from the package's path variables, including
    # paths embedded in command-line option strings such as arriba.extra.
    package_path = re.compile(re.escape(str(root)) + r"[^\s\"']*")
    for name, raw in strings(config):
        resolved = resolve(raw)
        for match in package_path.findall(resolved):
            candidate = Path(match.rstrip(",;"))
            if not candidate.exists():
                fail(errors, f"{name}: runtime path does not exist: {candidate}")

    for module, revision in config.get("modules", {}).items():
        repository = root / "hydra-genetics" / module
        if not repository.is_dir():
            fail(errors, f"missing Hydra module: hydra-genetics/{module}")
            continue
        result = subprocess.run(
            ["git", "-C", str(repository), "cat-file", "-e", f"{revision}^{{commit}}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode:
            fail(errors, f"hydra-genetics/{module} lacks revision {revision}")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1

    print(f"Offline package validated: {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
