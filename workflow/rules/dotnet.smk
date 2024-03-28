__author__ = "Arielle R Munters"
__copyright__ = "Copyright 2022, Arielle R Munters"
__email__ = "arielle.munters@scilifelab.uu.se"
__license__ = "GPL-3"


rule dotnet_pisces:
    input:
        bam="alignment/samtools_extract_reads/{sample}_{type}_{chr}.bam",
        bai="alignment/samtools_extract_reads/{sample}_{type}_{chr}.bam.bai",
        fasta=config.get("reference", {}).get("fasta", ""),
        bed="snv_indels/bed_split/design_bedfile_{chr}.bed",
    output:
        vcf=temp("snv_indels/pisces/{sample}_{type}_{chr}_bad_name/{sample}_{type}_{chr}.vcf"),
        pisces_log=temp("snv_indels/pisces/{sample}_{type}_{chr}_bad_name/PiscesLogs/PiscesLog.txt"),
        pisces_options=temp("snv_indels/pisces/{sample}_{type}_{chr}_bad_name/PiscesLogs/PiscesOptions.used.json"),
    params:
        extra=config.get("dotnet_pisces", {}).get("extra", "--gvcf FALSE --filterduplicates TRUE"),
    log:
        "snv_indels/pisces/{sample}_{type}_{chr}.bad_name.vcf.log",
    benchmark:
        repeat(
            "snv_indels/pisces/{sample}_{type}_{chr}.bad_name.vcf.benchmark.tsv",
            config.get("dotnet_pisces", {}).get("benchmark_repeats", 1),
        )
    threads: config.get("dotnet_pisces", {}).get("threads", config["default_resources"]["threads"])
    resources:
        mem_mb=config.get("dotnet_pisces", {}).get("mem_mb", config["default_resources"]["mem_mb"]),
        mem_per_cpu=config.get("dotnet_pisces", {}).get("mem_per_cpu", config["default_resources"]["mem_per_cpu"]),
        partition=config.get("dotnet_pisces", {}).get("partition", config["default_resources"]["partition"]),
        threads=config.get("dotnet_pisces", {}).get("threads", config["default_resources"]["threads"]),
        time=config.get("dotnet_pisces", {}).get("time", config["default_resources"]["time"]),
    container:
        config.get("dotnet_pisces", {}).get("container", config["default_container"])
    message:
        "{rule}: Call variants using Illumina Pisces on alignment/samtools_extract_reads/{wildcards.sample}_{wildcards.type}_{wildcards.chr}.bam"
    shell:
        "REF_FOLDER=`dirname {input.fasta}` && "
        "OUTPUT_FOLDER=`dirname {output.vcf}` && "
        "(dotnet /app/Pisces/Pisces.dll "
        "-b {input.bam} "
        "-g $REF_FOLDER "
        "-i {input.bed} "
        "-t {threads} "
        "--outfolder $OUTPUT_FOLDER "
        "{params.extra}) "
        "&> {log}"
