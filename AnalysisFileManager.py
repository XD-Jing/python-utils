import os
import ROOT as R

class AnalysisFileManager:

    def __init__(self,analysis_tag):
        self.analysis_dir = os.path.expanduser( os.getenv("ZZ_ANAL_DIR") )
        self.analysis_tag = analysis_tag
        self.files = {}

    def __del__(self):
        for file in self.files.values():
            file.Close()

    def GetAnalysisDir(self):
        return self.analysis_dir

    def GetNtupTagDir(self):
        return self.GetAnalysisDir()+"/"+self.analysis_tag

    def GetDsDir(self,ds):
        if type(ds) == type("a"):
            return self.GetNtupTagDir()+"/"+ds
        else:
            return self.GetNtupTagDir()+"/"+ds.name

    # PROJECTS
    # A root file containing HIST (or possibly a tree)
    # One per DS
    def GetProjectDir(self, project,tag):
        return self.GetNtupTagDir()+"/HIST/"+project+"/"+tag

    def GetProjectRootFilePath(self,ds, project, tag):
        if type(ds) == type(""):
            ds_name = ds
        else:
            ds_name = ds.name
        return self.GetProjectDir(project,tag)+"/"+project+"_"+tag+"_"+ds_name+".root"

    def GetProjectRootFile(self,ds, project, tag):
        file_path =  self.GetProjectRootFilePath(ds, project, tag)
        if not file_path in self.files:
            if not os.path.exists( file_path ):
                raise RuntimeError("File not found: "+ file_path )
            self.files[file_path] = R.TFile( file_path )
        return self.files[file_path]

    def MakeProjectDir(self, project, tag):
        if not self.IsProjectDir(project, tag):
            if not os.path.isdir(self.GetNtupTagDir()+"/HIST/"):
                os.mkdir(self.GetNtupTagDir()+"/HIST/")
            if not os.path.isdir(self.GetNtupTagDir()+"/HIST/"+project):
                os.mkdir(self.GetNtupTagDir()+"/HIST/"+project)
            os.mkdir(self.GetProjectDir(project,tag))

    def IsProjectFile(self, ds, project, tag):
        return os.path.exists(self.GetProjectRootFilePath(ds, project, tag))

    def IsProjectDir(self, project,tag):
        return os.path.exists(self.GetProjectDir( project,tag))

    def MakeProjectRootFile(self, ds, project, tag):
        if not self.IsProjectDir( project, tag):
            self.MakeProjectDir( project, tag)
        file_path = self.GetProjectRootFilePath(ds, project, tag)
        self.files[file_path] = R.TFile(file_path, "RECREATE")
        return self.files[file_path]

    # PLOTS
    # Directories containing plots
    def GetPlotDir(self, plotdir):
        return self.GetNtupTagDir()+"/PLOT/"+plotdir

    def GetPlotTagDir(self, plotdir, tag):
        self.MakePlotTagDir(plotdir, tag)
        return self._GetPlotTagDir(plotdir, tag)


    def _GetPlotTagDir(self, plotdir, tag):
        return self.GetNtupTagDir()+"/PLOT/"+plotdir+"/"+tag

    def MakePlotTagDir(self, plotdir, tag):
        if not os.path.isdir(self._GetPlotTagDir(plotdir, tag)):
            if not os.path.isdir(self.GetNtupTagDir()+"/PLOT/"):
                os.mkdir(self.GetNtupTagDir()+"/PLOT/")
            if not os.path.isdir(self.GetPlotDir(plotdir)):
                    os.mkdir(self.GetPlotDir(plotdir))
            os.mkdir(self._GetPlotTagDir(plotdir,tag))

    def SaveCanvasPlot(self, canvas, plotdir, tag):
        self.MakePlotTagDir(plotdir, tag)
        canvas.SaveAs(self.GetPlotTagDir(plotdir,tag)+"/"+canvas.GetName()+".png")
        canvas.SaveAs(self.GetPlotTagDir(plotdir,tag)+"/"+canvas.GetName()+".eps")
        print "Saved plots (.png and .eps) to ", self.GetPlotTagDir(plotdir,tag)
    
    # GATHERED ROOT FILE
    def GetGatheredRootFilePath(self,project, tag):
        return self.GetProjectDir(project, tag)+"/"+project+"_"+tag+"_GATHERED.root"

    def GetGatheredRootFile(self, project, tag):
        file_path =  self.GetGatheredRootFilePath(project, tag)
        if not file_path in self.files:
            if not os.path.exists( file_path ):
                raise RuntimeError("File not found: "+ file_path )
            self.files[file_path] = R.TFile( file_path )
        return self.files[file_path]

    def IsGatheredFile(self, project, tag):
        return os.path.exists(self.GetGatheredRootFilePath( project, tag))

    def MakeGatheredRootFile(self,  project, tag):
        if not self.IsProjectDir( project, tag ):
            self.MakeProjectDir( project, tag )
        file_path = self.GetGatheredRootFilePath(project, tag)
        self.files[file_path] = R.TFile(file_path, "RECREATE")
        return self.files[file_path]

