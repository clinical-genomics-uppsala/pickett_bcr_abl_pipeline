import base64
import gzip
import runpy
from types import SimpleNamespace

import pysam


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def test_summary_report_handles_positions_without_background_median(tmp_path):
    vcf_plain = tmp_path / "sample.vcf"
    with vcf_plain.open("w") as handle:
        handle.write(
            "\n".join(
                [
                    "##fileformat=VCFv4.2",
                    "##contig=<ID=chr1,length=1000>",
                    "##INFO=<ID=AF,Number=A,Type=Float,Description=Allele frequency>",
                    "##INFO=<ID=DP,Number=1,Type=Integer,Description=Read depth>",
                    "##FORMAT=<ID=GT,Number=1,Type=String,Description=Genotype>",
                    "##FORMAT=<ID=AD,Number=R,Type=Integer,Description=Allelic depths>",
                    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE",
                    "chr1\t300\t.\tA\tC\t.\tPASS\tAF=0.1;DP=100\tGT:AD\t0/1:90,10",
                    "",
                ]
            )
        )

    vcf = tmp_path / "sample.vcf.gz"
    pysam.tabix_compress(str(vcf_plain), str(vcf), force=True)

    mosdepth = tmp_path / "regions.bed.gz"
    with gzip.open(mosdepth, "wt") as handle:
        handle.write("chr1\t0\t1\ttranscript\t100\n")

    background = tmp_path / "background.tsv"
    background.write_text("Chr\tPos\tMedian\tSD\tNrSamples\nchr1\t100\t0.1\t0.0\t4\n")

    branford = tmp_path / "branford.bed"
    branford.write_text("chr1\tunused\t200\ttranscript\tA\tG\tMUT2\n")

    arriba = tmp_path / "arriba.tsv"
    arriba.write_text(
        "#gene1\tgene2\tbreakpoint1\tbreakpoint2\tconfidence\ttype\t"
        "split_reads1\tsplit_reads2\tdiscordant_mates\tcoverage1\tcoverage2\n"
    )
    image = tmp_path / "arriba.png"
    image.write_bytes(ONE_PIXEL_PNG)
    output = tmp_path / "summary.xlsx"

    fake_snakemake = SimpleNamespace(
        input=SimpleNamespace(
            vcf=str(vcf),
            mosdepth_regions=str(mosdepth),
            background=str(background),
            branford=str(branford),
            bed="bedfile.bed",
            arriba_tsv=str(arriba),
            jpg=str(image),
        ),
        output=SimpleNamespace(xlsx=str(output)),
    )

    runpy.run_path(
        "workflow/scripts/summary_report.py",
        init_globals={"snakemake": fake_snakemake},
    )

    assert output.exists()
    assert output.stat().st_size > 0
