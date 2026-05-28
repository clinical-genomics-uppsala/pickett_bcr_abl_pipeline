__author__ = "Arielle R. Munters"
__copyright__ = "Copyright 2022, Arielle R. Munters"
__email__ = "arielle.munters@scilifelab.uu.se"
__license__ = "GPL-3"


rule sample_order_for_multiqc:
    output:
        replacement="qc/multiqc/sample_replacement.tsv",
        order="qc/multiqc/sample_order.tsv",
    log:
        "qc/multiqc/sample_order.tsv.log",
    benchmark:
        repeat(
            "qc/multiqc/sample_order.tsv.benchmark.tsv",
            config.get("sample_order_for_multiqc", {}).get("benchmark_repeats", 1),
        )
    container:
        config.get("sample_order_for_multiqc", {}).get(
            "container", config["default_container"]
        )
    threads:
        config.get("sample_order_for_multiqc", {}).get(
            "threads", config["default_resources"]["threads"]
        )
    resources:
        mem_mb=config.get("sample_order_for_multiqc", {}).get(
            "mem_mb", config["default_resources"]["mem_mb"]
        ),
        mem_per_cpu=config.get("sample_order_for_multiqc", {}).get(
            "mem_per_cpu", config["default_resources"]["mem_per_cpu"]
        ),
        partition=config.get("sample_order_for_multiqc", {}).get(
            "partition", config["default_resources"]["partition"]
        ),
        threads=config.get("sample_order_for_multiqc", {}).get(
            "threads", config["default_resources"]["threads"]
        ),
        time=config.get("sample_order_for_multiqc", {}).get(
            "time", config["default_resources"]["time"]
        ),
    params:
        filelist=[(u.sample, u.fastq1) for u in units[units.type == "R"].itertuples()],
    message:
        "{rule}: Create a sample order tsv based on S_index in {params.filelist} for multiqc"
    script:
        "../scripts/sample_order_for_multiqc.py"
