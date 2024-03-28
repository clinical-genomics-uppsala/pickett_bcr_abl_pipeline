__author__ = "Arielle R. Munters"
__copyright__ = "Copyright 2024, Arielle R. Munters"
__email__ = "arielle.munters@scilifelab.uu.se"
__license__ = "GPL-3"


include: "rules/common.smk"
include: "rules/create_background_file.smk"


rule all:
    input:
        compile_output_file_list,


module pipeline:
    snakefile:
        "Snakefile"
    config:
        config


use rule * from pipeline exclude all


use rule bcftools_reheader from pipeline with:
    input:
        vcf="snv_indels/pisces/{sample}_{type}_{chr}_bad_name/{sample}_{type}_{chr}.genome.vcf",


use rule dotnet_pisces from pipeline with:
    output:
        vcf=temp("snv_indels/pisces/{sample}_{type}_{chr}_bad_name/{sample}_{type}_{chr}.genome.vcf"),
        pisces_log=temp("snv_indels/pisces/{sample}_{type}_{chr}_bad_name/PiscesLogs/PiscesLog.txt"),
        pisces_options=temp("snv_indels/pisces/{sample}_{type}_{chr}_bad_name/PiscesLogs/PiscesOptions.used.json"),
    params:
        extra=config.get("dotnet_pisces", {}).get("extra", "--gvcf TRUE --filterduplicates TRUE"),
