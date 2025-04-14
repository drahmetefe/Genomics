#!/usr/bin/env python3

"""
variant_calling_pipeline.py

Automated variant calling pipeline for small-scale whole genome or exome sequencing.
Steps:
    1. Index reference genome (BWA)
    2. Align paired-end reads (BWA-MEM)
    3. Convert, sort, and index BAM files (SAMtools)
    4. Call variants (BCFtools)

Usage:
    python variant_calling_pipeline.py -r ref.fa -1 sample_R1.fastq -2 sample_R2.fastq -o sample_output
"""

import argparse
import subprocess
import os

def run_cmd(cmd):
    """Execute shell commands safely."""
    print(f"\n[Executing] {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def index_reference(ref):
    run_cmd(f"bwa index {ref}")
    run_cmd(f"samtools faidx {ref}")

def align_reads(ref, r1, r2, output_prefix):
    sam = f"{output_prefix}.sam"
    run_cmd(f"bwa mem -t 4 {ref} {r1} {r2} > {sam}")
    return sam

def convert_sort_index_bam(sam, output_prefix):
    bam = f"{output_prefix}.sorted.bam"
    run_cmd(f"samtools view -S -b {sam} | samtools sort -o {bam}")
    run_cmd(f"samtools index {bam}")
    return bam

def call_variants(ref, bam, output_vcf):
    run_cmd(f"bcftools mpileup -Ou -f {ref} {bam} | bcftools call -mv -Ov -o {output_vcf}")

def main():
    parser = argparse.ArgumentParser(description="Variant Calling Pipeline")
    parser.add_argument("-r", "--reference", required=True, help="Reference genome FASTA")
    parser.add_argument("-1", "--read1", required=True, help="FASTQ R1")
    parser.add_argument("-2", "--read2", required=True, help="FASTQ R2")
    parser.add_argument("-o", "--output", required=True, help="Output prefix")
    args = parser.parse_args()

    index_reference(args.reference)
    sam = align_reads(args.reference, args.read1, args.read2, args.output)
    bam = convert_sort_index_bam(sam, args.output)
    call_variants(args.reference, bam, f"{args.output}.vcf")

if __name__ == "__main__":
    main()
