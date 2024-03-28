__author__ = "Arielle R. Munters"
__copyright__ = "Copyright 2022, Arielle R. Munters"
__email__ = "arielle.munters@scilifelab.uu.se"
__license__ = "GPL-3"


rule convert_pdf:
    input:
        pdf="fusions/arriba_draw_fusion/{sample}_{type}.pdf",
    output:
        jpg="fusions/arriba_draw_fusion/{sample}_{type}_page1.jpg",
    params:
        extra=config.get("convert_pdf", {}).get("extra", ""),
    log:
        "fusions/arriba_draw_fusion/{sample}_{type}_page1.jpg.log",
    benchmark:
        repeat(
            "fusions/arriba_draw_fusion/{sample}_{type}_page1.jpg.benchmark.tsv",
            config.get("convert_pdf", {}).get("benchmark_repeats", 1),
        )
    threads: config.get("convert_pdf", {}).get("threads", config["default_resources"]["threads"])
    resources:
        mem_mb=config.get("convert_pdf", {}).get("mem_mb", config["default_resources"]["mem_mb"]),
        mem_per_cpu=config.get("convert_pdf", {}).get("mem_per_cpu", config["default_resources"]["mem_per_cpu"]),
        partition=config.get("convert_pdf", {}).get("partition", config["default_resources"]["partition"]),
        threads=config.get("convert_pdf", {}).get("threads", config["default_resources"]["threads"]),
        time=config.get("convert_pdf", {}).get("time", config["default_resources"]["time"]),
    container:
        config.get("convert_pdf", {}).get("container", config["default_container"])
    message:
        "{rule}: Convert first page of {input.pdf} to {output.jpg}"
    shell:
        "(convert -background white -alpha background -alpha off -density 300 -quality 100 {input.pdf}[0] {output.jpg}) &> {log}"
