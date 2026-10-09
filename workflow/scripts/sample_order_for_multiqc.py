#!/bin/python3

import sys
import csv
import re

# process input as pairs, [sample, fastq1] from units.tsv
sample_order = {}
s_pattern = re.compile("_S([0-9]+)_")
for sample, fastq_path in snakemake.params.filelist:
    fastq = fastq_path.split("/")[-1]
    match = s_pattern.search(fastq)
    s_index = int(match.group(1)) if match else float("inf")
    sample_order[sample] = min(s_index, sample_order.get(sample, s_index))

# Order by sequencing sample index when present, with a deterministic sample-name
# tie-breaker and a fallback for filenames without an _S index.
sample_order = sorted(sample_order.items(), key=lambda x: (x[1], x[0]))

with open(snakemake.output.replacement, "w+") as tsv:
    tsv_writer = csv.writer(tsv, delimiter="\t")
    i = 1
    for sample, _ in sample_order:
        tsv_writer.writerow([sample, "sample_" + str(f"{i:03}")])
        i += 1

with open(snakemake.output.order, "w+") as tsv:
    tsv_writer = csv.writer(tsv, delimiter="\t")
    tsv_writer.writerow(["Sample Order", "Sample Name"])
    i = 1
    for sample, _ in sample_order:
        tsv_writer.writerow(["sample_" + str(f"{i:03}"), sample])
        i += 1
