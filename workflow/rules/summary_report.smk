__author__ = "Arielle R. Munters"
__copyright__ = "Copyright 2022, Arielle R. Munters"
__email__ = "arielle.munters@scilifelab.uu.se"
__license__ = "GPL-3"


rule summary_report:
    input:
        vcf="snv_indels/pisces/{sample}_{type}.normalized.sorted.background_annotated.vcf.gz",
        tbi="snv_indels/pisces/{sample}_{type}.normalized.sorted.background_annotated.vcf.gz.tbi",
        branford=config["summary_report"]["branford"],
        bed=config["reference"]["design_bed"],
        mosdepth_regions="qc/mosdepth_bed/{sample}_{type}.regions.bed.gz",
        arriba_tsv="fusions/arriba/{sample}_{type}.fusions.tsv",
        jpg="fusions/arriba_draw_fusion/{sample}_{type}_page1.jpg",
        background=config["reference"]["background"],
    output:
        xlsx="Results/{sample}_{type}_summary.xlsx",
    params:
        extra=config.get("summary_report", {}).get("extra", ""),
    log:
        "summary_report/{sample}_{type}.output.log",
    benchmark:
        repeat(
            "summary_report/{sample}_{type}.output.benchmark.tsv",
            config.get("summary_report", {}).get("benchmark_repeats", 1),
        )
    threads: config.get("summary_report", {}).get("threads", config["default_resources"]["threads"])
    resources:
        mem_mb=config.get("summary_report", {}).get("mem_mb", config["default_resources"]["mem_mb"]),
        mem_per_cpu=config.get("summary_report", {}).get("mem_per_cpu", config["default_resources"]["mem_per_cpu"]),
        partition=config.get("summary_report", {}).get("partition", config["default_resources"]["partition"]),
        threads=config.get("summary_report", {}).get("threads", config["default_resources"]["threads"]),
        time=config.get("summary_report", {}).get("time", config["default_resources"]["time"]),
    container:
        config.get("summary_report", {}).get("container", config["default_container"])
    message:
        "{rule}: Summarize {input.vcf} results in {output.xlsx}"
    script:
        "../scripts/summary_report.py"
