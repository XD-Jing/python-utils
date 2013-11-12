import pdb
import os
from ROOT import TFile, TChain
import ROOT as R
import glob
import Proc

analysis_dir = os.getenv("ZZ_ANAL_DIR")

flfilename = "FourLepton_ntuple.root"
fltreename = "FourLepton"

tlfilename = "TwoLepton_ntuple.root"
tltreename = "TwoLepton"

fffilename = "FFNtuple.root"
fftreename = "FakeFactor"


def GetFourLeptonTree(analysis_tag, ds, project=None, tag=None, chunk=None):
    return _GetTree(analysis_tag, ds, flfilename, fltreename, chunk)

def GetTwoLeptonTree(analysis_tag, ds, project=None, tag=None, chunk=None):
    return _GetTree(analysis_tag, ds, tlfilename, tltreename, chunk)

def GetFakeFactorTree(analysis_tag, ds, project=None, tag=None, chunk=None):
    return _GetTree(analysis_tag, ds, fffilename, fftreename, chunk)

def _GetTree(analysis_tag, ds, filename, treename, chunk):

    datasets = []
    if isinstance(ds,Proc.Proc):
        datasets = ds.datasets
    else:
        datasets = [ds,]

    c = TChain(treename)

    for ds in datasets:
        print analysis_tag, ds.name
        files = glob.glob(analysis_dir+"/"+analysis_tag+"/"+ds.name+"/user*/*"+filename+"*")
        files += glob.glob(analysis_dir+"/"+analysis_tag+"/"+ds.name+"/*"+filename+"*")

        files.sort()
        #pdb.set_trace()

        for iFile in range(len(files)):
            #print "Adding ", files[iFile]
            #print iFile, len(files)
            c.Add(files[iFile])

    size = R.Long(100e6)
    c.SetCacheSize(size)
    c.SetCacheLearnEntries(20)

    return c

def GetFourLeptonTree2(analysis_tag, name):

    c = TChain(fltreename)
    files = glob.glob(analysis_dir+"/"+analysis_tag+"/"+name+"/user*/*"+flfilename+"*")
    files += glob.glob(analysis_dir+"/"+analysis_tag+"/"+name+"/*"+flfilename+"*")
    print "NFiles", len(files)

    for rf in files:
        #print "Adding ", rf
        c.Add(rf)

    return c
