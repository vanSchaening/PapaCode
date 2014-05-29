Code for the Lionfish project 
========

This repository contains the scripts our lab has written for manipulating the output files from several bioinformatics platforms, mainly from STACKS. Most of the scripts either reconstruct short genome sequences or generate pseudogenomes based on the given input, returning them as .fasta files.

The kinds of pseudogenomes used by our group in this project are the following:
<ul>
</item Concatenations of the sequences for an individual's two alleles for a particular loci.>
</item Instead of concatenating the alleles, using IUPAC ambiguity codes in the SNP positions.>
</item For an individual, concatenating all of the SNPs for selected loci.>
</ul>

Pseudomaker



Magic




Export To Fasta

input:  export data from stacks (usually a file called export_haps.tsv), and optionally a list of loci to filter by.
output: sequences reconstructed based on requests. It can either reconstruct biallelic versions of a locus, with both alleles concatenated, or monoallelic versions using IUPAC ambiguity codes. Instead of reconstructing the whole locus, it can instead make a string of concatenated SNPs.
