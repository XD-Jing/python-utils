import AddInQuad
import ROOT as R
import pdb
import PlotUtils
import math
from initFromArgs import initFromArgs

nice_colours = [1,2,3,4,6,7,8,9]
nice_markers = [20,21,22,23,24,25,26,27,28]

class PlotElement:

    # type is "stack", "hist"
    # legend entries is a LIST since stacks need multiple entries
    def __init__(self, hist, type, legend_entries, drawOpt, legOpt, stack_hists = None):

        if isinstance(hist, R.THStack):
            self.rootobj = hist
            self.hists = stack_hists
            if not len(stack_hists):
                raise RuntimeError("Need to pass in stack_hists")
            #self.total_hist = hist
            self.totalhist = self.hists[0].Clone(self.hists[0].GetName()+"_STACKMAX")
            for hist in self.hists[1:]:
                self.totalhist.Add(hist)
        else:
            self.rootobj = hist
            self.totalhist = hist
            self.hists = [hist,]
            #self.total_hist = hist

        self.drawOpt = drawOpt
        self.legOpt = legOpt
        self.legend_entries = legend_entries
        self.type = type

    def GetTotalHist(self):
        
        return self.totalhist

    def GetMax(self):
        
        return PlotUtils.GetTrueMaximum(self.totalhist)


class MultiPlot:

    def __init__(self, plot_getter=None, xlabel="", ylabel="", xrangelow=None, xrangehigh=None, draw_ratio = False, ratio_yhigh = 2, ratio_ylow=0.5, linear=True, lumi_label = "", atlas_label = "", systematic = False, cutLines=[], ratio_ylabel="Ratio", axis_label_size=0.05, text_size=0.05, ecm_label="", ratio_pad_height = 0.4, rebin=1, ymin_lin = 0.001, ymin_log=0.01, y_max_sf_user=-1, text_font = 42, leg_line_spacing=1.1, label_line_spacing=1.4, leg_width = 0.18, label_width = 0.22, auto_sort=True, stack_drawOpt="hist", stack_legOpt="f", leg_bot_padding=0, leg_ymin_min=0.65, leg_text_size=None, right_margin=0.05, left_margin=0.12, bottom_margin=0.15, y_axis_title_offset=1.05, debug=False, add_syst_leg = True, label_text_size=None ):

        #self.AM = AM
        initFromArgs(self)

        self.plot_elements = []
        self.iColour = 0
        self.iMarker = 0
        self.labels = []
        self.leg_axis_offset = 0.03
        self.stack_labels = []
        self.stack_hists = {}

        if not self.leg_text_size:
            self.leg_text_size = self.text_size * 0.9

        if lumi_label:
            self.AddLabel("#scale[0.7]{#int}L#kern[0.2]{dt} = "+lumi_label)
        if ecm_label:
            self.AddLabel("#sqrt{s} = "+ecm_label)

        if not self.draw_ratio:
            self.ratio_pad_height = 0

        # Stores FRACTIONAL variation
        self.flat_syst_frac = 0.0
        self.stack_syst_abs_hists = []
        self.stack_err_hist_has_systematic = False
        self.stack_err_hist = False

    def AddFlatSystBandFrac(self, frac):
        self.flat_syst_frac = math.sqrt(self.flat_syst_frac * self.flat_syst_frac + frac*frac)
        self.stack_err_hist_has_systematic = True

    # Systematics should be in bin errors in absolute terms
    def AddSystBandAbsHist(self, abs_hist):
        self.stack_err_hist_has_systematic = True
        self.stack_syst_abs_hists.append(abs_hist) 


    def AddHist(self, hist, label, drawOpt, legOpt, marker_style=False, marker_size=-1, colour=False, fill=0, rescale=False, recolour=True, line_width=1, line_style=1):

        if marker_size>-1:
            hist.SetMarkerSize(marker_size)

        if not marker_style:
            marker_style = nice_markers[self.iMarker]
            self.iMarker +=1

        hist.SetMarkerStyle(marker_style)
        hist.SetLineWidth(line_width)
        hist.SetLineStyle(line_style)

        #print marker_size, 

        if recolour:
            if not colour:
                colour = nice_colours[self.iColour]
                self.iColour +=1
            hist.SetMarkerColor(colour)
            hist.SetLineColor(colour)
            hist.SetFillColor(colour)

        hist.SetFillStyle(fill)

        element = PlotElement(hist,  "hist", [label,], drawOpt, legOpt)
        self.plot_elements.append(element)

    def AddHistFromProc(self, hname, project, tag, proc, drawOpt, legOpt, marker_style=False, marker_size=False, colour=False, fill=0, rescale=False, recolour=False, line_width=1, line_style=1):

        hist = self.plot_getter.GetHistogram(project, tag, proc, hname, rescale,rebin=self.rebin)

        if marker_size:
            hist.SetMarkerSize(marker_size)

        if not marker_style:
            marker_style = nice_markers[self.iMarker]
            self.iMarker +=1

        hist.SetMarkerStyle(marker_style)
        hist.SetLineWidth(line_width)
        hist.SetLineStyle(line_style)

        if recolour:
            if not colour:
                colour = nice_colours[self.iColour]
                self.iColour +=1
            hist.SetMarkerColor(colour)
            hist.SetLineColor(colour)
            hist.SetFillColor(colour)

        hist.SetFillStyle(fill)

        element = PlotElement(hist,  "hist", [proc.label,], drawOpt, legOpt)
        self.plot_elements.append(element)

    def AddStackElementFromHist(self, hist, label, marker_style=0, marker_size=0, colour=False, fill=1001, rescale=False, recolour=False, line_width=1, line_style=1, line_colour = 1, flat_syst=None):

        self.stack_hists[label] = hist
        self.stack_labels.append(label)

        if marker_size:
            hist.SetMarkerSize(marker_size)

        if not marker_style:
            marker_style = nice_markers[self.iMarker]
            self.iMarker +=1

        hist.SetMarkerStyle(marker_style)
        hist.SetLineWidth(line_width)
        hist.SetLineStyle(line_style)
        hist.SetLineColor(line_colour)

        if recolour:
            colour = nice_colours[self.iColour]
            self.iColour +=1

        if colour:
            hist.SetMarkerColor(colour)
            hist.SetFillColor(colour)

        hist.SetFillStyle(fill)

        if flat_syst:
            self.stack_err_hist_has_systematic = True
            for bin in range(1,hist.GetNbinsX()):
                content = hist.GetBinContent(bin)
                stat = hist.GetBinError(bin)
                err =  AddInQuad.AddInQuad([flat_syst * content, stat])
                hist.SetBinError(bin, err)

    def AddStackElementsFromProcs(self, hname, project, tag, procs, marker_style=0, marker_size=0, colour=False, fill=1001, rescale=False, recolour=False, line_width=1, line_style=1, line_colour = 1, flat_syst = None):

        hists = {}

        for proc in procs:
            hist = self.plot_getter.GetHistogram(project, tag, proc, hname, rescale,rebin=self.rebin)

            self.AddStackElementFromHist(hist, proc.label, marker_style, marker_size, colour, fill, rescale, recolour, line_width, line_style, line_colour, flat_syst)

    def _finaliseStack(self):

        stack = R.THStack("stack", "stack")

        if self.auto_sort:
            sorted(self.stack_labels, key = lambda x: -1*PlotUtils.GetTrueMaximum(self.stack_hists[x]))

        hists_reversed = []
        first = True
        bins = []

        stackXmax = 9999999

        for hist in  self.stack_hists.values():
            if hist.GetXaxis().GetXmax() < stackXmax: 
                stackXmax = hist.GetXaxis().GetXmax()

        for label in self.stack_labels:
            #self.stack_hists[label].GetXaxis().SetLimits(self.xrangelow, self.xrangehigh)

            if first:

                # If we have a pilot hist, use it for binning template
                # If not use first stack element
                if self.pilot_hist:
                    bin_hist = self.pilot_hist
                else:
                    bin_hist = self.stack_hists[label]

                for bin in range(bin_hist.GetNbinsX()):
                    if bin_hist.GetBinLowEdge(bin+1) > stackXmax: continue
                    bins.append(bin_hist.GetBinLowEdge(bin+1))
                if bin_hist.GetBinLowEdge(bin+1) <= stackXmax:
                    bins.append(bin_hist.GetBinLowEdge(bin+1)+bin_hist.GetBinWidth(bin+1))
                first = False
                #print repr(bins)

            #print self.stack_hists[label].
            #pdb.set_trace()
            self.stack_hists[label] = PlotUtils.SmartRebin(self.stack_hists[label], bins)

            stack.Add(self.stack_hists[label], self.stack_drawOpt)
            hists_reversed.append(self.stack_hists[label])

        labels_reversed = list(self.stack_labels)
        labels_reversed.reverse()
        hists_reversed.reverse()

        #pdb.set_trace()

        element = PlotElement(stack,  "stack", labels_reversed, self.stack_drawOpt, self.stack_legOpt, hists_reversed)
        self.plot_elements.append(element)

        # Make stack error band
        self.stack_err_hist = element.totalhist.Clone("stack_err")
        #pdb.set_trace()
        
        if self.flat_syst_frac:
            print "Adding flat systematic"
            for bin in range(1,self.stack_err_hist.GetNbinsX()+1):
                if self.stack_err_hist.GetBinContent(bin):
                    stat_frac = self.stack_err_hist.GetBinError(bin) / self.stack_err_hist.GetBinContent(bin)
                    total_err_frac = AddInQuad.AddInQuad([stat_frac,self.flat_syst_frac])
                    total_err_abs = total_err_frac * self.stack_err_hist.GetBinContent(bin)
                    self.stack_err_hist.SetBinError(bin, total_err_abs)

        if len(self.stack_syst_abs_hists):
            print "Adding systematic from abs hist"
            for abs_hist in self.stack_syst_abs_hists:
                for bin in range(1,self.stack_err_hist.GetNbinsX()+1):
                    if self.stack_err_hist.GetBinContent(bin):
                        old_err = self.stack_err_hist.GetBinError(bin) 
                        abs_hist_err = abs_hist.GetBinError(bin)
                        new_err = AddInQuad.AddInQuad([old_err,abs_hist_err])
                        #print self.stack_err_hist.GetBinContent(bin), old_err, abs_hist_err, new_err
                        self.stack_err_hist.SetBinError(bin, new_err)

    def AddLabel(self, text):
        self.labels.append(text)

    def Draw(self, sortByMax=True):

        self.pilot_hist = None

        if len( self.plot_elements ) :
            self.pilot_hist = self.plot_elements[0].hists[0].Clone("PILOT")
            self.pilot_hist.Reset()

        # Needs pilot hist if posible
        if self.stack_hists:
            self._finaliseStack()

        # Make max and pilot hist
        #pdb.set_trace()
        self.maxhist = PlotUtils.GetTrueMaximumHist([x.GetTotalHist() for x in self.plot_elements])
        if self.pilot_hist:
            self.pilot_hist = self.plot_elements[0].hists[0].Clone("PILOT")
            self.pilot_hist.Reset()

        if not self.xrangehigh:
            self.xrangelow = self.pilot_hist.GetXaxis().GetXmin()
            self.xrangehigh = self.pilot_hist.GetXaxis().GetXmax()

        self.MakePads()
        self.PlaceLegendSetYmax()

        self.PrepareElements()

        elements = self.SortElements(sortByMax)

        self.pad_histogram.cd()
        self.DrawElements(elements)

        if self.draw_ratio:
            self.pad_ratio.cd()
            self.DrawRatioPlot()

        self.pad_histogram.cd()
        self.DrawLegend(elements)
        self.DrawLabels()



    def DrawLabels(self):

      if not self.label_text_size:
          text_size = self.leg_text_size
      else:
          text_size = self.label_text_size

      tlatex = R.TLatex()
      tlatex.SetNDC()
      tlatex.SetTextFont(self.text_font)
      tlatex.SetTextSize(text_size/ (1-self.ratio_pad_height))
      tlatex.SetTextColor(1)

      line_height = self.label_line_spacing * text_size/ (1-self.ratio_pad_height)
      cur_y = self.leg_ymax - line_height*0.75

      # ATLAS label first
      if self.atlas_label:
          tlatex.DrawLatex(self.label_xmin, cur_y,"#font[72]{ATLAS} "+self.atlas_label)
          cur_y -= line_height
          #tlatex.DrawLatex(self.label_xmin, cur_y,"ATLAS")
          #tlatex.SetTextFont(self.text_font)

      for label in self.labels:
          tlatex.DrawLatex(self.label_xmin,cur_y,label)
          cur_y -= line_height
      
      self.tlatex = tlatex
      #pdb.set_trace()

    def PlaceLegendSetYmax(self):

        self.leg_ymax = 0.91

        penalty_l = 0.5

        # Figure out leg height and set y_min
        n_elements = sum([len(x.hists) for x in self.plot_elements])
        self.leg_ymin = self.leg_ymax - (self.leg_text_size*self.leg_line_spacing/ (1-self.ratio_pad_height))*(n_elements)
        #print "Leg line spacing ", self.leg_line_spacing, self.leg_ymin

        n_labels = len(self.labels) + int(bool(self.atlas_label))
        if (self.debug): print "n_labels",n_labels, "hasATLASlabel? ", int(self.atlas_label!="")

        self.label_ymin = self.leg_ymax -(self.leg_text_size*self.label_line_spacing/ (1-self.ratio_pad_height))*(n_labels)

        #print self.label_ymin

        if self.leg_ymin < self.leg_ymin_min and not self.draw_ratio:
          self.leg_ymin = self.leg_ymin_min

        if self.y_max_sf_user < 0:
            # Need to figure it out for ourselves to fit in legend

            # 1. Find legend width in bins, height in pad-cord

            y_max_sf_l = self.GetMaxSf(self.leg_width, self.leg_ymin - self.leg_bot_padding, True)
            y_max_sf_r = self.GetMaxSf(self.leg_width, self.leg_ymin - self.leg_bot_padding, False)

            if ( y_max_sf_l * (1+penalty_l)) < y_max_sf_r:
                # is on left
                self.y_max_sf =  y_max_sf_l
                self.leg_xmax =  self.pad_histogram.GetLeftMargin() + self.leg_width + self.leg_axis_offset
                self.leg_xmin = self.pad_histogram.GetLeftMargin() + self.leg_axis_offset

                self.label_xmin = self.pad_histogram.GetRightMargin() - self.leg_axis_offset - self.label_width
                y_max_sf_label = self.GetMaxSf(self.label_width,self.label_ymin,  False)
                if y_max_sf_label > self.y_max_sf:
                    self.y_max_sf = y_max_sf_label

            else:
                # is on right
                self.y_max_sf = y_max_sf_r
                self.leg_xmax =  1 - self.pad_histogram.GetRightMargin() - self.leg_axis_offset
                self.leg_xmin = self.leg_xmax - self.leg_width - self.leg_axis_offset

                self.label_xmin = self.pad_histogram.GetLeftMargin() + self.leg_axis_offset
                y_max_sf_label = self.GetMaxSf(self.label_width, self.label_ymin, True)
                if y_max_sf_label > self.y_max_sf:
                    self.y_max_sf = y_max_sf_label
            #print self.y_max_sf

        else:

            # Just put legend in default place

            self.y_max_sf = self.y_max_sf_user
            self.leg_xmax =  1 - self.pad_histogram.GetRightMargin()- self.leg_axis_offset
            self.leg_xmin = self.leg_xmax - self.leg_width

            self.label_xmin = self.pad_histogram.GetLeftMargin() + self.leg_axis_offset
    
    def GetMaxSf(self, width,  ymin, isL):


        # Convert width in pad-frac to NBins
        width_axis =  1 - (self.pad_histogram.GetLeftMargin() + self.pad_histogram.GetLeftMargin())
        nbins = self.pilot_hist.FindBin(self.xrangehigh) - self.pilot_hist.FindBin(self.xrangelow)  + 1
        #print "nbins=",nbins
        bin_width_frac = width_axis / nbins
        legend_width_bins = int(math.ceil((width+self.leg_axis_offset) / bin_width_frac) + 1)

        # 2. Figure out if best on L or R
        if isL:
            #print self.pilot_hist.FindBin(self.xrangelow) + legend_width_bins
            max_range = PlotUtils.GetTrueMaximum(self.maxhist, self.pilot_hist.FindBin(self.xrangelow)-1, self.pilot_hist.FindBin(self.xrangelow) + legend_width_bins )
        else:
            max_range = PlotUtils.GetTrueMaximum(self.maxhist, self.maxhist.FindBin(self.xrangehigh) - legend_width_bins, self.maxhist.FindBin(self.xrangehigh) )

        # 3. Find height of highest bin in range
        # fiigure how much need to scale it down by

        #print width, ymin, isL, max_range

        if max_range == 0 :
            return 1
        else:
            if self.linear == False:
                ndivs_below_1 = -1 * math.log10(self.ymin_log)
                ndivs_max = math.log10(PlotUtils.GetTrueMaximum(self.maxhist)) + ndivs_below_1
                ndivs_max_range = math.log10(max_range) + ndivs_below_1
                y_max_sf = ndivs_max_range / (ndivs_max*(ymin-0.03))
            else:
                y_max_sf =  max_range/(PlotUtils.GetTrueMaximum(self.maxhist) * (ymin-0.03))

        #print y_max_sf 
        return y_max_sf



    def PrepareElements(self):
        

        y_max = PlotUtils.GetTrueMaximum(self.maxhist)
        #print y_max

        #y_max_sf_min = 0
        y_max_sf_min = 1.1

        if y_max<=0:
            print "***---> Uh oh, y_max <=0, BadThings(TM) might happen..."
            print "   ---> Setting y_max =1, will se what happens..."
            y_max = 1

        if self.y_max_sf < y_max_sf_min:
            print "Using minimum SF of 1.1"
            self.y_max_sf = y_max_sf_min


        if self.linear:
            self.ymax = y_max * self.y_max_sf
            # Non-zero to supress first Axis label ("0")
            self.ymin = self.ymin_lin
        else:
            # Sets maximum such that is same height as on linear scaqle
            ndivs_below_1 = -1 * math.log10(self.ymin_log)
            self.ymax = 10**((ndivs_below_1+math.log10(y_max))*self.y_max_sf-ndivs_below_1)
            self.ymin = self.ymin_log * 1.00001

        #print self.ymin,  self.ymax, self.y_max_sf

        ########################################
        # Set minimum and maximum for pilot hist

        self.pilot_hist.SetMaximum( self.ymax )
        self.pilot_hist.SetMinimum( self.ymin )

        # Set minimum and maximum for pilot hist
        # Set Range for pilot hist
        if not self.xrangelow == None:
            self.pilot_hist.GetXaxis().SetRangeUser(self.xrangelow, self.xrangehigh)
        ########################################

        self.pilot_hist.GetYaxis().SetTitleFont(self.text_font)
        self.pilot_hist.GetXaxis().SetTitleFont(self.text_font)
        self.pilot_hist.GetYaxis().SetLabelFont(self.text_font)
        self.pilot_hist.GetXaxis().SetLabelFont(self.text_font)

        ########################################
        # Set x and y labels
        if self.draw_ratio:

          # Only need to label Y as X was labelled on ratio plot
          # According to the ROOT manual the label and title size are fractions of the pads width
          # But seems to scale with height too
          #hist.GetYaxis().SetLabelSize(self.axis_label_size )
          #hist.GetYaxis().SetTitleSize(self.text_size )
          #print "Setting ratio pad tyitle size to", self.text_size
          self.pilot_hist.GetYaxis().SetLabelSize(self.axis_label_size / (1-self.ratio_pad_height))
          self.pilot_hist.GetYaxis().SetTitleSize(self.text_size / (1-self.ratio_pad_height))
          self.pilot_hist.GetYaxis().SetTitleOffset(1.3 * (1-self.ratio_pad_height) * 0.05 / self.text_size )
          if self.xlabel:
              self.pilot_hist.GetYaxis().SetTitle(self.ylabel)

        else:

          self.pilot_hist.GetXaxis().SetLabelSize(self.axis_label_size)
          self.pilot_hist.GetXaxis().SetTitleSize(self.text_size)
          #self.pilot_hist.GetXaxis().SetTitleOffset(1.2 * 0.04 /self.text_size)
          self.pilot_hist.GetXaxis().SetTitleOffset(1.05 )
          #print 1.2 * 0.04 /self.text_size

          if self.xlabel:
              self.pilot_hist.GetXaxis().SetTitle(self.xlabel)
              self.pilot_hist.GetYaxis().SetTitle(self.ylabel)

          self.pilot_hist.GetYaxis().SetLabelSize(self.axis_label_size)
          self.pilot_hist.GetYaxis().SetTitleSize(self.text_size)
          self.pilot_hist.GetYaxis().SetTitleOffset( self.y_axis_title_offset )
          #self.pilot_hist.GetYaxis().SetTitleOffset(1.3 * 0.04 /self.text_size)
        ########################################

        #pdb.set_trace()

    def DrawElements(self, elements):

        R.TGaxis.SetMaxDigits(4)
        self.pilot_hist.Draw(elements[0].drawOpt)

        for element in elements:
            element.rootobj.Draw("same,"+element.drawOpt)

        if self.stack_err_hist:
            self.stack_err_hist.SetMarkerSize(0)
            self.stack_err_hist.SetMarkerStyle(0)
            self.stack_err_hist.SetFillStyle(3244)
            self.stack_err_hist.SetFillColor(12)
            self.stack_err_hist.SetLineWidth(1)
            self.stack_err_hist.SetLineColor(R.kBlack)
            self.stack_err_hist.Draw("same,e2")

        for element in elements:
            if not "hist" in element.drawOpt:
                element.rootobj.Draw("same,"+element.drawOpt)


        # And finally the axis again to get tick marks on top
        self.pilot_hist.Draw("axis,same")
        self.pad_histogram.Update()

    def DrawRatioPlot(self, ):

        self.pad_ratio.cd()

        # Put the stack first
        ratio_elements = [element for element in self.plot_elements if  element.type == 'stack']
        ratio_elements += [element for element in self.plot_elements if not element.type == 'stack']

        h_ratio_denom = ratio_elements[0].totalhist

        first_ratio_plot = True
        self.ratio_hists = []

        for element in ratio_elements[1:]:

            h_ratio = element.totalhist.Clone(element.totalhist.GetName()+"_RATIO")
            h_ratio.Reset()

            # Set minimum and maximum for pilot hist
            # Set Range for pilot hist
            if not self.xrangelow == None:
                h_ratio.GetXaxis().SetRangeUser(self.xrangelow, self.xrangehigh)
            ########################################

            h_ratio.Divide(element.totalhist, h_ratio_denom,1,1)
            h_ratio.SetTitle("")
            h_ratio.SetMaximum(self.ratio_yhigh-0.00001)
            h_ratio.SetMinimum(self.ratio_ylow)

            h_ratio.GetYaxis().SetTitle(self.ratio_ylabel+"  ")
            h_ratio.GetYaxis().SetTitleSize(self.text_size / self.ratio_pad_height )
            h_ratio.GetYaxis().SetLabelSize(self.axis_label_size / self.ratio_pad_height )
            h_ratio.GetYaxis().SetTitleOffset(1.3 * self.ratio_pad_height * 0.05 / self.text_size )

            # ROOT will tend to put title right up to top of pad, sometimes casuing clipping
            h_ratio.GetYaxis().SetNdivisions(7)
            h_ratio.GetYaxis().SetLabelSize(self.axis_label_size / self.ratio_pad_height)

            h_ratio.SetFillColor(0)

            h_ratio.GetXaxis().SetLabelSize( self.axis_label_size / self.ratio_pad_height )
            h_ratio.GetXaxis().SetTitleSize( self.text_size / self.ratio_pad_height )
            h_ratio.GetXaxis().SetTitleOffset(2.75 * self.ratio_pad_height* 0.05 / self.text_size  )
            # LabelOffset is ditsance between label and axis in % pad width
            h_ratio.GetXaxis().SetLabelOffset(0.005 / self.ratio_pad_height)

            if self.xlabel:
                h_ratio.GetXaxis().SetTitle(self.xlabel)

            #self.ytitle_ratio_tlatex = R.TLatex()
            #self.ytitle_ratio_tlatex.Draw(0.05,

            #pdb.set_trace()
            self.ratio_hists.append(h_ratio)

            if first_ratio_plot:
                h_ratio.Draw(element.drawOpt)
                first_ratio_plot = False
            else:
                h_ratio.Draw("same,"+element.drawOpt)

    def SortElements(self, sortByMax):

        if sortByMax:
            elements = sorted(self.plot_elements, key = lambda x: -1 * x.GetMax())
        else:
            elements = self.plot_elements

        return elements

    def MakePads(self, ):

        ########################################
        # Make pad for main histogram
        if self.draw_ratio:
            self.pad_histogram = R.TPad("pad_histogram", "pad_histogram", 0, self.ratio_pad_height, 1, 1)
            self.pad_histogram.SetBottomMargin(0.0)
        else:
            self.pad_histogram = R.TPad("pad_histogram", "pad_histogram", 0, 0, 1, 1)
            self.pad_histogram.SetBottomMargin(self.bottom_margin)

        self.pad_histogram.SetBorderMode(0)
        self.pad_histogram.SetBorderSize(0)
        self.pad_histogram.SetRightMargin(self.right_margin)
        self.pad_histogram.SetLeftMargin(self.left_margin)
        self.pad_histogram.Draw()
        ########################################

        ########################################
        # Make pad for ratio
        if self.draw_ratio:
            self.pad_ratio = R.TPad("pad_ratio", "pad_ratio", 0, 0, 1, self.ratio_pad_height)
            self.pad_ratio.SetTopMargin(0)
            self.pad_ratio.SetBottomMargin(0.3)
            self.pad_ratio.SetGrid()
            self.pad_ratio.SetBorderMode(0)
            self.pad_ratio.SetBorderSize(2)
            self.pad_ratio.SetRightMargin(self.right_margin)
            self.pad_ratio.SetLeftMargin(self.left_margin)
            self.pad_ratio.Draw()
        ########################################

        if not self.linear:
            #print "Settin gLogy"
            self.pad_histogram.SetLogy()

    def DrawLegend(self, elements):

        #pdb.set_trace()

        legend = R.TLegend(self.leg_xmin, self.leg_ymin, self.leg_xmax, self.leg_ymax)
        legend.SetFillColor(0)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(self.leg_text_size/ (1-self.ratio_pad_height))
        legend.SetTextFont(self.text_font)

        elements_reversed = list(elements)
        #elements_reversed.reverse()

        # Draw non stack stuff first
        # Then draw stack
        for element in elements_reversed:
            #if element.type == "stack":
                #continue
            for hist, label in zip(element.hists,element.legend_entries):
                if element.legOpt == "none": continue
                legend.AddEntry(hist, label, element.legOpt)

        if self.stack_err_hist and self.add_syst_leg:
            if self.stack_err_hist_has_systematic:
                legend.AddEntry(self.stack_err_hist, "Total Uncertainty", "f")
            else:
                legend.AddEntry(self.stack_err_hist, "Stat. Uncertainty", "f")

        legend.Draw()
        self.legend = legend
