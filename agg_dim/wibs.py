# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 08:26:00 2024

@author: mrupp
"""


from datetime import datetime,timezone
import h5py
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.dates as md
import pickle

from .ErrorHandler import IllegalValue,IllegalArgument

class WIBS:
    
    """
    Inits the WIBS obj

    Parameters
    ----------
    file : str or list of str
        Either the path to a wibs produced .h5 file or to a preprocessed .wibs file or a list of paths to wibs produced .h5 files.
    FT_file : str
        Path to a wibs produced forcedtrigger-file. Can be left if a preprocessed .wibs file is passed as file.
    FT_time : str
        String in the form of 'hh:mm:ss' of the time when the forced trigger was started, which is used to correct the time. Can be left if a preprocessed .wibs file is passed as file.
    FT_sigma : int or float, optional
        Will be used as sigma for data processing. The default is 3.
    bin_borders : list of float, optional
        Particles will be classified according to the bins given here (in micrometers). The default is [0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,1.7,2,2.5,3,3.5,4,5,10,15,20]
    flow : float, optional
        Flow in ccm/s. Will be used to calculate partconc and dndlogdp. The default is 0.018 ccm/s (=0.3 lpm).
    fixed : list of floats with len 3, optional
        If fixed is passed, the values will be treated as bg and FT_file will only be used for time correction.
    start : str, optional
        String in the form 'hh:mm:ss'. If start is given, all data acquired before this timestamp will be ignored.
    end : str, optional
        String in the form 'hh:mm:ss'. If end is given, all data acquired after this timestamp will be ignored.
    FT_date : str, optional
        Sets the FT_time to be this date (str format: 'dd.mm.yyyy'), only relevant if the data is going to be compared with other data. The default is '01.01.2000'

    Variables
    ---------
    WIBS.bins : int
        Number of bins
    WIBS.bin_means : list of float
        Geometric means of bins. Used for dndlogdp stuff.
    WIBS.data : {str : 1D numpy array}
        contains all processed data in the form of a dictionary (processed for every second)
    WIBS.details : {str : [str, str]}
        contains a description and the unit to each data array
    WIBS.rawdata : {str : 1D numpy array}
        conains all the raw data used for data processing
    WIBS.fl1_FTbg : float
        Contains the fluorescence of the chamber for fl1, calculated from the forced trigger.
    WIBS.fl2_FTbg : float
        Contains the fluorescence of the chamber for fl2, calculated from the forced trigger.
    WIBS.fl3_FTbg : float
        Contains the fluorescence of the chamber for fl3, calculated from the forced trigger.
    """
    
    def __init__(self,file,FT_file="",FT_time="hh:mm:ss",**kwargs):
        """
        Inits the WIBS obj

        Parameters
        ----------
        file : str or list of str
            Either the path to a wibs produced .h5 file or to a preprocessed .wibs file or a list of paths to wibs produced .h5 files.
        FT_file : str
            Path to a wibs produced forcedtrigger-file. Can be left if a preprocessed .wibs file is passed as file.
        FT_time : str
            String in the form of 'hh:mm:ss' of the time when the forced trigger was started, which is used to correct the time. Can be left if a preprocessed .wibs file is passed as file.
        FT_sigma : int or float, optional
            Will be used as sigma for data processing. The default is 3.
        bin_borders : list of float, optional
            Particles will be classified according to the bins given here (in micrometers). The default is [0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,1.7,2,2.5,3,3.5,4,5,10,15,20]
        flow : float, optional
            Flow in ccm/s. Will be used to calculate partconc and dndlogdp. The default is 0.018 ccm/s (=0.3 lpm).
        fixed : list of floats with len 3, optional
            If fixed is passed, the values will be treated as bg and FT_file will only be used for time correction.
        start : str, optional
            String in the form 'hh:mm:ss'. If start is given, all data acquired before this timestamp will be ignored.
        end : str, optional
            String in the form 'hh:mm:ss'. If end is given, all data acquired after this timestamp will be ignored.
        FT_date : str, optional
            Sets the FT_time to be this date (str format: 'dd.mm.yyyy'), only relevant if the data is going to be compared with other data. The default is '01.01.2000'
        channels : list of str, optional
            Decides which channels should be processed, by default all channels are processed, but it can be reduced for large files. The default is  ["a","b","c","ab","ac","bc","abc"].

        """
        
        if file[-5:] == ".wibs":
            
            ip = pickle.load(open(file,"rb"))
            
            for arg in ip.keys():
                exec(f"self.{arg} = ip[arg]")
                
        else:
        
            #import kwargs
            defaults = {
                "FT_sigma" : 3,
                "bin_borders" : [0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,1.7,2,2.5,3,3.5,4,5,10,15,20],
                "flow" : 0.3*1000/60,
                "fixed" : None, #[float,flat,float]
                "start" : None,
                "end" : None,
                "FT_date" : "01.01.2000",
                "channels" :  ["a","b","c","ab","ac","bc","abc"]
                }
            for key,value in defaults.items():
                self.hk_kwargs(kwargs, key, value)
            self.hk_errorhandling(kwargs, defaults.keys(), "WIBS")
            
            #setup variables
            self.bins = len(self.bin_borders)-1
            self.bin_means = [math.sqrt(self.bin_borders[i] * self.bin_borders[i+1]) for i in range(self.bins)]
            self.data = {}
            self.rawdata = {}
            self.details = {} #[name,unit]
            if self.fixed != None:
                self.fl1_FTbg = self.fixed[0]
                self.fl2_FTbg = self.fixed[1]
                self.fl3_FTbg = self.fixed[2]
            
            
            #load Forced Trigger
            
            if FT_file == "":
                raise KeyError("WIBS needs a FT_file unless preprocessed data (.wibs-file) is used")
    
            try:
                ft = h5py.File(FT_file,"r")
            except:
                raise FileNotFoundError("Cant find FT_file at given path")
            ft2 = ft["NEO"]
            ft3 = ft2["ParticleData"]
            
            ft_xe1 = np.transpose(list(ft3["Xe1_FluorPeak"]))
            ft_xe2 = np.transpose(list(ft3["Xe2_FluorPeak"]))
            self.start_FT = datetime.fromtimestamp(list(ft3["Seconds"])[0],tz=timezone.utc).replace(year=int(self.FT_date[-4:]),month=int(self.FT_date[3:5]),day=int(self.FT_date[:2]))
            
            
            FT_time = datetime.strptime(f"{self.FT_date}-{FT_time}/+0000","%d.%m.%Y-%H:%M:%S/%z")
            timecorr = FT_time - self.start_FT
            
            if self.fixed == None:
                self.fl1_FTbg = np.mean(ft_xe1[0]) + self.FT_sigma * np.std(ft_xe1[0])
                self.fl2_FTbg = np.mean(ft_xe1[1]) + self.FT_sigma * np.std(ft_xe1[1])
                self.fl3_FTbg = np.mean(ft_xe2[1]) + self.FT_sigma * np.std(ft_xe2[1])
            
            
            #load file
            if type(file) == str:
                try:
                    f = h5py.File(file,"r")
                except:
                    raise FileNotFoundError("Cant find file at given path")
                f2 = f["NEO"]
                f3 = f2['ParticleData']
                
                wibstime = list(f3["Seconds"])
                self.timehandler = np.array(wibstime).astype(np.uint32)
                
                xe1 = np.transpose(list(f3["Xe1_FluorPeak"]))
                xe2 = np.transpose(list(f3["Xe2_FluorPeak"]))
                
                self.rawdata["size"] = np.array(list(f3["Size_um"]))
                self.rawdata["excited"] = np.array(list(f3["Flag_Excited"])).astype(bool)
                self.rawdata["Fl1"] = np.where(xe1[0] >= self.fl1_FTbg, True, False)
                self.rawdata["Fl2"] = np.where(xe1[1] >= self.fl2_FTbg, True, False)
                self.rawdata["Fl3"] = np.where(xe2[1] >= self.fl3_FTbg, True, False)
                
    
            #load files
            elif type(file) == list:
    
                firstfile = True
                
                for ff in file:
                    f = h5py.File(ff,"r")
                    f2 = f["NEO"]
                    f3 = f2['ParticleData']
                    
                    filetime = list(f3["Seconds"])
                    th = np.array(filetime).astype(np.uint32)
                    
                    xe1 = np.transpose(list(f3["Xe1_FluorPeak"]))
                    xe2 = np.transpose(list(f3["Xe2_FluorPeak"]))
                    if len(xe1) == 0 or len(xe2) == 0:
                        continue
                    
                    filecounts = np.array(list(f3["Size_um"]))
                    file_excited = np.array(list(f3["Flag_Excited"])).astype(bool)
                    filefl1 = np.where(xe1[0] >= self.fl1_FTbg, True, False)
                    filefl2 = np.where(xe1[1] >= self.fl2_FTbg, True, False)
                    filefl3 = np.where(xe2[1] >= self.fl3_FTbg, True, False)
                    
                    if firstfile:
                        self.timehandler = th.astype(np.uint32)
                        self.rawdata["size"] = filecounts
                        self.rawdata["excited"] = file_excited
                        self.rawdata["Fl1"] = filefl1
                        self.rawdata["Fl2"] = filefl2
                        self.rawdata["Fl3"] = filefl3
                        firstfile = False
                    else:
                        self.timehandler = np.append(self.timehandler,th).astype(np.uint32)
                        self.rawdata["size"] = np.append(self.rawdata["size"],filecounts)
                        self.rawdata["excited"] = np.append(self.rawdata["excited"],file_excited)
                        self.rawdata["Fl1"] = np.append(self.rawdata["Fl1"],filefl1)
                        self.rawdata["Fl2"] = np.append(self.rawdata["Fl2"],filefl2)
                        self.rawdata["Fl3"] = np.append(self.rawdata["Fl3"],filefl3)
               
             
            if type(self.start) == str:
                starttime = datetime.strptime(f"{self.FT_date}-{self.start}/+0000","%d.%m.%Y-%H:%M:%S/%z")
                starttime = int(starttime.replace(year=int(self.FT_date[-4:])).timestamp())
                if int(timecorr.total_seconds()) >= 0:
                    start_m = np.where((self.timehandler + int(timecorr.total_seconds())) > starttime, True, False)
                else:
                    offset = abs(int(timecorr.total_seconds()))
                    start_m = np.where((self.timehandler - offset) > starttime, True, False)
                self.timehandler = self.timehandler[start_m]
                self.rawdata["size"] = self.rawdata["size"][start_m]
                self.rawdata["excited"] = self.rawdata["excited"][start_m]
                self.rawdata["Fl1"] = self.rawdata["Fl1"][start_m]
                self.rawdata["Fl2"] = self.rawdata["Fl2"][start_m]
                self.rawdata["Fl3"] = self.rawdata["Fl3"][start_m]
                del start_m
            if type(self.end) == str:
               endtime = datetime.strptime(f"{self.FT_date}-{self.end}/+0000","%d.%m.%Y-%H:%M:%S/%z")
               endtime = int(endtime.replace(year=int(self.FT_date[-4:])).timestamp())
               if int(timecorr.total_seconds()) >= 0:
                   end_m = np.where((self.timehandler + int(timecorr.total_seconds())) < endtime,True,False)
               else:
                   offset = abs(int(timecorr.total_seconds()))
                   end_m = np.where((self.timehandler - offset) < endtime,True,False)
                   print(self.timehandler[0] - offset)
                   print(endtime)
               self.timehandler = self.timehandler[end_m] 
               self.rawdata["size"] = self.rawdata["size"][end_m]
               self.rawdata["excited"] = self.rawdata["excited"][end_m]
               self.rawdata["Fl1"] = self.rawdata["Fl1"][end_m]
               self.rawdata["Fl2"] = self.rawdata["Fl2"][end_m]
               self.rawdata["Fl3"] = self.rawdata["Fl3"][end_m]
               del end_m
    
                
            #process data
            self.data["t"] = np.array([datetime.utcfromtimestamp(timestamp) for timestamp in range(self.timehandler[0],self.timehandler[-1])]) + timecorr
            self.date = [self.data["t"][0].day,self.data["t"][0].month,self.data["t"][0].year]
            time_mask = np.array([np.where(self.timehandler==i,True,False) for i in range(self.timehandler[0],self.timehandler[-1])])
                    
            #part_conc & #/s
            for bin_no in range(self.bins):
                m = np.where(self.bin_borders[bin_no] < self.rawdata["size"],True,False)
                m = np.where(self.bin_borders[bin_no+1] > self.rawdata["size"],m,False)
                bin_handler = time_mask & m
                self.data[f"bin{bin_no}_cps"] = np.array([np.count_nonzero(arr) for arr in bin_handler])
                del bin_handler
                self.data[f"bin{bin_no}_partconc"] = self.data[f"bin{bin_no}_cps"] / self.flow
                self.details[f"bin{bin_no}_partconc"] = [f"Particle Conc. (bin{bin_no}) ","#/cm${}^3$"]
                self.details[f"bin{bin_no}_cps"] = [f"Particle Counts (Bin{bin_no})","#/s"]
                
            #dndlogdp
            for bin_no in range(self.bins):
                log_binwidth = np.log10(self.bin_borders[bin_no+1])-np.log10(self.bin_borders[bin_no])
                self.data[f"bin{bin_no}_dndlogdp"] = self.data[f"bin{bin_no}_partconc"] / log_binwidth
                self.details[f"bin{bin_no}_dndlogdp"] = [f"dN/dlog$D_P$ (Bin{bin_no})","$\mu$m${}^{-1}$"]
                
            #total
            self.data["total_cps"] = np.sum([self.data[f"bin{i}_cps"] for i in range(self.bins)],axis=0)
            self.data["total_partconc"] = self.data["total_cps"] / self.flow
            self.details["total_cps"] = ["Particle Counts","#/s"]
            self.details["total_partconc"] = ["Particle Conc.","#/cm${}^3$"]
            
            
            #excited
            ex_handler = time_mask & self.rawdata["excited"]
            self.data["excited"] = np.array([np.count_nonzero(arr) for arr in ex_handler])
            del ex_handler
            self.data["excited_fraction"] = np.divide(self.data["excited"],self.data["total_cps"],out=np.zeros(self.data["excited"].shape,dtype=float),where=self.data["total_cps"]!=0)
            self.details["excited"] = ["Particle Counts (excited)","#/s"]
            self.details["excited_fraction"] = ["Fraction of excited Particles", "No Unit"]
            
            
            #fluorescence channels
            fl1_handler = time_mask & self.rawdata["Fl1"]
            fl2_handler = time_mask & self.rawdata["Fl2"]
            fl3_handler = time_mask & self.rawdata["Fl3"]
            
            self.data["fl1"] = np.array([np.count_nonzero(arr) for arr in fl1_handler])/self.data["excited_fraction"]
            self.data["fl2"] = np.array([np.count_nonzero(arr) for arr in fl2_handler])/self.data["excited_fraction"]
            self.data["fl3"] = np.array([np.count_nonzero(arr) for arr in fl3_handler])/self.data["excited_fraction"]
            self.data["fl1_fraction"] = np.divide(self.data["fl1"],self.data["total_cps"],out=np.zeros(self.data["fl1"].shape,dtype=float),where=self.data["total_cps"]!=0)
            self.data["fl2_fraction"] = np.divide(self.data["fl2"],self.data["total_cps"],out=np.zeros(self.data["fl2"].shape,dtype=float),where=self.data["total_cps"]!=0)
            self.data["fl3_fraction"] = np.divide(self.data["fl3"],self.data["total_cps"],out=np.zeros(self.data["fl3"].shape,dtype=float),where=self.data["total_cps"]!=0)
            for i in [1,2,3]:
                self.details[f"fl{i}"] = [f"Particle Counts (Fl{i})","#/s"]
                self.details[f"fl{i}_fraction"] = [f"Fluorescent Fraction (Fl{i})", "No Unit"]
            
            def createmask(a,b,c,string):
                a = a if "a" in string else ~a
                b = b if "b" in string else ~b
                c = c if "c" in string else ~c
                
                op = a&b
                return op&c
            
            for channel in self.channels:
                channel_mask = createmask(fl1_handler,fl2_handler,fl3_handler,channel)
                for bin_no in range(self.bins):
                    m =np.where(self.bin_borders[bin_no] < self.rawdata["size"],True,False)
                    m = np.where(self.bin_borders[bin_no+1] > self.rawdata["size"],m,False)
                    m = channel_mask & m
                    self.data[f"{channel}_bin{bin_no}_cps"] = np.array([np.count_nonzero(arr) for arr in m])
                    del m
                    self.data[f"{channel}_bin{bin_no}_partconc"] = self.data[f"{channel}_bin{bin_no}_cps"] / self.flow
                    self.details[f"{channel}_bin{bin_no}_partconc"] = [f"Particle Conc. of {channel}-Particles (bin{bin_no}) ","#/cm${}^3$"]
                    self.details[f"{channel}_bin{bin_no}_cps"] = [f"Particle Counts of {channel}-Particles (Bin{bin_no})","#/s"]
                    
                    log_binwidth = np.log10(self.bin_borders[bin_no+1])-np.log10(self.bin_borders[bin_no])
                    self.data[f"{channel}_bin{bin_no}_dndlogdp"] = self.data[f"{channel}_bin{bin_no}_partconc"] / log_binwidth
                    self.details[f"{channel}_bin{bin_no}_dndlogdp"] = [f"dN/dlog$D_P$ of {channel}-Particles (Bin{bin_no})","$\mu$m${}^{-1}$"]
                   
                del channel_mask
                self.data[f"{channel}_total_cps"] = np.sum([self.data[f"{channel}_bin{i}_cps"] for i in range(self.bins)],axis=0)
                self.data[f"{channel}_total_partconc"] = self.data[f"{channel}_total_cps"] / self.flow
                self.data[f"{channel}_fraction"] = np.divide(self.data[f"{channel}_total_cps"],self.data["total_cps"],out=np.zeros(self.data[f"{channel}_total_cps"].shape,dtype=float),where=self.data["total_cps"]!=0)
                self.details[f"{channel}_total_cps"] = [f"Particle Counts of {channel}-Particles","#/s"]
                self.details[f"{channel}_total_partconc"] = [f"Particle Conc. of {channel}-Particles","#/cm${}^3$"]
                self.details[f"{channel}_fraction"] = [f"Fluorescent Fraction ({channel})", "No Unit"]
                
            del self.timehandler
            del self.start
            del self.end
            del self.FT_date
            
    
    def quickplot(self,y):
        """
        Plots the given y over time

        Parameters
        ----------
        y : str
            Determines which data should be plotted.

        Returns
        -------
        None.

        """
        
        #error handling
        xx = self.data["t"]
        try:
            yy = self.data[y]
        except KeyError:
            raise IllegalValue(y, "WIBS.quickplot()",[key for key in self.data])
                
        #draw plot
        fig,ax = plt.subplots()

        ax.set_xlabel("CET")
        ylabel = f"{self.details[y][0]} in {self.details[y][1]}" if self.details[y][1] != "No Unit" else self.details[y][0]
        ax.set_ylabel(ylabel)
        
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        ax.plot(xx,yy)
        
        plt.show()
        
        
    def quickheatmap(self,y):
        """
        Draws a dndlogdp number size distribution heatmap

        Parameters
        ----------
        y : str
            Determines which data should be plotted.

        Returns
        -------
        None.

        """
        
        #error handling
        try:
            yy = np.array([self.data[f"{y}_bin{i}_dndlogdp"] for i in range(self.bins)]) if y != "allparticles" else np.array([self.data[f"bin{i}_dndlogdp"] for i in range(self.bins)])
        except KeyError:
            raise IllegalValue(y, "WIBS.quickheatmap", ["allparticles","a","b","c","ab","ac","bc","abc"])
        
        xlims = [self.data["t"][0],self.data["t"][-1]]
        xlims = md.date2num(xlims)
            
        #draw plot
        fig,ax = plt.subplots()
        
        im = ax.imshow(yy,aspect="auto",norm="log",extent=[xlims[0],xlims[1],0,self.bins],cmap="RdYlBu_r",interpolation="none",origin="lower")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("$D_P$ in $\mu$m")
        ax.set_xlabel("CET")
        
        labels = [str(round(label,2)) for label in self.bin_means]
        ticks = [tick+0.5 for tick in range(self.bins)]
        ax.set_yticks(ticks,labels=labels)
        
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        plt.colorbar(im,ax=ax,label="dN/dlog$D_P$ in cm${}^{-3}$")
        
        plt.show()
        
        
    def heatmap(self,ax,y,**kwargs):
        """
        Draws a dndlogdp number size distribution heatmap over an existing mpl axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The heatmap will be drawn on this axis.
        y : str
            Determines which data should be plotted.
        cmap : str, optional
            Changes the colormap. The default is 'RdYlBu_r'
        pad : float, optional
            Changes the padding between colorbar and plot. The default is 0.
        orientation : str, optional
            Changes the orientation of the colorbar.
        location : str, optional
            Changes the location of the colorbar. The default is 'top'.
        togglecbar : bool, optional
            If False, the colorbar wont be shown. The default is True.

        Returns
        -------
        None.

        """
        
        defaults = {"cmap" : "RdYlBu_r",
                    "pad" : 0,
                    "orientation" : "horizontal",
                    "location" : "top",
                    "togglecbar" : True}
        for key,default in defaults.items():
            kwargs[key] = self.hk_func_kwargs(kwargs, key, default)
        self.hk_errorhandling(kwargs, defaults.keys(), "WIBS.heatmap()")
        
        try:
            yy = np.array([self.data[f"{y}_bin{i}_dndlogdp"] for i in range(self.bins)]) if y != "allparticles" else np.array([self.data[f"bin{i}_dndlogdp"] for i in range(self.bins)])
        except KeyError:
            raise IllegalValue(y, "WIBS.heatmap()", ["allparticles","a","b","c","ab","ac","bc","abc"])
        
        xlims = [self.data["t"][0],self.data["t"][-1]]
        xlims = md.date2num(xlims)
            
        #draw plot
        im = ax.imshow(yy,aspect="auto",norm="log",extent=[xlims[0],xlims[1],0,self.bins],cmap=kwargs["cmap"],interpolation="none",origin="lower")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("$D_P$ in $\mu$m")
        ax.set_xlabel("CET")
        
        labels = [str(round(label,2)) for label in self.bin_means]
        ticks = [tick+0.5 for tick in range(self.bins)]
        ax.set_yticks(ticks,labels=labels)
        
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        plt.colorbar(im,ax=ax,label="dN/dlog$D_P$ in cm${}^{-3}$",pad=kwargs["pad"],orientation=kwargs["orientation"],location=kwargs["location"])
        
    
    def plot(self,ax,y,**kwargs):
        """
        Plots y over time on an existing mpl axis.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        y : str
            Determines which data should be plotted.
        label : str, optional
            Changes the label of the plot. If a legend is created, this label will be shown there. The default is 'no label'.
        color : str
            Changes the color of the plot. The default is 'tab:purple'.
        secondary : bool, optional
            If True, the plot will draw the axis on the right-hand side. Should be used if the given ax is a twinx(). The default is False.
        
        Returns
        -------
        None.

        """

        defaults = {"label" : "no label",
                    "color" : "tab:purple",
                    "secondary" : False}
        for key,default in defaults.items():
            kwargs[key] = self.hk_func_kwargs(kwargs, key, default)
        self.hk_errorhandling(kwargs, defaults.keys(), "WIBS.plot()")
        
        xx = self.data["t"]
        try:
            yy = self.data[y]
        except KeyError:
            raise IllegalValue(y, "WIBS.plot()",[key for key in self.data])
            
        ylabel = f"{self.details[y][0]} in {self.details[y][1]}" if self.details[y][1] != "No Unit" else self.details[y][0]
            
        #draw plot
        ax.plot(xx,yy,label=kwargs["label"],color=kwargs["color"])
        
        ax.set_xlabel("CET")
        ax.set_ylabel(ylabel)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
            
    def save(self, path):
        """
        Saves the obj as a preprocessed .wibs file

        Parameters
        ----------
        path : str
            Determines the path and name, where the .wibs file should be saved.

        Returns
        -------
        None.

        """
        
        op = {
            "bins" : self.bins,
            "bin_means" : self.bin_means,
            "data" : self.data,
            "rawdata" : self.rawdata,
            "details" : self.details,
            "fl1_FTbg" : self.fl1_FTbg,
            "fl2_FTbg" : self.fl2_FTbg,
            "fl3_FTbg" : self.fl3_FTbg,
            "FT_sigma" : self.FT_sigma,
            "flow" : self.flow
            }
        
        if path[-5:] != ".wibs":
            path.append(".wibs")
            
        pickle.dump(op,open(path,"wb"),4)

    
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
