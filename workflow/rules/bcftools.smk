__author__ = "Arielle R Munters"
__copyright__ = "Copyright 2022, Arielle R Munters"
__email__ = "arielle.munters@scilifelab.uu.se"
__license__ = "GPL-3"


rule bcftools_reheader:
    input:
        vcf="snv_indels/pisces/{sample}_{type}_{chr}_bad_name/{sample}_{type}_{chr}.vcf",
    output:
        vcf=temp("snv_indels/pisces/{sample}_{type}_{chr}.vcf"),
        samplename=temp("snv_indels/pisces/{sample}_{type}_{chr}.name.txt"),
    params:
        extra=config.get("bcftools_reheader", {}).get("extra", ""),
    log:
        "snv_indels/pisces/{sample}_{type}_{chr}.vcf.log",
    benchmark:
        repeat(
            "snv_indels/pisces/{sample}_{type}_{chr}.vcf.benchmark.tsv",
            config.get("bcftools_reheader", {}).get("benchmark_repeats", 1),
        )
    threads: config.get("bcftools_reheader", {}).get("threads", config["default_resources"]["threads"])
    resources:
        mem_mb=config.get("bcftools_reheader", {}).get("mem_mb", config["default_resources"]["mem_mb"]),
        mem_per_cpu=config.get("bcftools_reheader", {}).get("mem_per_cpu", config["default_resources"]["mem_per_cpu"]),
        partition=config.get("bcftools_reheader", {}).get("partition", config["default_resources"]["partition"]),
        threads=config.get("bcftools_reheader", {}).get("threads", config["default_resources"]["threads"]),
        time=config.get("bcftools_reheader", {}).get("time", config["default_resources"]["time"]),
    container:
        config.get("bcftools_reheader", {}).get("container", config["default_container"])
    message:
        "{rule}: Rename sample in snv_indels/pisces/{wildcards.sample}_{wildcards.type}_{wildcards.chr}.bad_name.vcf"
    shell:
        "echo {wildcards.sample}_{wildcards.type} > {output.samplename} && "
        "(bcftools reheader -s {output.samplename} -o {output.vcf} {input.vcf} ) &> {log}"
