import csv

def read_tsv(filename, skip=True):
    try:
        myfile = open(filename)
        data = csv.reader(myfile, delimiter="\t", quotechar="|")
    except IOError:
        print "Could not open file: ", filename
        print "Exiting ..."
        exit(1)
    if skip:
        data.next()
    return data

def write_tsv(filename, olist, hlist=False):
    try:
        o = open(filename, 'a')
        writer = csv.writer(o, delimiter="\t",quotechar="|")
    except:
        sys.exit("Could not write contents to file.")

    if hlist:
        writer.writerow(hlist)
    for row in olist:
        writer.writerow(row)
    o.close()
