#!/usr/bin/env python3

"""
cnv_detection_pipeline.py

A pipeline for Copy Number Variation (CNV) detection from whole-genome Illumina sequencing data.
Steps:
    1. Align reads to reference genome using BWA
    2. Sort and index BAM file using SAMtools
    3. Generate root file using CNVnator
    4. Detect CNVs with CNVnator

Usage:
    python cnv_detection_pipeline.py -r ref.fa -1 sample_R1.fastq -2 sample_R2.fastq -o output_prefix -b bin_size
"""

import subprocess
import argparse
import os

def run_cmd(command):
    print(f"[Running] {command}")
    subprocess.run(command, shell=True, check=True)

def align_reads(ref, r1, r2, out_prefix):
    run_cmd(f"bwa index {ref}")
    sam = f"{out_prefix}.sam"
    run_cmd(f"bwa mem -t 8 {ref} {r1} {r2} > {sam}")
    return sam

def process_bam(sam_file, out_prefix):
    bam = f"{out_prefix}.bam"
    sorted_bam = f"{out_prefix}.sorted.bam"
    run_cmd(f"samtools view -bS {sam_file} | samtools sort -o {sorted_bam}")
    run_cmd(f"samtools index {sorted_bam}")
    return sorted_bam

def prepare_cnvnator(sorted_bam, ref, bin_size, out_prefix):
    root_file = f"{out_prefix}.root"
    run_cmd(f"cnvnator -root {root_file} -tree {sorted_bam}")
    run_cmd(f"cnvnator -root {root_file} -his {bin_size} -d ./")
    run_cmd(f"cnvnator -root {root_file} -stat {bin_size}")
    run_cmd(f"cnvnator -root {root_file} -partition {bin_size}")
    run_cmd(f"cnvnator -root {root_file} -call {bin_size} > {out_prefix}.cnv.txt")
    return f"{out_prefix}.cnv.txt"

def main():
    parser = argparse.ArgumentParser(description="CNV Detection Pipeline")
    parser.add_argument("-r", "--reference", required=True, help="Reference genome (FASTA)")
    parser.add_argument("-1", "--read1", required=True, help="FASTQ file R1")
    parser.add_argument("-2", "--read2", required=True, help="FASTQ file R2")
    parser.add_argument("-o", "--output", required=True, help="Output prefix")
    parser.add_argument("-b", "--bin", required=True, help="Bin size for CNVnator (e.g., 100 or 500)")
    args = parser.parse_args()

    print("[Step 1] Aligning reads...")
    sam = align_reads(args.reference, args.read1, args.read2, args.output)

    print("[Step 2] Converting SAM to sorted BAM...")
    sorted_bam = process_bam(sam, args.output)

    print("[Step 3] Detecting CNVs using CNVnator...")
    cnv_output = prepare_cnvnator(sorted_bam, args.reference, args.bin, args.output)

    print(f"\n✅ CNV analysis complete. CNVs written to: {cnv_output}")

if __name__ == "__main__":
    main()
