#!/usr/bin/env python3

"""
long_read_sv_pipeline.py

A pipeline for structural variant (SV) detection using long-read sequencing data (e.g., Nanopore/PacBio).
Steps:
    1. Index reference genome (Minimap2)
    2. Align long reads to reference (Minimap2)
    3. Sort and index BAM file (SAMtools)
    4. Call SVs (Sniffles2)

Usage:
    python long_read_sv_pipeline.py -r ref.fa -i longreads.fastq -o output_prefix
"""

import os
import argparse
import subprocess

def run_cmd(cmd):
    """Run a shell command and print it."""
    print(f"[Running] {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def index_reference(ref_path):
    """Index reference genome with Minimap2 and SAMtools."""
    run_cmd(f"minimap2 -d {ref_path}.mmi {ref_path}")
    run_cmd(f"samtools faidx {ref_path}")

def align_long_reads(ref_mmi, reads, out_prefix):
    """Align long reads using Minimap2."""
    paf_output = f"{out_prefix}.paf"
    bam_output = f"{out_prefix}.bam"
    run_cmd(f"minimap2 -ax map-ont {ref_mmi} {reads} | samtools view -b - > {bam_output}")
    return bam_output

def sort_and_index_bam(bam, out_prefix):
    """Sort and index BAM file."""
    sorted_bam = f"{out_prefix}.sorted.bam"
    run_cmd(f"samtools sort {bam} -o {sorted_bam}")
    run_cmd(f"samtools index {sorted_bam}")
    return sorted_bam

def call_svs(sorted_bam, ref, out_prefix):
    """Call structural variants with Sniffles2."""
    vcf_file = f"{out_prefix}.sv.vcf"
    run_cmd(f"sniffles --input {sorted_bam} --vcf {vcf_file} --reference {ref}")
    return vcf_file

def main():
    parser = argparse.ArgumentParser(description="Structural Variant Detection Pipeline (long reads)")
    parser.add_argument("-r", "--reference", required=True, help="Reference genome FASTA")
    parser.add_argument("-i", "--input", required=True, help="Long-read FASTQ file")
    parser.add_argument("-o", "--output", required=True, help="Output prefix")
    args = parser.parse_args()

    ref = args.reference
    reads = args.input
    prefix = args.output

    print("[Step 1] Indexing reference...")
    index_reference(ref)

    print("[Step 2] Aligning long reads...")
    bam = align_long_reads(ref + ".mmi", reads, prefix)

    print("[Step 3] Sorting and indexing BAM...")
    sorted_bam = sort_and_index_bam(bam, prefix)

    print("[Step 4] Calling SVs with Sniffles2...")
    vcf = call_svs(sorted_bam, ref, prefix)

    print(f"\n✅ Pipeline complete. Final VCF: {vcf}")

if __name__ == "__main__":
    main()
