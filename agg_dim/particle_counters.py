from copy import copy
import csv
import datetime as dt
import math
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.colors import LogNorm
import numpy as np
import pickle

from .ErrorHandler import *

class Pops:
    
    """full documentation see https://github.com/matrup01/data_import_modules
    
    Parameters
    ----------
    file : str
        path to pops produced .csv file.
    title : str, optional
        Given str is used as a title for quickplots. The default is "no title".
    start : str, optional
        Takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp.
    end : str, optional
        Takes a str in 'hh:mm:ss'-format and only import data acquired before that timestamp.
    bgobj : Pops, optional
        Takes another Pops object and uses its mean values as background.
    timecorr : int, optional
        Takes an int and corrects popstime by it. The default is 23.
    relobj : Pops, optional
        Takes a Pops object and displays all data as relative to the mean of it
    deviate : bool, optional
        If True, all values are expressed as relative values to the mean. The default is False
    layout : dict or str
        Makes sure, the data is read correctly from the .csv-file. Legal strings are "desktopmode", "box_pallnsdorfer" and "FlyingFlo2.0". For custom dicts see documentation. The default is "FlyingFlo2.0".
        
    Variables
    ---------
    Pops.filename : str
        Contains the file path
    Pops.relative : bool
        True if the data is expressed relatively to another obj
    Pops.deviated : bool
        True if the data is expressed relative to the mean
    Pops.d_categories : list of float
        Contains the bin borders in nanometers
    Pops.plottypes : list of lists of str
        Contains information of the different values measured by the peripheral sensors (even if they arent mounted)
    Pops.plottypes2 : list of lists of str
        Contains information of the different values measured by POPS
        """
    
    def __init__(self,file,**kwargs):
        """
        inits a Pops obj

        Parameters
        ----------
        file : str
            path to pops produced .csv file.
        title : str, optional
            Given str is used as a title for quickplots. The default is "no title".
        start : str, optional
            Takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp.
        end : str, optional
            Takes a str in 'hh:mm:ss'-format and only import data acquired before that timestamp.
        bgobj : Pops, optional
            Takes another Pops object and uses its mean values as background.
        timecorr : int, optional
            Takes an int and corrects popstime by it. The default is 23.
        relobj : Pops, optional
            Takes a Pops object and displays all data as relative to the mean of it
        deviate : bool, optional
            If True, all values are expressed as relative values to the mean. The default is False
        layout : dict or str
            Makes sure, the data is read correctly from the .csv-file. Legal strings are "desktopmode", "box_pallnsdorfer" and "FlyingFlo2.0". For custom dicts see documentation. The default is "FlyingFlo2.0".

        Returns
        -------
        None.

        """

        #init vars
        self.filename = file
        self.relative = False
        self.deviated = False
        self.d_categories = [element * 1000 for element in [0.115,0.125,0.135,0.150,0.165,0.185,0.210,0.250,0.350,0.475,0.575,0.855,1.220,1.53,1.99,2.585,3.37]]
        self.plottypes = [["temp_bm680","temperature (bm680)","°C"],["hum_bm680","rel. humidity (bm680)","%"],["temp_sen55","temperature","°C"],["hum_sen55","rel. humidity","%"],["press","ambient pressure","hPa"],["gas","Gaswiderstand",r"$\Ohm$"],["pm1","PM1.0",r"$\mu$g/$m^3$"],["pm25","PM2.5",r"$\mu$g/$m^3$"],["pm4","PM4.0",r"$\mu$g/$m^3$"],["pm10","PM10.0",r"$\mu$g/$m^3$"],["voc","VOC-Index",""],["nox",r"$NO_X$-Index",""],["co2",r"$CO_2$","ppm"],["tvoc","TVOC","ppb"]]
        self.plottypes2 = [["total","part. conc." , r"Counts/$cm^3$"],["popstemp","temperature inside POPS-box","°C"],["boardtemp","boardtemp","°C"],["overpm25","PM2.5 from POPS",r"Counts/$cm^3$"],["underpm25","particles smaller than 350 nm",r"Counts/$cm^3$"]]
        
        #kwargs
        defaults = {"title" : "no title",
                    "start" : "none",
                    "end" : "none",
                    "bgobj" : "none",
                    "timecorr" : 2,
                    "relobj" : "none",
                    "deviate" : False,
                    "wintertime" : False,
                    "layout" : "FlyingFlo2.0"}
        for key,value in zip(defaults.keys(),defaults.values()):
            self.hk_kwargs(kwargs, key, value)
        self.hk_errorhandling(kwargs, defaults.keys(), "Pops")
        
        #fix layout
        if type(self.layout) == str:
            match self.layout:
                case "desktopmode":
                    self.layout = {"bins" : [pbin for pbin in range(33,49)],
                                   "ydata" : "NULL",
                                   "ydata2" : [5,20,11],
                                   "popstime" : 1,
                                   "t" : -1,
                                   "flow" : 15}
                case "box_pallnsdorfer":
                    self.layout = {"bins" : [pbin for pbin in range(56,72)],
                                   "ydata" : [2,3,11,10,4,5,6,7,8,9,12,13,14,15],
                                   "ydata2" : [28,43,34],
                                   "popstime" : 23,
                                   "t" : 1,
                                   "flow" : 38}
                case "FlyingFlo2.0":
                    self.layout = {"bins" : [pbin for pbin in range(36,52)],
                                   "ydata" : "NULL",
                                   "ydata2" : [8,23,14],
                                   "popstime" : 3,
                                   "t" : 1,
                                   "flow" : 18}
                case _:
                    raise UnknownLayoutError(self.layout, ["desktopmode","box_pallnsdorfer","FlyingFlo2.0"], "POPS")
        
        
        #reads data from csv to list
        data = csv.reader(open(file),delimiter=",")
        data = list(data)
        newdata = []
        for dat in data:
            if dat[0][0] == "2": #only works for the next 975 years
                newdata.append(dat)
        data = newdata
        
        #deletes last row if it hasnt been written completely
        if len(data[0]) > len(data[-1]):
            data = [data[i] for i in range(len(data)-1)]
            
        #init wintertime-correction
        wt_corr = dt.timedelta(0,3600) if self.wintertime else dt.timedelta(0,7200)
        
        #extract x and y values from list
        self.popstime = [dt.datetime.strptime("00:00:00","%H:%M:%S")-dt.timedelta(0,self.timecorr)+wt_corr+dt.timedelta(0,float(data[i][self.layout["popstime"]])) for i in range(1,len(data))]
        if self.layout["t"] < 0:
            self.t = self.popstime
        else:
            self.t = [dt.datetime.strptime(data[i][self.layout["t"]],"%H:%M:%S") for i in range(1,len(data))]
        self.pops_bins_raw = [[float(data[i][j]) for i in range(1,len(data))]for j in self.layout["bins"]]
        self.pops_bins = [[self.pops_bins_raw[j][i] / float(data[i+1][self.layout["flow"]]) for i in range(len(data)-1)] for j in range(len(self.pops_bins_raw))]
        if type(self.layout["ydata"]) == str:
            self.ydata = "NULL"
        else:
            self.ydata = [[float(data[i][j]) for i in range(1,len(data))]for j in self.layout["ydata"]]
        self.ydata2 = [[float(data[i][j]) for i in range(1,len(data))] for j in self.layout["ydata2"]]
        #ydata-Syntax: [temp_bm680,rf_bm680,temp_sen55,rf_sen55,press,gas,pm1,pm25,pm4,pm10,voc,nox,co2,tvoc]
        #ydata2-Syntax: [total,popstemp,boardtemp,pops_pm25,pops_underpm25]
        self.ydata2.append([np.sum([self.pops_bins[i][j] for i in range(8,15)]) for j in range(len(self.pops_bins[0]))])
        self.ydata2.append([np.sum([self.pops_bins[i][j] for i in range(8)]) for j in range(len(self.pops_bins[0]))])
        
        #crop
        if self.start != "none":
            tcounter = -1
            for element in [data[i][self.layout["t"]] for i in range(1,len(data))]:
                tcounter += 1
                if self.start == element:
                  t_start = tcounter
            popscounter = -1
            unixstart = str(int(self.start[0:2])*3600+int(self.start[3:5])*60+int(self.start[6:8])-7200 + self.timecorr)
            for element in [data[i][self.layout["popstime"]][0:5] for i in range(1,len(data))]:
                popscounter += 1
                if unixstart == element:
                    pops_start = popscounter
        else:
            t_start = 0
            pops_start = 0
            
        if self.end != "none":
            tcounter = -1
            for element in [data[i][self.layout["t"]] for i in range(1,len(data))]:
                tcounter += 1
                if self.end == element:
                  t_end = tcounter
            popscounter = -1
            unixend = str(int(self.end[0:2])*3600+int(self.end[3:5])*60+int(self.end[6:8])-7200 + self.timecorr)
            for element in [data[i][self.layout["popstime"]][0:5] for i in range(1,len(data))]:
                popscounter += 1
                if unixend == element:
                    pops_end = popscounter
        else:
            t_end = len(data)-1
            pops_end = len(data)-1
            
        self.t = [self.t[i] for i in range(t_start,t_end)]
        self.popstime = [self.popstime[i] for i in range(pops_start,pops_end)]
        for i in range(len(self.ydata2)):
            self.ydata2[i] = [self.ydata2[i][j] for j in range(pops_start,pops_end)]
        if type(self.ydata) != str:
            for i in range(len(self.ydata)):
                self.ydata[i] = [self.ydata[i][j] for j in range(t_start,t_end)]
        for i in range(len(self.pops_bins)):
            self.pops_bins[i] = [self.pops_bins[i][j] for j in range(pops_start,pops_end)]
            
        #correctbg
        if type(self.bgobj) == Pops:
            self.importbg(self.bgobj.exportbg())
            
        #make values relative
        if type(self.relobj) == Pops:
            self.relativevals(self.relobj)
            self.relative = True
            
        #make values relative to mean
        if self.deviate:
            self.deviatefrommean()
            self.deviated = True
            
            
    def exportbg(self):
        """
        Legacy-function: using this object as background is easier, if you pass it as bgobj in the target Pops objects init
        Calculates the mean of all pops bins and returns it.

        Returns
        -------
        list in the form of: [np.array,float]
            Contains the mean of all bins in an np.array and the mean of the total partconc.

        """
        
        bins = np.array(self.pops_bins)
        bg = np.array([np.mean(element) for element in bins])
        totalbg = np.mean(np.array(self.ydata2[0]))
        return [bg,totalbg]
    
    
    def importbg(self,bg):
        """
        Legacy-function: importing a background from another pops object is easier by passing it as bgobj in the init
        Imports a background in the form its exported through Pops.exportbg()

        Parameters
        ----------
        bg : list in the form of: [np.array,float]
            Contains the mean of all bins in an np.array and the mean of the total partconc.

        Returns
        -------
        None.

        """
        
        for i in range(len(self.pops_bins)):
            self.pops_bins[i] = [self.pops_bins[i][j]-bg[0][i] for j in range(len(self.pops_bins[i]))]
        self.ydata2[0] = [self.ydata2[0][i] - bg[1] for i in range(len(self.ydata2[0]))]
        
        
    def quickplot(self,y,**kwargs):
        """
        Draws a plot y vs time

        Parameters
        ----------
        y : str
            Determines which y should be plotted.
        startcrop : int, optional
            Crops the data by startcrop seconds starting from the beginning
        endcrop : int, optional
            Crops the data by endcrop seconds starting from the end

        Returns
        -------
        None.

        """
        
        #kwargs
        defaults = {"startcrop" : 0,
                    "endcrop" : 0}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "Pops.quickplot()")
        
        #find plotdata
        plotx,ploty,label,ylabel = self.hk_findplottype(y)
        plotx = [plotx[i] for i in range(kwargs["startcrop"],len(plotx)-kwargs["endcrop"])]
        ploty = [ploty[i] for i in range(kwargs["startcrop"],len(ploty)-kwargs["endcrop"])]
            
        #draw plot
        fig,ax = plt.subplots()
        ax.plot(plotx,ploty,label=label)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel(ylabel)
        plt.title(self.title)
        plt.legend()
        plt.show()
        
        
    def plot(self,ax,y,**kwargs): #add usepopstime kwarg
        """
        Plots y over time on an existing mpl axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        y : str
            Determines which data should be plotted..
        startcrop : int, optional
            rops the data by startcrop seconds starting from the beginning.
        endcrop : int, optional
            Crops the data by endcrop seconds starting from the end.
        quakes : list of str, optional
            Takes times in the form of "HH:MM:SS" and draws vertical lines on the plot at these times. The default is []
        quakeslabel : str, optional
            If quakes != [] this label will be used for the quake-lines if the plot contains a legend. The default is "no label"
        quakecolor : str, optional
            Determines which color the quake-lines should have. The default is "tab:pink"
        color : str, optional
            Determines the color of the plot. The default is "tab:blue"
        togglexticks : bool, optional
            If True, xticks of the axis are visible. The default is True.
        printstats : bool, optional
            If True, mean, std and var are printed in the console. The default is False
        secondary : bool, optional
            If True the plot uses the y-axis on the right-hand side. Should be used if the axis is a twinx. The default is False.
        plotlabel : str, optional
            This string is used as a label for the plot, if a legend is created. The default is "no label"
        usepopstime : bool, optional
            If True, popstime is used instead of Raspi-time. Should only used if layout="box_pallnsdorfer". The default is False.

        Returns
        -------
        None.

        """
        
        #kwargs
        defaults = {"startcrop" : 0,
                    "endcrop" : 0,
                    "quakes" : [],
                    "quakeslabel" : "none",
                    "quakecolor" : "tab:pink",
                    "color" : "tab:blue",
                    "togglexticks" : True,
                    "printstats" : False,
                    "secondary" : False,
                    "plotlabel" : "none",
                    "usepopstime" : False}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "Pops.plot()")
        
        #find plotdata
        plotx,ploty,label,ylabel = self.hk_findplottype(y)
        if kwargs["usepopstime"]:
            plotx = self.popstime
        plotx = [plotx[i] for i in range(kwargs["startcrop"],len(plotx)-kwargs["endcrop"])]
        ploty = [ploty[i] for i in range(kwargs["startcrop"],len(ploty)-kwargs["endcrop"])]
        
        #change label
        if kwargs["plotlabel"] != "none":
            legendlabel = kwargs["plotlabel"]
        else: legendlabel = label
        
        #draw plot
        ax.plot(plotx,ploty,label=legendlabel,color=kwargs["color"])
        ax.set_ylabel(label + " in " + ylabel)
        ax.axes.xaxis.set_visible(kwargs["togglexticks"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        ax.tick_params(axis='y', colors=kwargs["color"])
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
        if len(kwargs["quakes"]) != 0:
            ax.vlines(x=[dt.datetime.strptime(element, "%H:%M:%S")for element in kwargs["quakes"]],ymin=min(ploty),ymax=max(ploty),color=kwargs["quakecolor"],ls="dashed",label=kwargs["quakeslabel"])
        
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        #print stats
        if kwargs["printstats"]:
            mean = np.mean(ploty)
            std = np.std(ploty,ddof=1)
            var = np.var(ploty,ddof=1)
            print(label + " (mean,std,var): " + str(mean) + ", " + str(std) + ", " + str(var))
        
    
    def quickheatmap(self):
        """
        Draws a heatmap of dndlogdp number size distribution over time

        Returns
        -------
        None.

        """
        
        #convert to heatmapdata
        heatmapdata = [[self.pops_bins[j][i] / (math.log10(self.d_categories[j+1])-math.log10(self.d_categories[j])) for i in range(len(self.pops_bins[0])-1)] for j in range(len(self.pops_bins))]
        heatmapdata = self.hk_replacezeros(heatmapdata)
        xx,yy = np.meshgrid(self.popstime,self.d_categories)
        
        #draw plot
        fig,ax = plt.subplots()
        im = ax.pcolormesh(xx,yy,heatmapdata,cmap="RdYlBu_r",norm=LogNorm())
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_yscale("log")
        ax.set_ylabel("Durchmesser in nm")
        ax.set_xlabel("CET")
        plt.colorbar(im,ax=ax,label="dN/dlog$D_p$")
        plt.show()
        
        
    def heatmap(self,ax,**kwargs):
        """
        Draws a dndlogdp heatmap over an existing mpl axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        togglexticks : bool, optional
            If True, xticks of the axis are visible. The default is True.
        orientation : str, optional
            Changes the orientation of the colorbar. The default is "horizontal".
        location : str, optional
            Changes the location of the colorbar. The default is "top".
        pad : float, optional
            Changes the padding between plot and colorbar. The default is 0.

        Returns
        -------
        None.

        """
        
        #kwargs
        defaults = {"togglexticks" : True,
                    "orientation" : "horizontal",
                    "location" : "top",
                    "togglecbar" : True,
                    "pad" : 0}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "Pops.heatmap()")
        
        #convert to heatmapdata
        heatmapdata = [[self.pops_bins[j][i] / (math.log10(self.d_categories[j+1])-math.log10(self.d_categories[j])) for i in range(len(self.pops_bins[0])-1)] for j in range(len(self.pops_bins))]
        heatmapdata = self.hk_replacezeros(heatmapdata)
        xx,yy = np.meshgrid(self.popstime,self.d_categories)
        
        mask = np.array([[xx[i][j] for j in range(len(xx[i])-1)] for i in range(len(xx)-1)])
        
        heatmapdata = np.ma.masked_array(heatmapdata,mask<min(self.popstime))
        heatmapdata = np.ma.masked_array(heatmapdata,mask>max(self.popstime))
        
        #draw plot
        im = ax.pcolormesh(xx,yy,heatmapdata,cmap="RdYlBu_r",norm=LogNorm(vmin=1,vmax=10000))
        ax.set_yscale("log")
        ax.set_ylabel("optical diameter $D_p$ in $\mu$m")
        ax.set_xlabel("CET")
        ax.set_yticks(self.d_categories,labels=[str(self.d_categories[i]/1000) if len(str(self.d_categories[i]/1000)) == 5 else str(self.d_categories[i]/1000) + "0" for i in range(len(self.d_categories))])
        ax.axes.xaxis.set_visible(kwargs["togglexticks"])
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        if kwargs["togglecbar"]:
            plt.colorbar(im,label="dN/dlog$D_p$",orientation=kwargs["orientation"],location=kwargs["location"],pad=kwargs["pad"])
            
            
    def newheatmap(self,ax,**kwargs):
        """
        Draws a dndlogdp heatmap with consistent y-increments over an existing mpl axis.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        orientation : str, optional
            Changes the orientation of the colorbar. The default is "horizontal".
        location : str, optional
            Changes the location of the colorbar. The default is "top".
        pad : float, optional
            Changes the padding between plot and colorbar. The default is 0.

        Returns
        -------
        None.

        """
        
        #kwargs
        defaults = {"orientation" : "horizontal",
                    "location" : "top",
                    "pad" : 0}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "Pops.newheatmap()")
        
        heatmapdata = [[self.pops_bins[j][i] / (math.log10(self.d_categories[j+1])-math.log10(self.d_categories[j])) for i in range(len(self.pops_bins[0])-1)] for j in range(len(self.pops_bins))]
        heatmapdata = self.hk_replacezeros(heatmapdata)
        
        xlims = [self.t[0],self.t[-1]]
        xlims = md.date2num(xlims)
        
        im = ax.imshow(heatmapdata,aspect="auto",cmap="RdYlBu_r",norm=LogNorm(vmin=1,vmax=10000),extent=[xlims[0],xlims[1],0,len(self.d_categories)-1],origin="lower",interpolation="none")
        labels = [math.sqrt(self.d_categories[i]*self.d_categories[i+1]) for i in range(len(self.d_categories)-1)]
        labels = [str(round(labels[i]/1000,2)) for i in range(len(labels))]
        ticks = list(range(len(self.d_categories)-1))
        ticks = [ticks[i]+0.5 for i in range(len(ticks))]
        ax.set_yticks(ticks,labels=labels)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        plt.colorbar(im,label="dN/dlog$D_p$ in cm${}^{-3}$",orientation=kwargs["orientation"],location=kwargs["location"],pad=kwargs["pad"])
        
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        ax.set_xlabel("CET")
        ax.set_ylabel("optical diameter $D_p$ in $\mu$m")
        
    def dndlogdp(self,ax):
        """
        Draws a dndlogdp number size distribution histogram over an existing mpl axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.

        Returns
        -------
        None.

        """
        
        #calculate needed values
        means = np.array([np.mean(self.pops_bins[i]) for i in range(len(self.pops_bins))])
        dndlogdp = [means[i]/(math.log10(self.d_categories[i+1])-math.log10(self.d_categories[i])) for i in range(len(means))]
        xvals = [self.d_categories[i] for i in range(len(means))]
        widths = [self.d_categories[i+1]-self.d_categories[i] for i in range(len(xvals))]
        
        #draw plot
        ax.bar(x=xvals,width=widths,align="edge",height=dndlogdp)
        ax.set_yscale("log")
        ax.set_ylabel("dN/dlog$D_p$")
        ax.set_xscale("log")
        ax.set_xlabel("$D_p$ in nm")
        
        
    def quickdndlogdp(self):
        """
        Draws a dndlogdp number size distribution histogram

        Returns
        -------
        None.

        """
        
        #calculate needed values
        means = np.array([np.mean(self.pops_bins[i]) for i in range(len(self.pops_bins))])
        dndlogdp = [means[i]/(math.log10(self.d_categories[i+1]-math.log10(self.d_categories[i]))) for i in range(len(means))]
        xvals = [self.d_categories[i] for i in range(len(means))]
        widths = [self.d_categories[i+1]-self.d_categories[i] for i in range(len(xvals))]
        
        print(self.title)
        print(*dndlogdp)
        
        #draw
        fig,ax = plt.subplots()
        ax.bar(x=xvals,width=widths,align="edge",height=dndlogdp)
        ax.set_yscale("log")
        ax.set_ylabel("dN/dlog$D_p$")
        ax.set_xscale("log")
        ax.set_xlabel("$D_p$ in nm")
        plt.title(self.title)
        plt.show()
        
        
    def cumulativeparticles(self):
        """
        Legacy function just use the built in variable "total" instead.

        Returns
        -------
        cparticles : float
            Sum of the means of all bins.

        """
        
        #calculate needed values
        means = np.array([np.mean(self.pops_bins[i]) for i in range(len(self.pops_bins))])
        cparticles = np.sum(means)
        print(self.title + ": " + str(cparticles) + " counts/cm3 (cumulative)")
        
        return cparticles
        
    
    def crop(self,startcrop,endcrop):
        """
        Legacy function: Use kwargs 'start' and 'end' in init instead
        Crops the data by 'startcrop' seconds on the front and 'endcrop' seconds on the end

        Parameters
        ----------
        startcrop : int
            Data will be cropped by 'startcrop' seconds beginning from the start.
        endcrop : int
            Data will be cropped by 'endcrop' seconds beginning from the end.

        Returns
        -------
        None.

        """
        length = len(self.t)
        self.t = [self.t[i] for i in range(startcrop,length-endcrop)]
        self.popstime = [self.popstime[i] for i in range(startcrop,length-endcrop)]
        for i in range(len(self.ydata)):
            self.ydata[i] = [self.ydata[i][j] for j in range(startcrop,length-endcrop)]
        for i in range(len(self.pops_bins)):
            self.pops_bins[i] = [self.pops_bins[i][j] for j in range(startcrop,length-endcrop)]
        for i in range(len(self.ydata2)):
            self.ydata2[i] = [self.ydata2[i][j] for j in range(startcrop,length-endcrop)]
        
        
        
    def stats(self,y):
        """
        Prints mean, std and var of y to the console

        Parameters
        ----------
        y : str
            Determines which data should be used.

        Returns
        -------
        None.

        """
        
        placeholder1,data,label,unit = self.hk_findplottype(y)
        mean = np.mean(data)
        std = np.std(data,ddof=1)
        var = np.var(data,ddof=1)
        print(label + " in " + unit + " (mean,std,var): " + str(mean) + ", " + str(std) + ", " + str(var))
    
        
    def returnstats(self,y):
        """
        Returns a tuple of (mean,std,var)

        Parameters
        ----------
        y : str
            Decides which data should be used.

        Returns
        -------
        mean : float
            Arithmetic mean of y.
        std : float
            Standard deviation (1 degree of freedom) of y.
        var : float
            Variance (1 degree of freedom) of y.

        """
        
        placeholder1,data,label,unit = self.hk_findplottype(y)
        mean = np.mean(data)
        std = np.std(data,ddof=1)
        var = np.var(data,ddof=1)
        
        return mean,std,var
    
    
    def append(self,obj):
        """
        Takes another Pops obj and appends its data to this one

        Parameters
        ----------
        obj : Pops
            The data of obj will be appended to self.

        Returns
        -------
        None.

        """
        
        self.popstime += obj.popstime
        self.t += obj.t
            
        if type(self.ydata) != str and type(obj.ydata) != str:
            for i in range(len(self.ydata)):
                self.ydata[i] += obj.ydata[i]
        elif type(self.ydata) == str and type(obj.ydata) != str:
            self.ydata = obj.ydata
                
        for i in range(len(self.ydata2)):
            self.ydata2 += obj.ydata2
                
        for i in range(len(self.pops_bins)):
            self.pops_bins += obj.pops_bins
                
                
    def add(self,obj):
        """
        Takes a Pops obj and returns another Pops obj which contains the data of both objs without changing them

        Parameters
        ----------
        obj : Pops
            Data of this obj will be in the returned obj together with the data of self.

        Returns
        -------
        newpops : Pops
            Pops obj that contains the data of both 'obj' and self.

        """
                    
        newpops = Pops(file=self.filename)
        newpops.t = copy(self.t) + obj.t
        newpops.popstime = copy(self.popstime) + obj.popstime
        newpops.ydata = copy(self.ydata)
        newpops.ydata2 = copy(self.ydata2)
            
        if type(newpops.ydata) != str and type(obj.ydata) != str:
            for i in range(len(newpops.ydata)):
                newpops.ydata[i] += obj.ydata[i]
        elif type(newpops.ydata) == str and type(obj.ydata) != str:
            newpops.ydata = obj.ydata
                
        for i in range(len(newpops.ydata2)):
            newpops.ydata2 += obj.ydata2
                
        for i in range(len(newpops.pops_bins)):
            newpops.pops_bins += obj.pops_bins
                
        return newpops
    
    
    def deviatefrommean(self):
        """
        Changes all data to be expressed relative to the mean

        Returns
        -------
        None.

        """
        
        for element in self.ydata:
            
            mean = np.mean(element)
            
            for i in range(len(element)):
                element[i] = ((element[i] / mean) - 1)*100
                
        for element in self.ydata2:
            
            mean = np.mean(element)
            
            for i in range(len(element)):
                element[i] = ((element[i] / mean) - 1)*100
                
        for element in self.pops_bins:
            
            mean = np.mean(element)
            
            for i in range(len(element)):
                element[i] = ((element[i] / mean) - 1)*100
                
        self.deviated = True
    
    
    def relativevals(self,bgobj):
        """
        Changes all data to be expressed relative to the mean of the bgobj

        Parameters
        ----------
        bgobj : Pops
            All data of self will be expressed relative to the data of this obj.

        Returns
        -------
        None.

        """

        bgydata = [bgobj.returnstats(bgobj.plottypes[i][0])[0] for i in range(len(bgobj.plottypes))]            
        bgydata2 = [bgobj.returnstats(bgobj.plottypes2[i][0])[0] for i in range(len(bgobj.plottypes2))]
        bgpops_bins = [bgobj.returnstats(str(i))[0] for i in range(len(bgobj.pops_bins))]
        
        for j in range(len(self.ydata)):
            newdata = []
            if bgydata[j] > 0.0:
                for i in range(len(self.ydata[j])):
                    newdata.append(((self.ydata[j][i] / bgydata[j])-1)*100)
                self.ydata[j] = copy(newdata)
            else:
                for i in range(len(self.ydata[j])):
                    newdata.append((((self.ydata[j][i]) / (bgydata[j]+1))-1)*100)
                self.ydata[j] = copy(newdata)
            
        for j in range(len(self.ydata2)):
            newdata = []
            if bgydata2[j] > 0.0:
                for i in range(len(self.ydata2[j])):
                    newdata.append(((self.ydata2[j][i] / bgydata2[j])-1)*100)
                self.ydata2[j] = copy(newdata)
            else:
                for i in range(len(self.ydata2[j])):
                    newdata.append((((self.ydata2[j][i]) / (bgydata2[j]+1))-1)*100)
                self.ydata2[j] = copy(newdata)
            
        for j in range(len(self.pops_bins)):
            newdata = []
            if bgpops_bins[j] > 0.0:
                for i in range(len(self.pops_bins[j])):
                    newdata.append(((self.pops_bins[j][i] / bgpops_bins[j])-1)*100)
                self.pops_bins[j] = copy(newdata)
            else:
                for i in range(len(self.pops_bins[j])):
                    newdata.append((((self.pops_bins[j][i]) / (bgpops_bins[j])+1)-1)*100)
                self.pops_bins[j] = copy(newdata)
            
        self.relative = True
    
    
    def average(self):
        """
        Averages all data minutewise

        Returns
        -------
        None.

        """
        
        meant,meanydata,meanpopst,meanydata2,meanpopsbins = [],[],[],[],[]
        
        if type(self.ydata) != str:
            for i in range(len(self.ydata)):
                meanydata.append([])
        for i in range(len(self.ydata2)):
            meanydata2.append([])
        for i in range(len(self.pops_bins)):
            meanpopsbins.append([])
            
        for_checker = True
            
        for i in range(len(self.t)):
            
            if for_checker:
                now = self.t[i].minute
                minute_vals = []
                
            for_checker = False
            
            minute_vals.append(i)
            
            if self.t[i].minute != now:
                
                meant.append(self.t[minute_vals[math.ceil(len(minute_vals)/2)]])
                meanpopst.append(self.popstime[minute_vals[math.ceil(len(minute_vals)/2)]])
                if type(self.ydata) != str:
                    for j in range(len(self.ydata)):
                        meanydata[j].append(np.mean([self.ydata[j][k] for k in minute_vals]))
                for j in range(len(self.ydata2)):
                    meanydata2[j].append(np.mean([self.ydata2[j][k] for k in minute_vals]))
                for j in range(len(self.pops_bins)):
                    meanpopsbins[j].append(np.mean([self.pops_bins[j][k] for k in minute_vals]))
                    
                for_checker = True
                
        self.t = meant
        self.popstime = meanpopst
        self.ydata = meanydata
        self.ydata2 = meanydata2
        self.pops_bins = meanpopsbins
        
        
    def returndata(self):
        """
        Returns a tuple containing all data in a standardized form. Important for communication with DroneWrapper objs.

        Returns
        -------
        op : dict {str : np.array}
            This dict contains all data in the form of np.arrays indexed by their name.
        op_details : dict {str : [str,str]}
            This dict contains a description and a unit for all the data saved in op.

        """
        
        y = {}
        op_details = {}
        for i in range(len(self.plottypes2)):
            y[self.plottypes2[i][0]] = self.ydata2[i]
            op_details[self.plottypes2[i][0]] = [self.plottypes2[i][1],self.plottypes2[i][2]]
        for i in range(16):
            y[f"b{i}"] = self.pops_bins[i]
            op_details[f"b{i}"] = [f"Bin {i}",r"Counts/$cm^3$"]
            
        op_t = []
        new_t = self.t[0].replace(microsecond=0)
        while new_t < self.t[-1]:
            op_t.append(new_t)
            new_t += dt.timedelta(seconds=1)
        op_t = np.array(op_t)
        
        mask = []
        compare_t = [i.replace(microsecond=0) for i in self.t]
        for i in op_t:
            if i in compare_t:
                mask.append(compare_t.index(i))
            else:
                mask.append(np.nan)
                
        op = {"t" : op_t}
        for key,val in y.items():
            y_op = np.array([val[i] if not np.isnan(i) else np.nan for i in mask])
            op[key] = y_op
            
        return op,op_details
        
        
    #housekeeping funcs    
    def hk_kwargs(self,kwargs,key,default):
        
        op = kwargs[key] if key in kwargs else default
        if type(op) == str:
            if op =="null":
                print("WARNING: Loaded file seems to have been produced either from another object than NewFData or another version of NewFData. Some functions may not be available.")
        exec(f"self.{key} = op")
        
        
    def hk_func_kwargs(self,kwargs,key,default):
        
        op = kwargs[key] if key in kwargs else default
        return op
    
    
    def hk_errorhandling(self,kwargs,legallist,funcname):
        
        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)
        
        
    def hk_findplottype(self,y):
        
        #find correct plottype
        for i in range(len(self.plottypes)):
            if self.plottypes[i][0] == y:
                if type(self.ydata) == str:
                    raise SensorNotMounted(y, "POPS")
                plotx = self.t
                ploty = self.ydata[i]
                label = self.plottypes[i][1]
                ylabel = self.plottypes[i][2] if not self.relative else "% of background"
                if self.deviated:
                    ylabel = "%  deviation from mean"
                
                return plotx,ploty,label,ylabel
            
        
        
        for i in range(len(self.plottypes2)):
            if y == self.plottypes2[i][0]:
                plotx = self.t
                ploty = self.ydata2[i]
                label = self.plottypes2[i][1]
                ylabel = self.plottypes2[i][2] if not self.relative else "% of background"
                if self.deviated:
                    ylabel = "%  deviation from mean"
            
                return plotx,ploty,label,ylabel
            
        for i in range(16):
            if "".join([char for char in y if char.isdigit()]) == str(i):
                plotx = self.t
                ploty = self.pops_bins[i]
                label = "b" + str(i)
                ylabel = r"Counts/$cm^3$" if not self.relative else "% of background"
                if self.deviated:
                    ylabel = "%  deviation from mean"
                
                return plotx,ploty,label,ylabel
            
        output = "Unknown y: y must be one of the following strings: " + "".join([self.plottypes[i][0]+", " for i in range(len(self.plottypes))])
        output += "".join([self.plottypes2[i][0]+", " for i in range(len(self.plottypes2))])
        output += "".join(["b"+str(i)+", " for i in range(15)])
        output += "b15"
        
        raise ValueError(output)
        
        
    def hk_replacezeros(self,data):
        
        smallest = 10000
        for element in data:
            for i in range(len(element)):
                if element[i] < smallest and element[i] > 0:
                    smallest = element[i]
        for element in data:
            for i in range(len(element)):
                if element[i] <= 0:
                    element[i] = np.nan
        return data
 


class OPC:
    
    """
    full docu see https://github.com/matrup01/data_import_modules
    
    Parameters
    ----------
    file : str
        takes an OPC-produced ...-C.dat file.
    mfile : str, optional
        takes an OPC-produced ...-M.dat file (if no mfile is given, the program will replace the C in the ...-C.dat file with an M and look for the filename at the same path).
    dmfile : str, optional
        takes an OPC-produced ...-dM.dat file (if no dmfile is given, the program will replace the C in the ...-C.dat file with dM and look for the filename at the same path).
    start : str, optional
        takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp.
    end : str, optional
        takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp.
    bins : list of floats, optional
        takes a list of the geometric means of the bins. The default is [0.253,0.298,0.352,0.414,0.488,0.576,0.679,0.8,0.943,1.112,1.31,1.545,1.821,2.146,2.53,2.982,3.515,4.144,4.884,5.757,6.787,8,9.43,11.12,13.1,15.45,18.21,21.46,25.3,29.82,35.15].
        
    Variables
    ---------
    OPC.data : {str : 1D numpy array}
        contains all the acquired data in the form of a dictionary
    OPC.details : {str : [str, str]}
        contains a description and the unit to each data array
        
    Additionally every kwarg is saved as an object wide variable
    
    """

    def __init__(self,file,**kwargs):
        """
        Initializes an OPC object

        Parameters
        ----------
        file : str
            takes an OPC-produced ...-C.dat file.
        mfile : str, optional
            takes an OPC-produced ...-M.dat file (if no mfile is given, the program will replace the C in the ...-C.dat file with an M and look for the filename at the same path).
        dmfile : str, optional
            takes an OPC-produced ...-dM.dat file (if no dmfile is given, the program will replace the C in the ...-C.dat file with dM and look for the filename at the same path).
        start : str, optional
            takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp.
        end : str, optional
            takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp.
        bins : list of floats, optional
            takes a list of the geometric means of the bins. The default is [0.253,0.298,0.352,0.414,0.488,0.576,0.679,0.8,0.943,1.112,1.31,1.545,1.821,2.146,2.53,2.982,3.515,4.144,4.884,5.757,6.787,8,9.43,11.12,13.1,15.45,18.21,21.46,25.3,29.82,35.15].
            
        Returns
        -------
        None.

        """
        
        #kwargs
        defaults = {"mfile" : file.replace("C.","M."),
                    "dmfile" : file.replace("C.","dM."),
                    "start" : None,
                    "end" : None,
                    "bins" : [0.253,0.298,0.352,0.414,0.488,0.576,0.679,0.8,0.943,1.112,1.31,1.545,1.821,2.146,2.53,2.982,3.515,4.144,4.884,5.757,6.787,8,9.43,11.12,13.1,15.45,18.21,21.46,25.3,29.82,35.15]}
        for key,value in zip(defaults.keys(),defaults.values()):
            self.hk_kwargs(kwargs, key, value)
        self.hk_errorhandling(kwargs, defaults.keys(), "OPC")
        
        if file[-4:] == ".dat":
            cfile = file
            
            self.data = {}
            self.details = {}
            
            #import cfile
            with open(cfile) as f:
                cdata = list(f)[14:]
                chelper = cdata[0].replace(",",".").split("\t")
                cdata = cdata[1:]
            for i,row in enumerate(cdata):
                cdata[i] = row.replace(",",".").split("\t")
                cdata[i][0] = dt.datetime.strptime(cdata[i][0],"%d.%m.%Y %H:%M:%S")
            cdata = np.array(cdata).transpose()
            self.data["t"] = cdata[0]
            self.details["t"] = ["time","CET"]
            self.data["t_noday"] = np.array([cdata[0][i].time() for i in range(len(cdata[0]))])
            self.details["t_noday"] = ["time","CET"]
            cdata = cdata[1:].astype(float) / 1000 #convert from #/l to #/ccm
            self.data["totalpartconc"] = np.sum(cdata,axis=0)
            self.details["totalpartconc"] = ["Part.Conc. over all channels","counts/cm${}^3$"]
            for i,d in enumerate(cdata):
                self.data[f"b{i}partconc"] = d
                self.details[f"b{i}partconc"] = [f"Bin{i} ({chelper[i+1]})","counts/cm${}^3$"]
                
            #import mfile
            try:
                with open(self.mfile) as f:
                    mdata = list(f)[14:]
                    mhelper = mdata[0].replace(",",".").split("\t")[1:]
                    mdata = mdata[1:]
            except FileNotFoundError:
                raise FileNotFoundError(f"File {self.mfile} not found. If it has been renamed or moved, pass the new name/path as 'mfile' to OPC.__init__()")
            for i,row in enumerate(mdata):
                mdata[i] = row.replace(",",".").split("\t")[1:]
            mdata = np.array(mdata).transpose().astype(float)
            for key,val in zip(mhelper,mdata):
                key = key[:-8]
                self.data[key.lower()] = val
                self.details[key.lower()] = [key,"$\mu$g/m${}^3$"]
                
            #import dmfile
            try:
                with open(self.dmfile) as f:
                    dmdata = list(f)[14:]
                    dmhelper = dmdata[0].replace(",",".").split("\t")[1:]
                    dmdata = dmdata[1:]
            except FileNotFoundError:
                raise FileNotFoundError(f"File {self.dmfile} not found. If it has been renamed or moved, pass the new name/path as 'dmfile' to OPC.__init__()")
            for i,row in enumerate(dmdata):
                dmdata[i] = row.replace(",",".").split("\t")[1:]
            dmdata = np.array(dmdata).transpose().astype(float)
            self.data["totalmassconc"] = np.sum(cdata,axis=0)
            self.details["totalmassconc"] = ["Mass Conc. over all channels","$\mu$g/m${}^3$"]
            for i,d in enumerate(cdata):
                self.data[f"b{i}massconc"] = d
                self.details[f"b{i}massconc"] = [f"Bin{i} ({chelper[i+1]})","$\mu$g/m${}^3$"]
                
            #crop
            m = np.full(len(self.data["t_noday"]),True)
            if self.start != None:
                tstart = dt.datetime.strptime(self.start,"%H:%M:%S").time()
                m = np.where(tstart < self.data["t_noday"],m,False)
            if self.end != None:
                tend = dt.datetime.strptime(self.end,"%H:%M:%S").time()
                m = np.where(tend > self.data["t_noday"],m,False)
            for key in self.data:
                self.data[key] = self.data[key][m]
                
        elif file[-4:] == ".opc":
            self.data,self.details = pickle.load(open(file,"rb"))
            
            #crop
            m = np.full(len(self.data["t_noday"]),True)
            if self.start != None:
                tstart = dt.datetime.strptime(self.start,"%H:%M:%S")
                m = np.where(tstart < self.data["t_noday"],m,False)
            if self.end != None:
                tend = dt.datetime.strptime(self.end,"%H:%M:%S")
                m = np.where(tend > self.data["t_noday"],m,False)
            for key in self.data:
                self.data[key] = self.data[key][m]
                
        else:
            raise IllegalFileFormat(file.split(".")[1], "dat or .opc", "'file' argument in OPC.__init__()")
                
                
                
    def save(self,name):
        """
        Saves the OPC object to an .opc file

        Parameters
        ----------
        name : str
            This variable will be used as name and path where the .opc file is saved.

        Returns
        -------
        None.

        """
        
        if name[-4:] != ".opc":
            name += ".opc"
        op = [self.data,self.details]
        
        pickle.dump(op,open(name,"wb"),4)
        
        
    def plot(self,ax,y,**kwargs):
        """
        Draws an y vs time plot over an existing mpl axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        y : str
            This string is given to the OPC.data dict as a key, to determine which data should be plotted.
        quakes : list of str, optional
            Takes times in the form of "HH:MM:SS" and draws vertical lines on the plot at these times. The default is []
        quakeslabel : str, optional
            If quakes != [] this label will be used for the quake-lines if the plot contains a legend. The default is "no label"
        quakecolor : str, optional
            Determines which color the quake-lines should have. The default is "tab:purple"
        color : str, optional
            Determines the color of the plot. The default is "tab:orange"
        plotlabel : str, optional
            This string is used as a label for the plot, if a legend is created. The default is "no label"
        ylabel : str, optional
            This string is used as a label for the y axis. If no ylabel is given it will be created like this: f"OPC.details[y][0] in OPC.details[y][1]"
        secondary : bool, optional
            If True, the plot will draw the axis on the right-hand side. Should be used if the given ax is a twinx(). The default is False.
        setday : Takes a date in the format "DDMMYYYY" and moves the data to this day. Should be used if the data is plotted against data from another instrument that doesnt save a date. The default is None.


        Returns
        -------
        None.

        """
        
        #import kwargs   
        defaults = {"quakes" : [],
                    "quakeslabel" : "no label",
                    "quakecolor" : "tab:purple",
                    "color" : "tab:orange",
                    "plotlabel" : "no label",
                    "ylabel" : "*",
                    "secondary" : False,
                    "setday" : None}
        
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "OPC.plot()")
        
        if kwargs["ylabel"] == "*":
            kwargs["ylabel"] = f"{self.details[y][0]} in {self.details[y][1]}"
        
        #draw plot
        x = self.data["t"]
        if type(kwargs["setday"]) == str:
            date = [int(kwargs["setday"][:2]),int(kwargs["setday"][2:4]),int(kwargs["setday"][4:])]
            for i in range(len(x)):
                x[i] = x[i].replace(day=date[0],month=date[1],year=date[2])
        try:
            y = self.data[y]
        except KeyError:
            raise IllegalValue(y, "OPC.plot()", [key for key in self.data])
        ax.plot(x,y,label=kwargs["plotlabel"],color=kwargs["color"])
        ax.set_ylabel(kwargs["ylabel"])
        ax.set_xlabel("CET")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        if len(kwargs["quakes"]) != 0:
            ax.vlines(x=[dt.datetime.strptime(element, "%H:%M:%S")for element in kwargs["quakes"]],ymin=min(y),ymax=max(y),color=kwargs["quakecolor"],ls="dashed",label=kwargs["quakeslabel"])
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
            
            
    def heatmap(self,ax,**kwargs):
        """
        Draws a dndlogdp-heatmap over an existing mpl-axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        ylabel : str, optional
            Changes the label of the y-axis, if no ylabel is give it will say "dN/dlogDp in ccm^-3".
        orientation : str, optional
            Changes the orientation of the colorbar. The default is "horizontal".
        location : str, optional
            Changes the location of the colorbar. The default is "top"
        pad : float, optional
            Changes the padding between plot and colorbar. The default is 0.
        cmap : str, optional
            Changes the colormap used for the heatmap. The default is "RdYlBu_r".

        Returns
        -------
        None.

        """
        
        #import kwargs   
        defaults = {"ylabel" : None,
                    "orientation" : "horizontal",
                    "location" : "top",
                    "pad" : 0,
                    "cmap" : "RdYlBu_r"}
        
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "OPC.heatmap()")
                
        #draw heatmap
        logdp = np.log10(self.bins)
        dlogdp = np.array([(logdp[i+1]-logdp[i]) if i == 0 else logdp[i]-logdp[i-1] if i == len(logdp)-1 else (logdp[i+1]-logdp[i-1])/2 for i in range(len(logdp))])
        
        y = np.array([self.data[f"b{size_bin}partconc"]/val for size_bin,val in zip(range(31),dlogdp)])
        
        xlims = [self.data["t"][0],self.data["t"][-1]]
        xlims = md.date2num(xlims)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        ax.set_yticks([i+0.5 for i in range(len(self.bins))],[f"{i:.2f}" for i in self.bins])
        
        im = ax.imshow(y,aspect="auto",norm="log",extent=[xlims[0],xlims[1],0,len(dlogdp)],cmap=kwargs["cmap"],interpolation="none",origin="lower")
        plt.colorbar(im,label="dN/dlog$D_p$ in cm${}^{-3}$",orientation=kwargs["orientation"],location=kwargs["location"],pad=kwargs["pad"])
        
        if kwargs["ylabel"] != None:
            ax.set_ylabel(kwargs["ylabel"])
        else:
            ax.set_ylabel("$D_P$ in $\mu$m")
            
            
    def dndlogdp(self,ax,**kwargs):
        """
        Draws a bar-plot of the average dndlogdp number size distribution on an existing mpl-axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        start : str, optional
            Takes a str of the form "HH:MM:SS" and only uses data acquired after this time for the average distribution. The default is None.
        end : str, optional
            Takes a str of the form "HH:MM:SS" and only uses data acquired before this time for the average distribution. The default is None.
        logy : bool, optional
            If True, the y axis will be logarithmic. The default is False.
        ylabel : str, optional
            Changes the label of the y-axis, if no ylabel is give it will say "dN/dlogDp in ccm^-3".
        scatter : bool, optional
            If True, a scatterplot will be drawn instead of a bar plot.

        Returns
        -------
        None.

        """
        
        #import kwargs   
        defaults = {"start": None,
                    "end" : None,
                    "logy" : False,
                    "ylabel" : None,
                    "scatter" : False}
        
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "OPC.dndlogdp()")
        
        #draw plot
        m = np.full(len(self.data["t"]),True)
        if type(kwargs["start"]) == str:
            kwargs["start"] = dt.datetime.strptime(kwargs["start"], "%H:%M:%S").time()
            m = np.where(self.data["t_noday"] > kwargs["start"],m,False)
        if type(kwargs["end"]) == str:
            kwargs["end"] = dt.datetime.strptime(kwargs["end"], "%H:%M:%S").time()
            m = np.where(self.data["t_noday"] < kwargs["end"],m,False)
        
        
        logdp = np.log10(self.bins)
        dlogdp = np.array([(logdp[i+1]-logdp[i]) if i == 0 else logdp[i]-logdp[i-1] if i == len(logdp)-1 else (logdp[i+1]-logdp[i-1])/2 for i in range(len(logdp))])
        ddp = np.array([(self.bins[i+1]-self.bins[i]) if i == 0 else self.bins[i]-self.bins[i-1] if i == len(self.bins)-1 else (self.bins[i+1]-self.bins[i-1])/2 for i in range(len(self.bins))])
        
        y = np.array([np.mean(self.data[f"b{size_bin}partconc"][m]/val) for size_bin,val in zip(range(31),dlogdp)])
        
        if kwargs["scatter"]:
            ax.scatter(self.bins,y)
        else:
            ax.bar(self.bins,y,width=ddp)
        ax.set_xscale("log")
        if kwargs["logy"]:
            ax.set_yscale("log")
            
        ax.set_xlabel("$D_P$ in $\mu$m")
        if type(kwargs["ylabel"]) == str:
            ax.set_ylabel(kwargs["ylabel"])
        else:
            ax.set_ylabel("dN/dlog$D_P$ in cm${}^{-3}$")
        
        
    #housekeeping funcs    
    def hk_kwargs(self,kwargs,key,default):
        
        op = kwargs[key] if key in kwargs else default
        exec(f"self.{key} = op")
        
        
    def hk_func_kwargs(self,kwargs,key,default):
        
        op = kwargs[key] if key in kwargs else default
        return op
    
    
    def hk_errorhandling(self,kwargs,legallist,funcname):
        
        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)
                
                
