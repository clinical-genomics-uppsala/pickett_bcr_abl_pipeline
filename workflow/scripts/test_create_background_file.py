# workflow/scripts/test_create_background_file.py

import gzip
import runpy
from types import SimpleNamespace


def write_vcf_gz(path, chrom="chr1", pos=100, ad="90,10", dp=100):
    text = "\n".join(
        [
            "##fileformat=VCFv4.2",
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE",
            f"{chrom}\t{pos}\t.\tA\tC\t.\tPASS\t.\tGT:AD:DP\t0/1:{ad}:{dp}",
            "",
        ]
    )
    with gzip.open(path, "wt") as f:
        f.write(text)


def test_create_background_file_requires_four_observations(tmp_path):
    vcfs = []
    for i in range(4):
        p = tmp_path / f"sample_{i}.vcf.gz"
        write_vcf_gz(p)
        vcfs.append(str(p))

    output = tmp_path / "background_panel.tsv"

    fake_snakemake = SimpleNamespace(
        input=SimpleNamespace(gvcfs=vcfs),
        output=SimpleNamespace(background_file=str(output)),
        params=SimpleNamespace(min_dp=50, max_af=0.2),
    )

    runpy.run_path(
        "workflow/scripts/create_background_file.py",
        init_globals={"snakemake": fake_snakemake},
    )

    lines = output.read_text().splitlines()
    assert lines[0] == "Chr\tPos\tMedian\tSD\tNrSamples"
    assert lines[1].startswith("chr1\t100\t0.1\t")
    assert lines[1].endswith("\t4")
