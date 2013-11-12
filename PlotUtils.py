import os, pdb
import array
import ROOT as R
import math
import Proc
import RootStyle
import AnalysisFileManager

def SmartRebin(hist, rebin):

    #print hist.GetName(), repr(rebin)

    #pdb.set_trace()

    if type(rebin) == type(1):
        hist.Rebin(rebin)
        return hist
    elif rebin == False:
        return hist
    elif type(rebin) == type([0,1]):
        bins = array.array('d', rebin)

        # Can't rebin past end of hist
        # BadThings TM happen
        # So don't do it
        if bins[-1] > hist.GetXaxis().GetXmax():
            bins[-1] = hist.GetXaxis().GetXmax()
        hist.SetBit(R.TH1.kCanRebin)
        newhist = hist.Rebin(len(rebin)-1, hist.GetName(), bins)

        return newhist
    else:
        raise RuntimeError("Don't understand rebin variable"+ str(rebin))
    #pdb.set_trace()

# Very lightweight "Stack plot" class returned by the main method
# Gives the calling code access to e.g. the pads and stops
# stuff going out of scope
class StackPlot:

  def __init__(self, plotPad, ratioPad, stack, h_data, h_ratio, legend, label, h_stack_total):

    self.plotPad = plotPad
    self.ratioPad = ratioPad
    self.stack = stack
    self.h_data = h_data
    self.h_ratio = h_ratio
    self.legend = legend
    self.label = label
    self.h_stack_total = h_stack_total

# The main class for getting plots and drawing stackplots
class PlotGetter:

  # analysis_tag tells it which 'version' of results to use
  # lumi is the integrated luminosity to normalise to 
  # if ofile is set will write all of the normalised plots to a root file
    def __init__(self, AM, lumi, ofile = "", analysis_dir = "", useSameFileForNorm=False, fromGatheredFile=False, debug=False, sumw2=False):
        self.lumi = lumi
        self.files = {}
        self.useSameFileForNorm = useSameFileForNorm
        self.fromGatheredFile = fromGatheredFile
        self.debug = debug
        self.sumw2 = sumw2

        # for backwards compatability
        if type(AM) == type(""):
            print "WARNING: Passing tup_tag to PlotGetter is depreciated. Please pass file_manager as first argument to PlotGetter.__init__!"
            self.AM = AnalysisFileManager.AnalysisFileManager(AM)
        else:
            self.AM = AM

        if ofile:
            self.write_output = True
            self.ofile = R.TFile(ofile,"RECREATE")
        else:
            self.write_output = False

        #print "Writing Output: ", self.write_output

    # Gather plots from different ds files to one file, one plot per ds, no normalisation
    def GatherRawPlots(self, project, tag, rf_out, procs, hname, outname):

        all_datasets = []
        h_data = False

        for proc in procs:
            all_datasets += proc.datasets

        for ds in all_datasets:
            outdsname = ds.name.split('.')[-1]
            if ds.isMC:
                rf_out.cd()
                h = self.GetHist(self.AM.GetProjectRootFile(ds, project, tag),hname).Clone(outname+'_'+outdsname)
                rf_out.cd()
                #print "Writing ",h.GetName()
                h.Write()
            else:

                htmp = self.GetHist(self.AM.GetProjectRootFile(ds, project, tag),hname).Clone(outname+'_'+outdsname)
                
                if h_data:
                    h_data.Add(htmp )
                    h_data = htmp.Clone(outname+'_Data')

                #htmp.Delete()

        if h_data:
            rf_out.cd()
            h_data.Write()

    def GatherByProc(self, project, tag, proc, hname, outname, normalise = True):

        h = self.GetHistogram( project, tag, proc, hname, rescale = False, useKfactor = 1, normalise=normalise)
        rf_out = AM.MakeProjectRootFile(proc, project, tag)
        h.Write(outname)
        rf_out.Close()

    def GetHistogramFromGatheredFile(self, project, tag, proc, hname):
        hname_proc = hname + "_" + proc.name
        myhist = self.GetHist(self.AM.GetGatheredRootFile(project,tag), hname_proc)
        return myhist

    def GetDsSF(self, ds, useKfactor, project, tag):

        # If proj / tag specified, use that file
        # else default to grid output
        if self.useSameFileForNorm:
            h_nevents = self.GetHist(self.AM.GetProjectRootFile(ds, project, tag),'general_cutflow')
        else:
            h_nevents = self.GetHist(self.AM.GetProjectRootFile(ds, "GridOutput", "00"),'general_cutflow')

        nevents = h_nevents.GetBinContent(6)
        #h_nevents.Delete()
        #print h.GetName(), h.GetEntries(), nevents

        kfactor = 1.0

        #print "useKfactor", useKfactor

        if useKfactor==1 and "kfactor" in ds.__dict__:
            kfactor = ds.kfactor
        elif useKfactor==2 and "kfactor2" in ds.__dict__:
            kfactor = ds.kfactor2

        if self.lumi == -1:
          # Normalise to unit luminosity here
          # Then normalise to unit area once all of the datasets have been added together
          sf = 1. * ds.cx * kfactor * ds.filter_eff / nevents
        else:
          sf = self.lumi * ds.cx * kfactor * ds.filter_eff / nevents
          
        if (self.debug): print "SF for ",ds.name,sf
        return sf

    def GetHistogramFromDsFiles(self, project, tag, proc, hname, useKfactor, normalise):

        #print  project, tag, proc.name, hname

        ds = proc.datasets[0]
        #print "Getting", hname, ds.name
        htmp = self.GetHist(self.AM.GetProjectRootFile(ds, project, tag),hname)
        #print "Dataset ", ds.name


        R.gROOT.cd()

        if self.write_output:
            self.ofile.cd()

        #pdb.set_trace()
        h = htmp.Clone(hname.split("/")[-1]+'_'+proc.name.replace("/","").replace("+",""))
        #htmp.Delete()
        if self.sumw2:
            h.Sumw2() 

        if ds.isMC:
            if normalise:
                #print "%s %s Before normalisation %.2f" % (hname, ds.name, h.Integral())
                h.Scale(self.GetDsSF( ds, useKfactor, project, tag) )
                #print "%s %s After normalisation %.2f" % (hname, ds.name, h.Integral())

        # Add the other histograms in the same process, if need be
        for i in range(1, len(proc.datasets)):
            ds = proc.datasets[i]
            #print "Opening",  self.analysis_dir+'/'+self.analysis_tag+'/'+ds.name+'/merged/'+filename
            htmp = self.GetHist(self.AM.GetProjectRootFile(ds, project, tag),hname)
            #print "%s %s Before normalisation %.2f" % (hname, ds.name, htmp.Integral())
            #print "Dataset ", ds.name

            if not bool(htmp):
                raise RuntimeError("Histogram "+ hname+ " not found in file "+ self.AM.GetProjectRootFile(ds, project, tag).GetName())

            # The reason to add with sf not scale is we don't want to scale the histogram 
            # in the file memory incase we want to use it again
            sf = 1
            if ds.isMC:
                if normalise:
                    sf = self.GetDsSF( ds, useKfactor, project, tag) 
                    #print "%s %s After normalisation %.2f" % (hname, ds.name, htmp.Integral()*sf)

            #print htmp.GetEntries()
            #print htmp.GetXaxis().GetXmax(), htmp.GetXaxis().GetXmin()
            if self.sumw2:
                htmp.Sumw2() 
            h.Add(htmp, sf)
            #htmp.Delete()

        if normalise:
            # Normalise to unit area, both for MC and data
            if self.lumi == -1:
            
              if h.Integral():
                  sf = 1. / h.Integral()
              else:
                  sf = 1. 

              h.Scale(sf)

        return h


         
    # Given a process name, project, tag and histogram name, will return the properly normalised histogram
    def GetHistogram(self, project, tag, proc, hname, rescale = False, useKfactor = 1, normalise=True, rebin = 1):

        #pdb.set_trace()

        if type(hname) != type([]):
            hname_list = [hname,]
        else:
            hname_list = hname

        hist = False

        proc = self.BuildProc(proc)

        for hname in hname_list:
            if self.fromGatheredFile:
                htmp = self.GetHistogramFromGatheredFile(project, tag, proc, hname)

            else:
                htmp = self.GetHistogramFromDsFiles(project, tag, proc, hname, useKfactor , normalise)

            #pdb.set_trace()
            if not hist:
                hist = htmp
            else:
                hist.Add(htmp)
                #htmp.Delete()

        if rescale:
            xmax = hist.GetXaxis().GetXmax()
            xmin = hist.GetXaxis().GetXmin()
            hist.GetXaxis().SetLimits(xmin/1000., xmax/1000.)

        if not proc.datasets[0].isData:
            hist.SetFillColor(proc.colour)
            hist.SetLineColor(proc.colour)
            hist.SetMarkerColor(proc.colour)
        else:
            hist.SetMarkerStyle(20)
            hist.SetLineColor(R.kBlack)
            hist.SetMarkerColor(R.kBlack)

        if self.write_output:
            self.ofile.cd()
            hist.Write()

        if rebin != 1:
            hist = SmartRebin(hist, rebin)

        if (self.debug): print hist.GetName(), hist.Integral()
        return hist


    def GetHist(self,file, hname):
        # FIXME
        #print hname, file.GetName()
        if hname in file.GetListOfKeys() or "/" in hname:
            hist = file.Get(hname)
            R.SetOwnership(hist, True)
            if hist.__nonzero__():
                return hist
            else:
                raise RuntimeError("ERROR: Hist"+ hname+ " appears to be not found in file "+ file.GetName())

        else:
            raise RuntimeError("ERROR: Hist", hname, " not found in file ", file.GetName())

    # Legacy support for passing proc names as strings: build PRoc object
    def BuildProc(self, proc):

        if proc.__class__ == Proc.Proc:
            return proc
        elif type(proc) == type(""):
            # build Proc object
            raise RuntimeError("Please pass proc object not string")
            return Proc.Proc(proc, datasets, datasets[0].colour, proc )
        else:
            pdb.set_trace()
            raise RuntimeError("Can't understand proc type: "+str(type(proc)))

# Very simple function, pass it a list of histograms and a delta X and it plots them all on the same
# axis with (n-1)*delta_x applied to all histograms after the first
def ShiftedPlot(histograms, delta_x): 

    #R.gStyle.SetErrorX(0)

    histograms[0].Draw("PE1")
    
    n = 1
    graphs = []

    for hist in histograms[1:]:

        graph = R.TGraphAsymmErrors(hist)
        R.SetOwnership(graph,0)

        if n & 1 :
            dx = delta_x * n
        else:
            dx = -1 *( delta_x * (n-1))

        #print dx

        for point in range(graph.GetN()):

            x,y = R.Double(), R.Double()

            graph.GetPoint(point,x,y)
            graph.SetPoint(point,x+dx,y)

        graph.Draw("same,P")
        graphs.append(graph)

        n+=1

    return graphs

# Get the *true* histogram of a list of histograms
# ie, including errors
def GetTrueMaximumHist(hists):

    maxhist = hists[0].Clone("MAX")
    maxhist.Reset()

    for iBin in range(0, maxhist.GetNbinsX()):
        ymax = 0
        content = 0
        error = 0

        for hist in hists:
            height = hist.GetBinContent(iBin+1) + hist.GetBinError(iBin+1)

            if height > ymax:
              ymax = height
              content = hist.GetBinContent(iBin+1)
              error = hist.GetBinError(iBin+1)

        maxhist.SetBinContent(iBin+1, content)
        maxhist.SetBinError(iBin+1, error)

    return maxhist


# Get the *true* maximum of a histogram
# ie, including errors
def GetTrueMaximum(hist, bin_min=0, bin_max=-1):

    ymax = 0

    if bin_max == -1:
        bin_max = hist.GetNbinsX()

    for bin in range(bin_min, bin_max):

        height = hist.GetBinContent(bin+1) + hist.GetBinError(bin+1)

        if height > ymax:
            ymax = height

    return ymax

