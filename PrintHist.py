#!/usr/bin/env python

import ROOT as R
import sys

if len(sys.argv) < 3:
    print "Usage: PrintHist.py <root-file> <hist-name>"
    sys.exit()

rf = R.TFile(sys.argv[1])

hist = rf.Get(sys.argv[2])

for bin in range(hist.GetNbinsX()):
    print bin+1, hist.GetBinContent(bin+1)
    #print bin+1, hist.GetBinContent(bin+1), hist.GetBinError(bin+1)
