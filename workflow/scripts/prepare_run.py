#!/usr/bin/env python3
"""
Pickett's hook for the common CGU launcher (pipeline_start_scripts/tools/launch.py).

The launcher does everything that is the same for every pipeline. This file
holds only what is specific to Pickett, and is versioned with the pipeline.

    prepare_run.py inputs --run-dir D --pipeline-home H

`inputs` runs right after `hydra-genetics create-input-files` and fixes two
things in units.tsv that the MiSeq headers produce:

  * the flowcell comes out as "000000000-XXXXX"; the prefix is dropped
    (first occurrence per line, as the former `sed 's/\\t000000000-/\\t/'`)
  * doubled slashes in FASTQ paths are collapsed (`sed 's|//|/|g'`)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def fix_units(units: Path) -> None:
    lines = units.read_text().split("\n")
    fixed = [line.replace("\t000000000-", "\t", 1).replace("//", "/") for line in lines]
    units.write_text("\n".join(fixed))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["inputs"])
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--pipeline-home", type=Path, required=True)
    args = parser.parse_args(argv)

    units = args.run_dir / "units.tsv"
    if not units.is_file():
        print(f"ERROR: {units} missing", file=sys.stderr)
        return 1
    fix_units(units)
    return 0


if __name__ == "__main__":
    sys.exit(main())
