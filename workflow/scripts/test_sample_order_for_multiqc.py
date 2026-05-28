# workflow/scripts/test_sample_order_for_multiqc.py

import runpy
from types import SimpleNamespace


def test_sample_order_for_multiqc_sorts_and_deduplicates(tmp_path):
    replacement = tmp_path / "sample_replacement.tsv"
    order = tmp_path / "sample_order.tsv"

    fake_snakemake = SimpleNamespace(
        params=SimpleNamespace(
            filelist=[
                ("SAMPLE_B", "/data/SAMPLE_B_S2_L001_R1.fastq.gz"),
                ("SAMPLE_A", "/data/SAMPLE_A_S1_L001_R1.fastq.gz"),
                ("SAMPLE_A", "/data/SAMPLE_A_S1_L002_R1.fastq.gz"),
            ]
        ),
        output=SimpleNamespace(
            replacement=str(replacement),
            order=str(order),
        ),
    )

    runpy.run_path(
        "workflow/scripts/sample_order_for_multiqc.py",
        init_globals={"snakemake": fake_snakemake},
    )

    assert replacement.read_text().splitlines() == [
        "SAMPLE_A\tsample_001",
        "SAMPLE_B\tsample_002",
    ]

    assert order.read_text().splitlines() == [
        "Sample Order\tSample Name",
        "sample_001\tSAMPLE_A",
        "sample_002\tSAMPLE_B",
    ]