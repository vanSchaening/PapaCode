import sys, os
from tsv import *
from stacksFiles import *
from argparse import ArgumentParser


parser = ArgumentParser(description="Using Stacks output, create pseudo genomes for loci with FST above a given value. For each locus, a .fasta file will be created, with a pseudosequence for each population.")
parser.add_argument("infiles",
                    help = "path to Stacks output files for a batch",
                    type = str)
parser.add_argument("--batch",
                    help = "the name of the batch",
                    required = True,
                    type = str)
parser.add_argument("--outdir",
                    help = "path to the output directory. Will attempt to create it in working directory if it does not exist",
                    type = str,
                    default = None)
parser.add_argument("--fst",
                    help = "minimum fst",
                    type = float,
                    default = 0.5)
parser.add_argument("--snps",
                    help = ".vcf containing SNP information",
                    required = True,
                    type = str)
parser.add_argument("--missing",
                    help = "character to represent missing nucleotides. Default: '-'",
                    type = str)
parser.add_argument("--concatenated",
                    help = "instead of having one sequence per locus per individual, concatenate all the loci for each individual",
                    type = bool)

class Genes:
    #initialize
    def __init__(self):
        self.loci = {}
        self.snps = {}
        self.samples = []
    #increment locus count
    def count_locus(self, locus):
        try:
            self.loci[locus]['count'] += 1
        except KeyError:
            self.loci[locus] = {'count':1}
    #Does a locus exist here?
    def check_locus(self, locus):
        return locus in self.loci
    #Return a list of loci, without additional info
    def fetch_loci(self):
        return self.loci.keys()
    #Store a consensus sequence for a locus
    def add_seq(self, locus, sequence):
        try:
            self.loci[locus]['seq'] = sequence
        except KeyError:
            self.loci[locus] = {'seq':sequence}
    def fetch_seq(self,locus):
        return self.loci[locus]['seq']
    def add_sample(self,name):
        self.samples.append(name)
    def fetch_samples(self):
        return self.samples
    def add_snp(self,locus,position,nucpair):
        self.loci[locus][position] = nucpair
    def fetch_pos(self,locus):
        pos =  self.loci[locus].keys()
        pos.remove('seq')
        pos.remove('count')
        return pos
    def fetch_snp(self,locus,pos):
        return self.snps[(locus,pos)]
    def fetch_vals(self,locus,pos):
        return self.loci[locus][pos]
def filter_by_fst(filelist, val, genes):
    print "Filtering comparisons ..."
    # Filter files by fst, retain values >= val
    results = set()
    for f in filelist:
        data = read_tsv(f)
        for row in data:
            try:
                fst = float(row[8])
            except ValueError:
                continue
            if genes.check_locus(row[1]) or fst >= val:
                results.add((row[1],    #Locus
                             row[2],    #Pop1
                             row[3],    #Pop2
                             row[8],    #FST
                             row[6]))   #Column
                genes.count_locus(row[1])
    # Write results to file
    header = ["Locus","Pop1","Pop2","FST","Column"]
    write_tsv("high_fst_loci.tsv", results, header)
    return results

# Return a string as a list of characters
def listify(word):
    result = []
    for char in word:
        result.append(char)
    return result
# Return a list of characters as a string
def stringify(charlist):
    return "".join(charlist)

# Get consensus sequences and store them by locus 
def get_seqs(seqfile,genes):
    print "Retrieving consensus sequences ..."
    data = read_tsv(seqfile)
    for row in data:
        i=9
        if not row[2] in genes.fetch_loci():
            continue
        while not row[i].startswith(('A','T','C','G')):
            i+=1
        genes.add_seq(row[2],listify(row[i]))


def get_samples(snpfile,genes):
    print "Getting sample names ..."
    try:
        data = open(snpfile)
    except IOError:
        print "Could not open file: ", snpfile
        exit(1)
    for line in data:
        if line.startswith("#CHR"):
            line = line.strip("\n").split("\t")
            for i in range(9,len(line)):
                genes.add_sample(line[i])
            continue
        get_snps(line.strip("\n").split("\t"),
                 genes)
    data.close()

def get_snps(line,genes):
    # Store reference and alternate value for a position in a locus
    if not line[0].startswith("#"):
        loc = line[2]
        pos = line[1]
        pos = int(pos[len(pos)-2:])-1
        if pos < 0: pos+=100
        if loc in genes.fetch_loci():
            genes.add_snp(loc,pos,
                          (line[3],line[4])) #(ref,alt)
    # Store snps for individual samples
        snplist = line[9:]
        for i in range(len(snplist)):
            snplist[i] = snplist[i].split(":")[0]
        genes.snps[(loc,pos)] = snplist

def get_snp_nucs(value, thing, char):
    if thing == "1/1":
        return value[1],value[1]
    if thing == "0/1":
        return value[0],value[1]
    if thing == "1/0":
        return value[1],value[0]
    if thing == "0/0":
        return value[0],value[0]
    if char:
        return char, char
    return "-","-"

def mutate(seq, pos, mut1, mut2):
    seq[pos] = mut1
    seq[pos+100] = mut2

def make_fasta_header(locus,sample):
    return ">" + sample + "| locus=" + locus +"\n"
 
## ------- Main/Testing --------------------------------------------

# Receive command line arguments
args = parser.parse_args()
# Create structure to hold sequence and locus info
genes = Genes()
# Object that handles stacks files
if not args.outdir:
    args.outdir = "pseudogenomes_fst" + str(args.fst)
batchfiles = Files(args.infiles, 
                   args.batch,
                   args.outdir,
                   args.snps)
filter_by_fst(batchfiles.fetch('comparisons'),
              args.fst,
              genes)
get_seqs(batchfiles.fetch('tags'), 
         genes)
get_samples(batchfiles.fetch('snps'),
         genes)

samples = genes.fetch_samples()
if args.concatenated:
    individuals = {sample:[] for sample in samples}

for locus in genes.fetch_loci():
    mutlist = []
    seq = genes.fetch_seq(locus)
    if not args.concatenated:
        out = open(batchfiles.fetch_out() + "pseudo." + locus + ".fasta",'w')
    for i in range(len(samples)):
        pseudo = seq + seq
        for pos in genes.fetch_pos(locus):
            mut1, mut2 = get_snp_nucs(genes.fetch_vals(locus,pos),
                                      genes.fetch_snp(locus,pos)[i],
                                      args.missing)
            mutate(pseudo, pos, mut1, mut2)

        if not args.concatenated:
            header = make_fasta_header(locus,samples[i])
            out.write(header)
            out.write(stringify(pseudo)+"\n")
        else:
            individuals[samples[i]] = individuals[samples[i]] + pseudo
    if not args.concatenated:        
        out.close()


if args.concatenated:
    out = open(batchfiles.fetch_out() + "concatenated.fasta",'w')
    for sample in individuals:
        header = make_fasta_header("(fst>="+str(args.fst)+")",sample)
        out.write(header)
        out.write(stringify(individuals[sample])+"\n")
    out.close()
        
