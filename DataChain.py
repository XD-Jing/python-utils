from ROOT import TFile, THStack, TCanvas, TPad, TLatex
from ROOT import gROOT, gStyle, TLegend, TChain
import glob
import ROOT as R

data_chain = TChain('ZZCutsBaseline/FourLepton')
#data_files = glob.glob('analysis/ZZCutsBaseline_03_13_00/Data11_period*/user*/*root*')
data_files = glob.glob('analysis/ZZCutsBaseline_03_18_00/Data11_period*Egamma_WZ/user*/*.output.root*')

for data_file in data_files:
    data_chain.Add(data_file)

#types = {}
#types[0] = '4e'
#types[2] = '4mu'
#types[4] = '2e2mu'
#
#for event in data_chain:
#
#    z0 = []
#
#    if not event.ZZAna_ZZType in [0,2,4]:
#        continue
#
#    if not (event.ZZAna_cutTrigger and event.ZZAna_cutZ1Mass and event.ZZAna_cutZ2Mass):
#        continue
#
#    for i in range(len(event.ZZAna_sel_leptons_index)):
#
#        index = event.ZZAna_sel_leptons_index[i]
#        
#        if (event.ZZAna_sel_leptons_type[i] < 3):
#            z0.append( event.el_trackz0pv[index] )
#        else:
#            z0.append( event.mu_staco_id_z0_exPV[index] )
#
#    print "========= Run %i Event %i Type %s" % (event.RunNumber, event.EventNumber, types[event.ZZAna_ZZType])
#    print "Z01 lepton 1 Z0: %.4f mm lepton 2 Z0: %.4f mm" % (z0[event.ZZAna_Z1_lep1], z0[event.ZZAna_Z1_lep2])
#    print "Z23 lepton 1 Z0: %.4f mm lepton 2 Z0: %.4f mm" % (z0[event.ZZAna_Z2_lep1], z0[event.ZZAna_Z2_lep2])




