#!/usr/bin/env python
import sys, glob, os

if len(sys.argv) < 3:
    sys.exit("Usage: phadd <output_file> <input file1> <input_file2...>")

ofile = sys.argv[1]

files_list_raw = sys.argv[2:]

maxperjob = 500

# glob files_list_raw to get list of input files
files_list = []

for pattern in files_list_raw:
    files_list += glob.glob(pattern)

if len(files_list) < maxperjob:
    # simple case, just call hadd
    files_string = " ".join(files_list)
    os.system("hadd -f "+ofile+" "+files_string)

else:

    iFile =0
    nFiles = len(files_list)
    print "nFiles",nFiles
    nJobs = nFiles / maxperjob + 1
    print "nJobs",nJobs

    for iJob in range(nJobs):
        upperIndex = (iJob+1)*maxperjob
        if upperIndex > nFiles:
            upperIndex = nFiles
        files_string = " ".join(files_list[iJob*maxperjob:upperIndex])
        print "hadd -f phadd_TMP"+str(iJob)+".root "+files_string
        os.system("hadd -f phadd_TMP"+str(iJob)+".root "+files_string)

    print "hadd -f "+ofile+" phadd_TMP*.root"
    os.system("hadd -f "+ofile+" phadd_TMP*.root")
    os.system("rm phadd_TMP*.root")
