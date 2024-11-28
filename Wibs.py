# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 08:26:00 2024

@author: mrupp
"""


from datetime import datetime
import h5py
import numpy as np
import math
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.colors import LogNorm
from ErrorHandler import IllegalValue,NotPlottable,IllegalArgument

class WIBS:
    
    """full documentation see https://github.com/matrup01/data_import_modules \n
    
    file (str or list of str) ... takes a WIBS-produced h5-file or a list of WIBS-produced H5-files\n
    FT_file (str) ... takes a WIBS-produced h5-file and uses the FluorPeaks to calculate a background (give "none" if no FT was made)\n\n
    
    FT_sigma (int, optional) ... decides how many times std should be added to mean in FT, default-3\n
    timecorr (int, optional) ... takes an int and corrects the time by it (should be used for time differences between WIBS-computer and real time; weird WIBS time format should automatically be corrected)\n
    bin_borders (list of int, optional) ... takes a list of ints and uses them as bin borders in micro meters, default-[0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,1.7,2,2.5,3,3.5,4,5,10,15,20]\n
    flow (float) ... takes the volumetric flow rate in l/min, default-0.3\n
    loadexcited (bool) ... decides if excited particles are loaded (untoggle if facing performance issues), default-True\n
    loadfl1 (bool) ... decides if Fluorescence_1 is loaded (untoggle if facing performance issues), default-True\n
    loadfl2 (bool) ... decides if Fluorescence_2 is loaded (untoggle if facing performance issues), default-True\n
    loadfl3 (bool) ... decides if Fluorescence_3 is loaded (untoggle if facing performance issues), default-True\n
    FixedFT (list of int with len=3) ... takes 3 ints and takes them as FT-backgrounds, default values are completely random, default-[1000000,500000,300000]"""
    
    def __init__(self,file,FT_file,**kwargs):
        
        #import kwargs
        self.sigma = kwargs["FT_sigma"] if "FT_sigma" in kwargs else 3
        self.bin_borders = kwargs["bin_borders"] if "bin_borders" in kwargs else [0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,1.7,2,2.5,3,3.5,4,5,10,15,20]
        self.flow = kwargs["flow"]*1000/60 if "flow" in kwargs else 0.3*1000/60
        
        timecorr = kwargs["timecorr"] if "timecorr" in kwargs else 0
        wintertime = kwargs["wintertime"] if "wintertime" in kwargs else True
        loadexcited = kwargs["loadexcited"] if "loadexcited" in kwargs else True
        loadfl1 = kwargs["loadfl1"] if "loadfl1" in kwargs else True
        loadfl2 = kwargs["loadfl2"] if "loadfl2" in kwargs else True
        loadfl3 = kwargs["loadfl3"] if "loadfl3" in kwargs else True
        fixed = kwargs["FixedFT"] if "FixedFT" in kwargs else [100000,500000,300000]
        
        #setup variables
        self.bins = len(self.bin_borders)-1
        self.bin_means = [math.sqrt(self.bin_borders[i] * self.bin_borders[i+1]) for i in range(self.bins)]
        self.data = {}
        self.processed_data = {}
        self.misc = {} #[name,unit,plotable]
        
        #error handling
        for key in kwargs:
            if key not in ["FT_sigma","bin_borders","flow","timecorr","loadexcited","loadfl1","loadfl2","loadfl3","FixedFT"]:
                raise IllegalArgument(key,"WIBS")
        
        
        #load Forced Trigger
        if loadfl1 or loadfl2 or loadfl3:
            if FT_file == "none":
                
                #random values, load FT for accurate results
                self.fl1_FTbg,self.fl2_FTbg,self.fl3_FTbg = fixed
                
            else:
                ft = h5py.File(FT_file,"r")
                ft2 = ft["NEO"]
                ft3 = ft2["ParticleData"]
                
                ft_xe1 = np.transpose(list(ft3["Xe1_FluorPeak"]))
                ft_xe2 = np.transpose(list(ft3["Xe2_FluorPeak"]))
                
                if loadfl1: self.fl1_FTbg = np.mean(ft_xe1[0]) + self.sigma * np.std(ft_xe1[0])
                if loadfl2: self.fl2_FTbg = np.mean(ft_xe1[1]) + self.sigma * np.std(ft_xe1[1])
                if loadfl3: self.fl3_FTbg = np.mean(ft_xe2[1]) + self.sigma * np.std(ft_xe2[1])
        
        
        #load file
        if type(file) == str:
            f = h5py.File(file,"r")
            f2 = f["NEO"]
            f3 = f2['ParticleData']
            
            wibstime = list(f3["Seconds"])
            wibstime = [wibstime[i] - 3810797754 + 1727952954 for i in range(len(wibstime))] #correct weird WIBS dataformat
            if wintertime:
                wibstime = [wibstime[i] + 3600 - timecorr for i in range(len(wibstime))] #correct timezone and WIBS-computer time error
            else:
                wibstime = [wibstime[i] + 7200 - timecorr for i in range(len(wibstime))] #correct timezone and WIBS-computer time error
            self.wibstime = [datetime.utcfromtimestamp(wibstime[i]) for i in range(len(wibstime))] #convert to datetime
            
            xe1 = np.transpose(list(f3["Xe1_FluorPeak"]))
            xe2 = np.transpose(list(f3["Xe2_FluorPeak"]))
            
            self.data["size"] = list(f3["Size_um"])
            if loadexcited: self.data["excited"] = [bool(ex) for ex in list(f3["Flag_Excited"])]
            if loadfl1: self.data["Fl1"] = [False if np.isnan(i) or self.fl1_FTbg > i else True for i in xe1[0]]
            if loadfl2: self.data["Fl2"] = [False if np.isnan(i) or self.fl2_FTbg > i else True for i in xe1[1]]
            if loadfl3: self.data["Fl3"] = [False if np.isnan(i) or self.fl3_FTbg > i else True for i in xe2[1]]
            

        #load files
        if type(file) == list:
            wibstime = []
            sizes = []
            exs = []
            fl1 = []
            fl2 = []
            fl3 = []
            
            for ff in file:
                f = h5py.File(ff,"r")
                f2 = f["NEO"]
                f3 = f2['ParticleData']
                
                filetime = list(f3["Seconds"])
                filetime = [filetime[i] - 3810797754 + 1727952954 for i in range(len(filetime))] #correct weird WIBS dataformat
                if wintertime:
                    filetime = [filetime[i] + 3600 - timecorr for i in range(len(filetime))] #correct timezone and WIBS-computer time error
                else:
                    filetime = [filetime[i] + 7200 - timecorr for i in range(len(filetime))] #correct timezone and WIBS-computer time error
                filetime = [datetime.utcfromtimestamp(filetime[i]) for i in range(len(filetime))] #convert to datetime
                
                filecounts = list(f3["Size_um"])
                xe1 = np.transpose(list(f3["Xe1_FluorPeak"]))
                xe2 = np.transpose(list(f3["Xe2_FluorPeak"]))
                if loadexcited:
                    file_exc = list(f3["Flag_Excited"])
                    for e in file_exc:
                        exs.append(bool(e))
                if loadfl1: 
                    file_fl1 = [False if np.isnan(i) or self.fl1_FTbg > i else True for i in xe1[0]]
                    for ff1 in file_fl1:
                        fl1.append(ff1)
                if loadfl2: 
                    file_fl2 = [False if np.isnan(i) or self.fl2_FTbg > i else True for i in xe1[1]]
                    for ff2 in file_fl2:
                        fl2.append(ff2)
                if loadfl3: 
                    file_fl3 = [False if np.isnan(i) or self.fl3_FTbg > i else True for i in xe2[1]]
                    for ff3 in file_fl3:
                        fl1.append(ff3)
                
                for time,count in zip(filetime,filecounts):
                    wibstime.append(time)
                    sizes.append(count)
                    
            self.wibstime = wibstime
            self.data["size"] = sizes
            if loadexcited: self.data["excited"] = exs
            if loadfl1: self.data["Fl1"] = fl1
            if loadfl2: self.data["Fl2"] = fl2
            if loadfl3: self.data["Fl3"] = fl3

            
        #process data
        self.t = []
        self.timehandler = []
        for i in range(len(self.wibstime)):
            roundtime = self.wibstime[i].replace(microsecond=0)
            if roundtime not in self.t:
                self.t.append(roundtime)
                self.timehandler.append([i])
            else:
                self.timehandler[-1].append(i)
        self.date = [self.t[0].day,self.t[0].month,self.t[0].year]
                
        #counts per second
        cps = []
        for handler in self.timehandler:
            appender = [0 for i in range(self.bins)]
            for count in handler:
                appender[self.hk_binsorter(self.data["size"][count])] += 1
            cps.append(np.array(appender))
        self.processed_data["cps"] = cps
        self.misc["cps"] = ["Counts","#/s",False]
        
        #particle concentration
        partconc = []
        for dataset in self.processed_data["cps"]:
            conc = sum(dataset) / self.flow
            partconc.append(conc)
        self.processed_data["partconc"] = partconc
        self.misc["partconc"] = ["Particle Concentration","#/cm${}^3$",True]
            
        #dndlogdp
        dndlogdp = []
        for dataset in self.processed_data["cps"]:
            dat = self.hk_dndlogdp(dataset)
            dndlogdp.append(dat)
        self.processed_data["dndlogdp"] = dndlogdp
        self.misc["dndlogdp"] = ["dN/dlog$D_p$","cm${}^{-3}$",False]
        
        if loadexcited:
        
            #counts per second
            cps = []
            for handler in self.timehandler:
                appender = [0 for i in range(self.bins)]
                for count in handler:
                    if self.data["excited"][count]:
                        appender[self.hk_binsorter(self.data["size"][count])] += 1
                cps.append(np.array(appender))
            self.processed_data["ex_cps"] = cps
            self.misc["ex_cps"] = ["Counts (excited)","#/s",False]
            
            #particle concentration
            partconc = []
            for dataset in self.processed_data["ex_cps"]:
                conc = sum(dataset) / self.flow
                partconc.append(conc)
            self.processed_data["ex_partconc"] = partconc
            self.misc["ex_partconc"] = ["Particle Concentration (excited)","#/cm${}^3$",True]
                
            #dndlogdp
            dndlogdp = []
            for dataset in self.processed_data["ex_cps"]:
                dat = self.hk_dndlogdp(dataset)
                dndlogdp.append(dat)
            self.processed_data["ex_dndlogdp"] = dndlogdp
            self.misc["ex_dndlogdp"] = ["dN/dlog$D_p$ (excited)","cm${}^{-3}$",False]
        
        if loadfl1:
        
            #counts per second
            cps1 = []
            for handler in self.timehandler:
                appender = [0 for i in range(self.bins)]
                for count in handler:
                    if self.data["Fl1"][count]:
                        appender[self.hk_binsorter(self.data["size"][count])] += 1
                cps1.append(np.array(appender))
            self.processed_data["fl1_cps"] = cps1
            self.misc["fl1_cps"] = ["Counts (Fl1)","#/s",False]
            
            #particle concentration
            partconc1 = []
            for dataset in self.processed_data["fl1_cps"]:
                conc = sum(dataset) / self.flow
                partconc1.append(conc)
            self.processed_data["fl1_partconc"] = partconc1
            self.misc["fl1_partconc"] = ["Particle Concentration (Fl1)","#/cm${}^3$",True]
                
            #dndlogdp
            dndlogdp = []
            for dataset in self.processed_data["fl1_cps"]:
                dat = self.hk_dndlogdp(dataset)
                dndlogdp.append(dat)
            self.processed_data["fl1_dndlogdp"] = dndlogdp
            self.misc["fl1_dndlogdp"] = ["dN/dlog$D_p$ (Fl1)","cm${}^{-3}$",False]
            
        if loadfl2:
        
            #counts per second
            cps = []
            for handler in self.timehandler:
                appender = [0 for i in range(self.bins)]
                for count in handler:
                    if self.data["Fl2"][count]:
                        appender[self.hk_binsorter(self.data["size"][count])] += 1
                cps.append(np.array(appender))
            self.processed_data["fl2_cps"] = cps
            self.misc["fl2_cps"] = ["Counts (Fl2)","#/s",False]
            
            #particle concentration
            partconc = []
            for dataset in self.processed_data["fl2_cps"]:
                conc = sum(dataset) / self.flow
                partconc.append(conc)
            self.processed_data["fl2_partconc"] = partconc
            self.misc["fl2_partconc"] = ["Particle Concentration (Fl2)","#/cm${}^3$",True]
                
            #dndlogdp
            dndlogdp = []
            for dataset in self.processed_data["fl2_cps"]:
                dat = self.hk_dndlogdp(dataset)
                dndlogdp.append(dat)
            self.processed_data["fl2_dndlogdp"] = dndlogdp
            self.misc["fl2_dndlogdp"] = ["dN/dlog$D_p$ (Fl2)","cm${}^{-3}$",False]
            
        if loadfl3:
        
            #counts per second
            cps = []
            for handler in self.timehandler:
                appender = [0 for i in range(self.bins)]
                for count in handler:
                    if self.data["Fl3"][count]:
                        appender[self.hk_binsorter(self.data["size"][count])] += 1
                cps.append(np.array(appender))
            self.processed_data["fl3_cps"] = cps
            self.misc["fl3_cps"] = ["Counts (Fl3)","#/s",False]
            
            #particle concentration
            partconc = []
            for dataset in self.processed_data["fl3_cps"]:
                conc = sum(dataset) / self.flow
                partconc.append(conc)
            self.processed_data["fl3_partconc"] = partconc
            self.misc["fl3_partconc"] = ["Particle Concentration (Fl3)","#/cm${}^3$",True]
                
            #dndlogdp
            dndlogdp = []
            for dataset in self.processed_data["fl3_cps"]:
                dat = self.hk_dndlogdp(dataset)
                dndlogdp.append(dat)
            self.processed_data["fl3_dndlogdp"] = dndlogdp
            self.misc["fl3_dndlogdp"] = ["dN/dlog$D_p$ (Fl3)","cm${}^{-3}$",False]
            
    
    def quickplot(self,y):
        
        #error handling
        try: 
            ylabel = self.misc[y][0] + " in " + self.misc[y][1]
        except KeyError:
            legallist = []
            keys = self.misc.keys()
            for key in keys:
                if self.misc[key][2] == True:
                    legallist.append(key)
            raise IllegalValue("y","quickplot",legallist)
        if self.misc[y][2] == False:
            legallist = []
            keys = self.misc.keys()
            for key in keys:
                if self.misc[key][2] == True:
                    legallist.append(key)
            raise NotPlottable(y,"quickplot",legallist)
                
        #draw plot
        fig,ax = plt.subplots()

        ax.set_xlabel("CET")
        ax.set_ylabel(ylabel)

        
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        ax.plot(self.t,self.processed_data[y])
        
        plt.show()
        
        
    def quickheatmap(self,y):
        
        #error handling
        try: 
            ylabel = self.misc[y][0] + " in " + self.misc[y][1]
        except KeyError:
            legallist = []
            keys = self.misc.keys()
            for key in keys:
                if self.misc[key][2] == False:
                    legallist.append(key)
            raise IllegalValue("y","quickheatmap",legallist)
        if self.misc[y][2] == True:
            legallist = []
            keys = self.misc.keys()
            for key in keys:
                if self.misc[key][2] == False:
                    legallist.append(key)
            raise NotPlottable(y,"quickheatmap",legallist)
            
        #prepare data
        heatmap_t = deepcopy(self.t)
        newsec = heatmap_t[-1].second + 1
        heatmap_t.append(heatmap_t[-1].replace(second=newsec))
        xx,yy = np.meshgrid(heatmap_t,list(range(len(self.bin_borders))))
        
        heatmap_data = deepcopy(self.processed_data[y])
        heatmap_data = self.hk_replacezeros(heatmap_data)
        heatmap_data = np.ma.masked_where(np.isnan(heatmap_data),heatmap_data)
        heatmap_data = np.transpose(heatmap_data)
            
        #draw plot
        fig,ax = plt.subplots()
        
        im = ax.pcolormesh(xx,yy,heatmap_data,cmap="RdYlBu_r",norm=LogNorm(),shading="flat")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        #ax.set_yscale("log")
        ax.set_ylabel("optical diamter in $\mu$m")
        ax.set_xlabel("CET")
        labels = [math.sqrt(self.bin_borders[i]*self.bin_borders[i+1]) for i in range(self.bins)]
        labels = [str(round(label,2)) for label in labels]
        ticks = list(range(self.bins))
        ticks = [tick+0.5 for tick in ticks]
        ax.set_yticks(ticks,labels=labels)
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        plt.colorbar(im,ax=ax,label=ylabel)
        
        plt.show()
        
        
    def heatmap(self,ax,y,**kwargs):
        
        #import kwargs
        smooth = kwargs["smooth"] if "smooth" in kwargs else True
        cmap = kwargs["cmap"] if "cmap" in kwargs else "RdYlBu_r"
        pad = kwargs["pad"] if "pad" in kwargs else 0.01
        togglecbar = kwargs["togglecbar"] if "togglecbar" in kwargs else True
        xlims = kwargs["xlims"] if "xlims" in kwargs else "none"
        
        #error handling
        try: 
            ylabel = self.misc[y][0] + " in " + self.misc[y][1]
        except KeyError:
            legallist = []
            keys = self.misc.keys()
            for key in keys:
                if self.misc[key][2] == False:
                    legallist.append(key)
            raise IllegalValue("y","quickheatmap",legallist)
        if self.misc[y][2] == True:
            legallist = []
            keys = self.misc.keys()
            for key in keys:
                if self.misc[key][2] == False:
                    legallist.append(key)
            raise NotPlottable(y,"quickheatmap",legallist)
        for key in kwargs.keys():
            if key not in ["smooth","cmap","pad","togglecbar","xlims"]:
                raise IllegalArgument(key,"WIBS.heatmap()")
            
        #prepare data
        heatmap_t = deepcopy(self.t)
        if smooth:
            xx,yy = np.meshgrid(heatmap_t,[i+0.5 for i in range(self.bins)])
        else:
            newsec = heatmap_t[-1].second + 1
            heatmap_t.append(heatmap_t[-1].replace(second=newsec))
            xx,yy = np.meshgrid(heatmap_t,list(range(len(self.bin_borders))))

        heatmap_data = deepcopy(self.processed_data[y])
        heatmap_data = self.hk_replacezeros(heatmap_data)
        #heatmap_data = np.ma.masked_where(np.isnan(heatmap_data),heatmap_data)
        heatmap_data = np.transpose(heatmap_data)
        if type(xlims) == list:
            day,month,year = self.date
            ax.set_xlim([datetime.strptime(element,"%H:%M:%S").replace(day=day,month=month,year=year) for element in xlims])
            
        #draw plot
        if smooth:
            im = ax.pcolormesh(xx,yy,heatmap_data,cmap=cmap,norm=LogNorm(),shading="gouraud")
        else:
            im = ax.pcolormesh(xx,yy,heatmap_data,cmap=cmap,norm=LogNorm(),shading="flat")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("optical diamter in $\mu$m")
        ax.set_xlabel("CET")
        labels = [math.sqrt(self.bin_borders[i]*self.bin_borders[i+1]) for i in range(self.bins)]
        labels = [str(round(label,2)) for label in labels]
        ticks = list(range(self.bins))
        ticks = [tick+0.5 for tick in ticks]
        ax.set_yticks(ticks,labels=labels)
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        if togglecbar:
            plt.colorbar(im,ax=ax,label=ylabel,pad=pad)
        
    
    def plot(self,ax,y,**kwargs):
        
        label = kwargs["label"] if "label" in kwargs else "no label"
        color = kwargs["color"] if "color" in kwargs else "tab:orange"
        secondary = kwargs["secondary"] if "secondary" in kwargs else False
        
        #error handling
        try: 
            ylabel = self.misc[y][0] + " in " + self.misc[y][1]
        except KeyError:
            legallist = []
            keys = self.misc.keys()
            for key in keys:
                if self.misc[key][2] == True:
                    legallist.append(key)
            raise IllegalValue("y","quickplot",legallist)
        if self.misc[y][2] == False:
            legallist = []
            keys = self.misc.keys()
            for key in keys:
                if self.misc[key][2] == True:
                    legallist.append(key)
            raise NotPlottable(y,"quickplot",legallist)
        for key in kwargs.keys():
            if key not in ["label","color","secondary"]:
                raise IllegalArgument(key,"WIBS.plot()")
            
        #draw plot
        ax.plot(self.t,self.processed_data[y],label=label,color=color)
        
        ax.set_xlabel("CET")
        ax.set_ylabel(ylabel)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        ax.tick_params(axis='y', colors=color)
        if not secondary:
            ax.spines["left"].set_color(color)
        else:
            ax.spines["right"].set_color(color)
            ax.spines["left"].set_alpha(0)
    
    #housekeeping funcs
    
    def hk_binsorter(self,size):
        
        op = self.bins - 1
        
        for i in range(self.bins):
            if self.bin_borders[i] <= size and self.bin_borders[i+1] > size:
                op = i
                
        return op
    
    def hk_dndlogdp(self,arr):
        
        array = deepcopy(arr)
        
        for i in range(len(array)):
            array[i] = array[i] / (math.log10(self.bin_borders[i+1])-math.log10(self.bin_borders[i]))
            
        return array
    
    def hk_replacezeros(self,arr):
        
        array = deepcopy(arr)
        
        smallest = 10000
        for row in array:
            for element in row:
                if element < smallest and element > 0:
                    smallest = element
        for i in range(len(array)):
            for j in range(len(array[i])):
                if array[i][j] <= 0:
                    array[i][j] += smallest
                    
        return array