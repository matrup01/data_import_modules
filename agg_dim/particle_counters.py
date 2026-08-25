"""
This Submodule provides the `Pops` and the `OPC` obj, which can be used to 
read in pops and opc data
"""

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.colors import LogNorm
import numpy as np
import pickle

from .ErrorHandler import IllegalArgument,IllegalFileFormat,IllegalValue,UnknownLayoutError

class Pops:    
    
    def __init__(self,file,**kwargs):
        """
        Obj to read in data produced by Pops

        Parameters
        ----------
        file : str
            path to pops produced .csv file.
        start : str, optional
            Takes a str in 'hh:mm:ss'-format and only imports data acquired 
            after that timestamp.
        end : str, optional
            Takes a str in 'hh:mm:ss'-format and only import data acquired 
            before that timestamp.
        bgobj : Pops, optional
            Takes another Pops object and uses its mean values as background.
        timecorr : int, optional
            Takes an int and corrects popstime by it. The default is 23.
        relobj : Pops, optional
            Takes a Pops object and displays all data as relative to the 
            mean of it
        deviate : bool, optional
            If True, all values are expressed as relative values to the mean. 
            The default is False
        layout : dict or str
            Makes sure, the data is read correctly from the .csv-file. Legal 
            strings are "desktopmode", "box_pallnsdorfer" and "FlyingFlo2.0". 
            For custom dicts see documentation. The default is "FlyingFlo2.0".
        t_no_beaglebone : bool, optional
            If True, only the time column written by the raspy will be used 
            instead of the time column written by beaglebone. The default is
            True.

        Attributes
        ----------
        filename : str
            Contains the file path
        relative : bool
            True if the data is expressed relatively to another obj
        deviated : bool
            True if the data is expressed relative to the mean
        d_categories : list of float
            Contains the bin borders in nanometers
        data : dict of np.arrays
            contains all the data arrays
        details : dict of list of strs
            contains lists with `len=2` which contain information what data is 
            stored in `self.data`

        """

        #init vars
        self.filename = file
        self.data = {}
        self.details = {}
        self.relative = False
        self.deviated = False
        self.d_categories = np.array(
            [element * 1000 for element in [0.115,
                                            0.125,
                                            0.135,
                                            0.150,
                                            0.165,
                                            0.185,
                                            0.210,
                                            0.250,
                                            0.350,
                                            0.475,
                                            0.575,
                                            0.855,
                                            1.220,
                                            1.53,
                                            1.99,
                                            2.585,
                                            3.37]
             ]
            )
        self.plottypes = [
            ["temp_bm680","temperature (bm680)","°C"],
            ["hum_bm680","rel. humidity (bm680)","%"],
            ["temp_sen55","temperature","°C"],
            ["hum_sen55","rel. humidity","%"],
            ["press","ambient pressure","hPa"],
            ["gas","Gaswiderstand",r"$\Ohm$"],
            ["pm1","PM1.0",r"$\mu$g/$m^3$"],
            ["pm25","PM2.5",r"$\mu$g/$m^3$"],
            ["pm4","PM4.0",r"$\mu$g/$m^3$"],
            ["pm10","PM10.0",r"$\mu$g/$m^3$"],
            ["voc","VOC-Index",""],
            ["nox",r"$NO_X$-Index",""],
            ["co2",r"$CO_2$","ppm"],
            ["tvoc","TVOC","ppb"]
            ]
        self.plottypes2 = [
            ["total","part. conc." , r"Counts/$cm^3$"],
            ["popstemp","temperature inside POPS-box","°C"],
            ["boardtemp","boardtemp","°C"],
            ["overpm25","PM2.5 from POPS",r"Counts/$cm^3$"],
            ["underpm25","particles smaller than 350 nm",r"Counts/$cm^3$"]
            ]
        
        #kwargs
        defaults = {"start" : "00:00:00",
                    "end" : "23:59:59",
                    "bgobj" : "none",
                    "timecorr" : 2,
                    "relobj" : "none",
                    "deviate" : False,
                    "wintertime" : False,
                    "layout" : "FlyingFlo2.0",
                    "t_no_beaglebone" : True}
        for key,value in zip(defaults.keys(),defaults.values()):
            self._hk_kwargs(kwargs, key, value)
        self._hk_errorhandling(kwargs, defaults.keys(), "Pops")
        
        #fix layout
        if isinstance(self.layout,str):
            match self.layout:
                case "desktopmode":
                    self.layout = {"bins" : list(range(33,49)),
                                   "ydata" : "NULL",
                                   "ydata2" : [5,20,11],
                                   "popstime" : 1,
                                   "t" : -1,
                                   "flow" : 15}
                case "box_pallnsdorfer":
                    self.layout = {"bins" : list(range(56,72)),
                                   "ydata" : [2,3,11,10,4,5,6,7,8,9,12,13,14,15],
                                   "ydata2" : [28,43,34],
                                   "popstime" : 23,
                                   "t" : 1,
                                   "flow" : 38}
                case "FlyingFlo2.0":
                    self.layout = {"bins" : list(range(36,52)),
                                   "ydata" : "NULL",
                                   "ydata2" : [8,23,14],
                                   "popstime" : 3,
                                   "t" : 1,
                                   "flow" : 18}
                case _:
                    raise UnknownLayoutError(self.layout, 
                                             ["desktopmode",
                                              "box_pallnsdorfer",
                                              "FlyingFlo2.0"], 
                                             "POPS")
        self.ydata = np.array(
            [det[0] for det in self.plottypes])
        
        if self.filename.endswith(".csv"):
            with open(self.filename,"r") as f:
                data = list(f)[1:]
            for i in range(len(data)):
                data[i] = data[i].split(",")
            newdata = []
            for dat in data:
                if dat[0][0] == "2": #only works for the next 974 years
                    newdata.append(dat)
            data = newdata
            del newdata
            
            #deletes last row if it hasnt been written completely
            if len(data[0]) > len(data[-1]):
                data.pop(-1)
                
            wt_corr = dt.timedelta(0,3600) if self.wintertime else dt.timedelta(0,7200)
            
            self.data["popstime"] = [dt.datetime.strptime(
                "00:00:00",
                "%H:%M:%S"
                )-dt.timedelta(
                    0,
                    self.timecorr
                    )+wt_corr+dt.timedelta(
                        0,
                        float(data[i][self.layout["popstime"]])
                        ) for i in range(1,len(data))]
            self.data["popstime"] = np.array(self.data["popstime"])
            if self.layout["t"] < 0:
                self.data["t"] = self.data["popstime"]
            else:
                self.data["t"] = [dt.datetime.strptime(
                    data[i][self.layout["t"]],
                    "%H:%M:%S") for i in range(1,len(data))]
            self.data["t"] = np.array(self.data["t"])
            if self.t_no_beaglebone:
                self.data["popstime"] = self.data["t"]
            
            flow = np.array(
                [data[i][self.layout["flow"]] for i in range(1,len(data))]
                ).astype(float)
            print(flow)
            
            for i,b in enumerate(self.layout["bins"]):
                self.data[f"b{i}cps"] = np.array(
                    [data[row][b] for row in range(1,len(data))]
                    ).astype(float)
                self.details[f"b{i}cps"] = [
                    f"Particle Counts of Bin {i}",
                    "#/s"
                    ]
                self.data[f"b{i}partconc"] = self.data[f"b{i}cps"] / flow
                self.details[f"b{i}partconc"] = [
                    f"Particle Concentration of Bin {i}",
                    "#/s"
                    ]
            
            if self.layout["ydata"] != "NULL":
                for loc,dat in zip(self.layout["ydata"],self.plottypes):
                    self.data[dat[0]] = np.array(
                        [data[i][loc] for i in range(1,len(data))]
                        ).astype(float)
                    self.details = [dat[1],dat[2]]
            for loc,dat in zip(self.layout["ydata2"],self.plottypes2):
                self.data[dat[0]] = np.array(
                    [data[i][loc] for i in range(1,len(data))]
                    ).astype(float)
                self.details[dat[0]] = [dat[1],dat[2]]
                
        #crop
        m1 = self._hk_returncropmask(self.data["t"], self.start, self.end)
        m2 = self._hk_returncropmask(self.data["popstime"], self.start,self.end)
        for key in self.data:
            if key in self.ydata or key=="t":
                self.data[key] = self.data[key][m1]
            else:
                self.data[key] = self.data[key][m2]
            
        #correctbg
        if isinstance(self.bgobj,Pops):
            self.importbg(self.bgobj.exportbg())
            
            for key in self.data:
                try:
                    self.data[key] = self.data[key]-np.nanmean(self.bgobj[key])
                except:
                    msg = f"WARNING: {key} could not be bg-corrected, because"
                    msg += f"it does not exist in {self.bgobj}"
                    print(msg)
            
        #make values relative
        if isinstance(self.relobj,Pops):
            self.relativevals(self.relobj)
            self.relative = True
            
        #make values relative to mean
        if self.deviate:
            self.deviatefrommean()
            self.deviated = True
        
        
    def quickplot(self,y):
        """
        Draws a plot y vs time

        Parameters
        ----------
        y : str
            Determines which y should be plotted.

        Returns
        -------
        None.

        """
        
        xx = self.data["t"] if y in self.ydata else self.data["popstime"]
        yy = self.data[y]  
        label = f"{self.details[y][0]} in {self.details[y][1]}"
            
        #draw plot
        _,ax = plt.subplots()
        ax.plot(xx,yy,label=self.details[y][0])
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel(label)
        ax.legend()
        plt.show()
        
        
    def plot(self,ax,y,**kwargs):
        """
        Plots y over time on an existing mpl axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        y : str
            Determines which data should be plotted.
        start : str, optional
            When 'start' is given in the format "HH:MM:SS", only data acquired
            after this timestamp will be plotted.
        end : str, optional
            When 'end' is given in the format "HH:MM:SS", only data acquired
            before this timestamp will be plotted.
        quakes : list of str, optional
            Takes times in the form of "HH:MM:SS" and draws vertical lines on 
            the plot at these times. The default is []
        quakeslabel : str, optional
            If quakes != [] this label will be used for the quake-lines if the 
            plot contains a legend. The default is "no label"
        quakecolor : str, optional
            Determines which color the quake-lines should have. The default 
            is "tab:pink"
        color : str, optional
            Determines the color of the plot. The default is "tab:blue"
        togglexticks : bool, optional
            If True, xticks of the axis are visible. The default is True.
        printstats : bool, optional
            If True, mean, std and var are printed in the console. 
            The default is False
        secondary : bool, optional
            If True the plot uses the y-axis on the right-hand side. Should be 
            used if the axis is a twinx. The default is False.
        plotlabel : str, optional
            This string is used as a label for the plot, if a legend is 
            created. The default is "no label"
        usepopstime : bool, optional
            If True, popstime is used instead of Raspi-time. Should only used 
            if layout="box_pallnsdorfer". The default is False.

        Returns
        -------
        None.

        """
        
        #kwargs
        defaults = {"start" : "none",
                    "end" : "none",
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
            kwargs[key] = self._hk_func_kwargs(kwargs,key,default)
        self._hk_errorhandling(kwargs, defaults.keys(), "Pops.plot()")
        
        try:
            self.data[y]
        except ValueError:
            legals = ",".join(self.data.keys())
            msg = f"{y} is no legal 'y' for Pops.plot(). Consider one of the "
            msg += "following: "
            raise ValueError(msg+legals)
        
        if y in self.ydata and not kwargs["usepopstime"]:
            m = self._hk_returncropmask(self.data["t"], 
                                       kwargs["start"], 
                                       kwargs["end"])
            xx = self.data["t"][m]
        else:
            m = self._hk_returncropmask(self.data["popstime"], 
                                       kwargs["start"], 
                                       kwargs["end"])
            xx = self.data["popstime"][m]
        yy = self.data[y][m]
        
        #change label
        if kwargs["plotlabel"] != "none":
            legendlabel = kwargs["plotlabel"]
        else: 
            legendlabel = self.details[y][0]
        
        #draw plot
        ax.plot(xx,yy,label=legendlabel,color=kwargs["color"])
        ax.set_ylabel(f"{self.details[y][0]} in {self.details[y][1]}")
        ax.axes.xaxis.set_visible(kwargs["togglexticks"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        ax.tick_params(axis='y', colors=kwargs["color"])
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
        if len(kwargs["quakes"]) != 0:
            ax.vlines(
                x=[dt.datetime.strptime(element, "%H:%M:%S")
                   for element in kwargs["quakes"]],
                ymin=min(yy),
                ymax=max(xx),
                color=kwargs["quakecolor"],
                ls="dashed",
                label=kwargs["quakeslabel"])
        
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        #print stats
        if kwargs["printstats"]:
            mean = np.mean(yy)
            std = np.std(yy,ddof=1)
            var = np.var(yy,ddof=1)
            print(f"{legendlabel}:\n\tmean: {mean}\n\tstd:  {std}\n\tvar:  {var}")
        
    
    def quickheatmap(self):
        """
        Draws a heatmap of dndlogdp number size distribution over time

        Returns
        -------
        None.

        """
        
        #convert to heatmapdata
        
        dlog = np.log10(self.d_categories)
        dndlogdp = np.array(
            [self.data[f"b{i}partconc"]/(dlog[i+1]-dlog[i])
             for i in range(len(dlog)-1)]
            )[:,:-1]
        zeros = np.where(dndlogdp==0)
        dndlogdp[zeros] = np.nan
        xx,yy = np.meshgrid(self.data["popstime"],self.d_categories)
        
        #draw plot
        _,ax = plt.subplots()
        im = ax.pcolormesh(xx,yy,dndlogdp,cmap="RdYlBu_r",norm=LogNorm())
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_yscale("log")
        ax.set_ylabel("Durchmesser in nm")
        ax.set_xlabel("CET")
        plt.colorbar(im,ax=ax,label="dN/dlog$D_p$")
        plt.show()
        
        
    def heatmap(self,ax,**kwargs):
        """
        Draws a dndlogdp heatmap over an existing mpl axis
        
        .. deprecated:: 0.2.5
            This method was last updated in agg_dim 0.2.5 and might be removed
            soon since it was succeeded by Pops.newheatmap.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        start : str, optional
            When 'start' is given in the format "HH:MM:SS", only data acquired
            after this timestamp will be plotted.
        end : str, optional
            When 'end' is given in the format "HH:MM:SS", only data acquired
            before this timestamp will be plotted.
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
        msg = "WARNING: Pops.heatmap() is deprecated and might be removed soon"
        msg += ". Check out the docu and consider using Pops.newheatmap() "
        msg += "instead."
        print(msg)
        
        #kwargs
        defaults = {"start" : "none",
                    "end" : "none",
                    "togglexticks" : True,
                    "orientation" : "horizontal",
                    "location" : "top",
                    "togglecbar" : True,
                    "pad" : 0}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self._hk_func_kwargs(kwargs,key,default)
        self._hk_errorhandling(kwargs, defaults.keys(), "Pops.heatmap()")
        
        dlog = np.log10(self.d_categories)
        m = self._hk_returncropmask(self.data["popstime"],
                                   kwargs["start"],
                                   kwargs["end"])
        dndlogdp = np.array(
            [self.data[f"b{i}partconc"][m]/(dlog[i+1]-dlog[i])
             for i in range(len(dlog)-1)]
            )
        dndlogdp = np.where(dndlogdp==0,np.nan,dndlogdp)[:,:-1]
        
        xx,yy = np.meshgrid(self.data["popstime"][m],self.d_categories)
        
        #draw plot
        im = ax.pcolormesh(xx,
                           yy,
                           dndlogdp,
                           cmap="RdYlBu_r",
                           norm=LogNorm(vmin=1,vmax=10000))
        ax.set_yscale("log")
        ax.set_ylabel("optical diameter $D_p$ in $\mu$m")
        ax.set_xlabel("CET")
        yticks = [str(i/1000) for i in self.d_categories]
        for i,yt in enumerate(yticks):
            if len(yt) != 5:
                yticks[i] += "0"
        ax.set_yticks(self.d_categories,labels=yticks)
        ax.axes.xaxis.set_visible(kwargs["togglexticks"])
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        if kwargs["togglecbar"]:
            plt.colorbar(im,
                         label="dN/dlog$D_p$",
                         orientation=kwargs["orientation"],
                         location=kwargs["location"],
                         pad=kwargs["pad"])
            
            
    def newheatmap(self,ax,**kwargs):
        """
        Draws a dndlogdp heatmap with consistent y-increments over an existing mpl axis.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        start : str, optional
            When 'start' is given in the format "HH:MM:SS", only data acquired
            after this timestamp will be plotted.
        end : str, optional
            When 'end' is given in the format "HH:MM:SS", only data acquired
            before this timestamp will be plotted.
        orientation : str, optional
            Changes the orientation of the colorbar. The default is "horizontal".
        location : str, optional
            Changes the location of the colorbar. The default is "top".
        pad : float, optional
            Changes the padding between plot and colorbar. The default is 0.
        cmap : str, optional
            Decides which colormap should be used. The default is "RdYlBu_r".

        Returns
        -------
        None.

        """
        
        #kwargs
        defaults = {"orientation" : "horizontal",
                    "location" : "top",
                    "pad" : 0,
                    "start" : "none",
                    "end" : "none",
                    "cmap" : "RdYlBu_r"}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self._hk_func_kwargs(kwargs,key,default)
        self._hk_errorhandling(kwargs, defaults.keys(), "Pops.heatmap()")
        
        dlog = np.log10(self.d_categories)
        m = self._hk_returncropmask(self.data["popstime"],
                                   kwargs["start"],
                                   kwargs["end"])
        dndlogdp = np.array(
            [self.data[f"b{i}partconc"][m]/(dlog[i+1]-dlog[i])
             for i in range(len(dlog)-1)]
            )
        zeros = np.where(dndlogdp==0)
        dndlogdp[zeros] = np.nan

        
        xlims = [self.data["popstime"][0],self.data["popstime"][-1]]
        xlims = md.date2num(xlims)
        
        im = ax.imshow(dndlogdp,
                       aspect="auto",
                       cmap=kwargs["cmap"],
                       norm=LogNorm(vmin=1,vmax=10000),
                       extent=[xlims[0],xlims[1],0,len(self.d_categories)-1],
                       origin="lower",
                       interpolation="none")
        labels = [np.sqrt(self.d_categories[i]*self.d_categories[i+1]) 
                  for i in range(len(self.d_categories)-1)]
        labels = [str(round(labels[i]/1000,2)) for i in range(len(labels))]
        ticks = list(range(len(self.d_categories)-1))
        ticks = [ticks[i]+0.5 for i in range(len(ticks))]
        ax.set_yticks(ticks,labels=labels)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        plt.colorbar(im,
                     label="dN/dlog$D_p$ in cm${}^{-3}$",
                     orientation=kwargs["orientation"],
                     location=kwargs["location"],
                     pad=kwargs["pad"])
        
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        ax.set_xlabel("CET")
        ax.set_ylabel("optical diameter $D_p$ in $\mu$m")
        
    def dndlogdp(self,ax,**kwargs):
        """
        Draws a dndlogdp number size distribution histogram over an existing mpl axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        start : str, optional
            When 'start' is given in the format "HH:MM:SS", only data acquired
            after this timestamp will be plotted.
        end : str, optional
            When 'end' is given in the format "HH:MM:SS", only data acquired
            before this timestamp will be plotted.
        scatter : bool, optional
            If True, a scatterplot will be drawn instead of a bar plot. 
            The default is False.
        color : str, optional
            Changes the color of the bar/points. The default is 'tab:blue'.
        label : str, optional
            Changes the plot label, which is used in a legend. The default is
            'no label'.

        Returns
        -------
        None.

        """
        
        #kwargs
        defaults = {"start" : "none",
                    "end" : "none",
                    "scatter" : False,
                    "color" : "tab:blue",
                    "label" : "no label"}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self._hk_func_kwargs(kwargs,key,default)
        self._hk_errorhandling(kwargs, defaults.keys(), "Pops.dndlogdp()")
        
        #calculate needed values       
        dlog = np.log10(self.d_categories)
        m = self._hk_returncropmask(self.data["popstime"],
                                   kwargs["start"],
                                   kwargs["end"])
        dndlogdp = np.array(
            [self.data[f"b{i}partconc"][m]/(dlog[i+1]-dlog[i])
             for i in range(len(dlog)-1)]
            )
        dndlogdp = np.mean(dndlogdp,axis=1)
        xvals = self.d_categories[:-1]
        widths = self.d_categories[1:] - self.d_categories[:-1]
        
        #draw plot
        if kwargs["scatter"]:
            ax.scatter(xvals,
                       dndlogdp,
                       color=kwargs["color"],
                       label=kwargs["label"])
        else:
            ax.bar(x=xvals,
                   width=widths,
                   align="edge",
                   height=dndlogdp,
                   color=kwargs["color"],
                   label=kwargs["label"])
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
        dlog = np.log10(self.d_categories)
        dndlogdp = np.array(
            [self.data[f"b{i}partconc"]/(dlog[i+1]-dlog[i])
             for i in range(len(dlog)-1)]
            )
        dndlogdp = np.mean(dndlogdp,axis=1)
        xvals = self.d_categories[:-1]
        widths = self.d_categories[1:] - self.d_categories[:-1]
        print(*dndlogdp)
        #draw
        _,ax = plt.subplots()
        ax.bar(x=xvals,width=widths,align="edge",height=dndlogdp)
        ax.set_yscale("log")
        ax.set_ylabel("dN/dlog$D_p$")
        ax.set_xscale("log")
        ax.set_xlabel("$D_p$ in nm")
        plt.show()        
        
        
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
        
        data = self.data[y]
        mean = np.mean(data)
        std = np.std(data,ddof=1)
        var = np.var(data,ddof=1)
        print(f"\nSTATS:\n{self.details[y][0]} in {self.details[y][1]}:")
        print(f"\tmean {mean}\n\tstd  {std}\n\tvar  {var}")
    
        
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
        
        data = self.data["y"]
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
            
        for key in self.data:
            try:
                self.data[key] = np.append(self.data[key],obj.data[key])
            except:
                msg = f"WARNING: {key} is not loaded in the Pops obj that "
                msg += "should be appended"
                print(msg)
                
                
                
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
        
        for key in self.data:
            try:
                newpops.data[key] = np.append(self.data[key],obj.data[key])
            except:
                msg = f"WARNING: {key} is not loaded in the Pops obj that "
                msg += "should be appended"
                print(msg)
                
        return newpops
    
    
    def deviatefrommean(self):
        """
        Changes all data to be expressed relative to the mean

        Returns
        -------
        None.

        """
        
        for key in self.data:
            if key != "t" and key != "popstime":
                mean = np.mean(self.data[key])
                self.data[key] = ((self.data[key]/mean)-1)*100
                self.details[key][1] = self.details[key][1] + " (normalised)"
                
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
        
        for key in self.data:
            try:
                if key != "t" and key != "popstime":
                    mean = np.mean(bgobj.data[key])
                    self.data[key] = ((self.data[key]/mean)-1)*100
                    self.details[key][1] = f"{self.details[key][1]} (normalised)"
            except:
                msg = f"WARNING: {key} is not loaded in the Pops obj that "
                msg += "should be appended. {key} will not be expressed "
                msg += "relatively"
                print(msg)
            
        self.relative = True
    
    
    def average(self):
        """
        Averages all data minutewise
        
        .. deprecated:: 0.2.5
            This method was last updated in agg_dim 0.2.5 and might be removed
            soon since it was succeeded by Pops.desample.

        Returns
        -------
        None.

        """
        
        msg = "WARNING: Pops.average() is deprecated and might be removed soon"
        msg += ". Consider using Pops.desample() instead."
        print(msg)
        self.desample(60)
    
    def desample(self,samplesize):
        """
        Averages all data by a custom amount of seconds
        
        Parameters
        ----------
        samplesize : int
            The data will be desampled to chunks of this many seconds (e.g. 
            `samplesize=60` means minutewise averaging)

        Returns
        -------
        None.

        """
        
        n1 = len(self.data["t"]) // samplesize
        n2 = len(self.data["popstime"]) // samplesize
        for key in self.data:
            if key != "t" and key != "popstime":
                if key in self.ydata:
                    yy = self.data[key][:n1*samplesize].reshape(
                        -1,
                        samplesize
                        ).mean(axis=1)
                    self.data[key] = np.append(
                        yy,
                        np.mean(self.data[key][n1*samplesize:])
                        )
                else:
                    yy = self.data[key][:n2*samplesize].reshape(
                        -1,
                        samplesize
                        ).mean(axis=1)
                    self.data[key] = np.append(
                        yy,
                        np.mean(self.data[key][n2*samplesize:])
                        )
            elif key == "t":
                self.data[key] = np.append(
                    self.data[key][:n1*samplesize:samplesize],
                    self.data[key][n1*samplesize]
                    ) + dt.timedelta(seconds=samplesize/2)
            else:
                self.data[key] = np.append(
                    self.data[key][:n2*samplesize:samplesize],
                    self.data[key][n2*samplesize]
                    ) + dt.timedelta(seconds=samplesize/2)
        
        
    def returndata(self):
        """
        Returns a tuple containing all data in a standardized form. 
        Important for communication with `DroneWrapper` or `Wrapper` objs.

        Returns
        -------
        op : dict {str : np.array}
            This dict contains all data in the form of np.arrays indexed by their name.
        op_details : dict {str : [str,str]}
            This dict contains a description and a unit for all the data saved in op.

        """
        
        return self.data,self.details
        
        
    #housekeeping funcs    
    def _hk_kwargs(self,kwargs,key,default):
        """
        @private
        Housekeeping Func --> no usecase outside obj
        
        Turns kwargs into attributes
        """
        
        op = kwargs[key] if key in kwargs else default
        setattr(self, key, op)
        
        
    def _hk_func_kwargs(self,kwargs,key,default):
        """
        @private
        Housekeeping func --> no usecase outside obj
        
        Gives kwargs a default value if they are not passed
        """
        
        op = kwargs[key] if key in kwargs else default
        return op
    
    
    def _hk_errorhandling(self,kwargs,legallist,funcname):
        """
        @private
        Housekeeping func --> no usecase outside obj
        
        Checks if all passed kwargs are legal
        """
        
        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)

 
    def _hk_returncropmask(self,cropby,start,end):
        """
        @private
        Housekeeping Func --> no usecase outside obj 
        
        Helps with cropping data to a timewindow
        """
        
        y = cropby[0].year
        m = cropby[0].month
        d = cropby[0].day
        if start != "none":
            start = dt.datetime.strptime(
                f"{y}.{m}.{d}-{start}",
                "%Y.%m.%d-%H:%M:%S"
                )
        else:
            start = dt.datetime(1199,1,1,11,11,11)
        if end != "none":
            end = dt.datetime.strptime(
                f"{y}.{m}.{d}-{end}",
                "%Y.%m.%d-%H:%M:%S"
                )
        else:
            end = dt.datetime(2999,1,1,11,11,11)
            
        return np.array([start<=i<=end for i in cropby])
 


class OPC:

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
            
        Attributes
        ----------
        data : {str : 1D numpy array}
            contains all the acquired data in the form of a dictionary
        details : {str : [str, str]}
            contains a description and the unit to each data array

        """
        
        #kwargs
        defaults = {"mfile" : file.replace("C.","M."),
                    "dmfile" : file.replace("C.","dM."),
                    "start" : None,
                    "end" : None,
                    "bins" : [0.253,0.298,0.352,0.414,0.488,0.576,0.679,0.8,0.943,1.112,1.31,1.545,1.821,2.146,2.53,2.982,3.515,4.144,4.884,5.757,6.787,8,9.43,11.12,13.1,15.45,18.21,21.46,25.3,29.82,35.15]}
        for key,value in zip(defaults.keys(),defaults.values()):
            self._hk_kwargs(kwargs, key, value)
        self._hk_errorhandling(kwargs, defaults.keys(), "OPC")
        
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
            except Exception as exc:
                raise FileNotFoundError(f"File {self.mfile} not found. If it has been renamed or moved, pass the new name/path as 'mfile' to OPC.__init__()") from exc
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
                    dmdata = dmdata[1:]
            except Exception as exc:
                raise FileNotFoundError(f"File {self.dmfile} not found. If it has been renamed or moved, pass the new name/path as 'dmfile' to OPC.__init__()") from exc
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
            with open(file,"rb") as openfile:
                self.data,self.details = pickle.load(openfile)
            
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
            kwargs[key] = self._hk_func_kwargs(kwargs,key,default)
        self._hk_errorhandling(kwargs, defaults.keys(), "OPC.plot()")
        
        if kwargs["ylabel"] == "*":
            kwargs["ylabel"] = f"{self.details[y][0]} in {self.details[y][1]}"
        
        #draw plot
        x = self.data["t"]
        if isinstance(kwargs["setday"],str):
            date = [int(kwargs["setday"][:2]),int(kwargs["setday"][2:4]),int(kwargs["setday"][4:])]
            for i in range(len(x)):
                x[i] = x[i].replace(day=date[0],month=date[1],year=date[2])
        try:
            y = self.data[y]
        except KeyError as kerr:
            raise IllegalValue(y, "OPC.plot()", list(self.data)) from kerr
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
            kwargs[key] = self._hk_func_kwargs(kwargs,key,default)
        self._hk_errorhandling(kwargs, defaults.keys(), "OPC.heatmap()")
                
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
            kwargs[key] = self._hk_func_kwargs(kwargs,key,default)
        self._hk_errorhandling(kwargs, defaults.keys(), "OPC.dndlogdp()")
        
        #draw plot
        m = np.full(len(self.data["t"]),True)
        if isinstance(kwargs["start"],str):
            kwargs["start"] = dt.datetime.strptime(kwargs["start"], "%H:%M:%S").time()
            m = np.where(self.data["t_noday"] > kwargs["start"],m,False)
        if isinstance(kwargs["end"],str):
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
        if isinstance(kwargs["ylabel"],str):
            ax.set_ylabel(kwargs["ylabel"])
        else:
            ax.set_ylabel("dN/dlog$D_P$ in cm${}^{-3}$")
            
            
    def returndata(self):
        """
        Returns a tuple containing all data in a standardized form. Important 
        for communication with DroneWrapper or Wrapper objs.

        Returns
        -------
        data : dict {str : np.array}
            This dict contains all data in the form of np.arrays indexed by 
            their name.
        details : dict {str : [str,str]}
            This dict contains a description and a unit for all the 
            exported data.
        """
        
        op_t = [self.data["t"][0]]
        ts = op_t[0]
        while ts < self.data["t"][-1]:
            ts = op_t[-1] + dt.timedelta(seconds=1)
            op_t.append(ts)
        op_dict = {"t" : np.array(op_t)}
        
        for key in self.data.keys():
            if key == "t" or key == "t_noday":
                continue
            op = []
            for t in op_t:
                if t in self.data["t"]:
                    op_item = self.data[key][np.where(self.data["t"]==t)[0][0]]
                    op.append(op_item)
                else:
                    op.append(np.nan)
            op_dict[key] = np.array(op)
        return op_dict,self.details
    
    def append(self,opc):
        """
        Adds another `OPC` obj to the current one.

        Parameters
        ----------
        opc : OPC
            The data of this obj will be appended to self.

        Returns
        -------
        None
        """
        
        for key in self.data:
            self.data[key] = np.append(
                self.data[key],
                opc.data[key]
                )
        
        
    #housekeeping funcs    
    def _hk_kwargs(self,kwargs,key,default):
        """Turns kwargs into attributes"""
        
        op = kwargs[key] if key in kwargs else default
        setattr(self,key,op)
        
        
    def _hk_func_kwargs(self,kwargs,key,default):
        """Gives kwargs a default value if they are not passed"""
 
        op = kwargs[key] if key in kwargs else default
        return op
    
    
    def _hk_errorhandling(self,kwargs,legallist,funcname):
        """Checks if all passed kwargs are legal"""
        
        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)
                
                