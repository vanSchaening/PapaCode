import sys, os, re, types

def fixpath(path):
    if not path.endswith('/'):
        path = path + '/'
    return path

def checkpath(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Files:
    # Create a dictionary of stacks output files
    def __init__(self,infiles,name,out,snpfile):
        print "Finding input files ..."
        self.files = {}
        try:
            fnames = os.listdir(infiles)
        except OSError:
            print "Could not open directory: ", infiles
            print "Exiting ..."
            exit(1)
        self.files['comparisons'] = []
        self.files['outpath'] = fixpath(out)
        self.files['path'] = fixpath(infiles)
        self.files['tags'] = name + ".catalog.tags.tsv" 
        self.files['snps'] = snpfile

        fstpattern = re.compile(name + ".fst_[0-9]")
        for f in fnames:
            if fstpattern.match(f):
                self.files['comparisons'].append(f)
        checkpath(out)

    # Get a file or list of files
    def fullpath(self,f):
        return self.files['path'] + f
    def fetch(self,f):
        result = self.files[f]
        if isinstance(result, types.StringTypes):
            return self.fullpath(result)
        return map(self.fullpath,result)
    def fetch_out(self):
        return self.files['outpath']
