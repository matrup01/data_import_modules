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
from ErrorHandler import IllegalValue,NotPlottable

class WIBS:
    
    def __init__(self,file,timecorr=0,bin_borders=[0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,1.7,2,2.5,3,3.5,4,5,10,15,20],flow=0.3):
        
        self.bin_borders = bin_borders
        self.bins = len(self.bin_borders)-1
        self.bin_means = [math.sqrt(self.bin_borders[i] * self.bin_borders[i+1]) for i in range(self.bins)]
        self.processed_data = {}
        self.misc = {} #[name,unit,plotable]
        self.flow = flow * 1000 / 60 #flow in cc/s
        
        if type(file) == str:
            f = h5py.File(file,"r")
            f2 = f["NEO"]
            f3 = f2['ParticleData']
            
            wibstime = list(f3["Seconds"])
            wibstime = [wibstime[i] - 3810797754 + 1727952954 - 212 for i in range(len(wibstime))] #correct weird WIBS dataformat
            wibstime = [wibstime[i] + 7200 - timecorr for i in range(len(wibstime))] #correct timezone and WIBS-computer time error
            self.wibstime = [datetime.utcfromtimestamp(wibstime[i]) for i in range(len(wibstime))] #convert to datetime
            
            self.data = {"size" : list(f3["Size_um"]),
                         "excited" : [bool(ex) for ex in list(f3["Flag_Excited"])]}
            
            
            
        if type(file) == list:
            wibstime = []
            sizes = []
            exs = []
            
            for ff in file:
                f = h5py.File(ff,"r")
                f2 = f["NEO"]
                f3 = f2['ParticleData']
                
                filetime = list(f3["Seconds"])
                filetime = [filetime[i] - 3810797754 + 1727952954 - 212 for i in range(len(filetime))] #correct weird WIBS dataformat
                filetime = [filetime[i] + 7200 - timecorr for i in range(len(filetime))] #correct timezone and WIBS-computer time error
                filetime = [datetime.utcfromtimestamp(filetime[i]) for i in range(len(filetime))] #convert to datetime
                
                filecounts = list(f3["Size_um"])
                file_exc = list(f3["Flag_Excited"])
                
                for time,count,ex in zip(filetime,filecounts,file_exc):
                    wibstime.append(time)
                    sizes.append(count)
                    exs.append(ex)
                    
            self.wibstime = wibstime
            self.data = {"size" : sizes,
                         "excited" : exs}
            
        self.data_misc = {"size" : ["Parcticle Size","$\mu$m"],
                          "excited" : ["Excited_Flag","True/False"],
                          "ex_size" : ["Particle Size (Excited Particles only)","$\mu$m"]}
        self.data["ex_size"] = [s if x else np.NaN for s,x in zip(self.data["size"],self.data["excited"])]
            
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
            
    
    def quickplot(self,y):
        
        #error handling
        try: 
            ylabel = self.misc[y][0] + " in " + self.misc[y][1]
        except KeyError:
            raise IllegalValue("y","quickplot",self.processed_data)
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
            raise IllegalValue("y","quickheatmap",self.processed_data)
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
        xx,yy = np.meshgrid(heatmap_t,self.bin_borders)
        
        heatmap_data = deepcopy(self.processed_data[y])
        heatmap_data = self.hk_replacezeros(heatmap_data)
        heatmap_data = np.ma.masked_where(np.isnan(heatmap_data),heatmap_data)
        heatmap_data = np.transpose(heatmap_data)
            
        #draw plot
        fig,ax = plt.subplots()
        
        im = ax.pcolormesh(xx,yy,heatmap_data,cmap="RdYlBu_r",norm=LogNorm())
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_yscale("log")
        ax.set_ylabel("optical diamter in $\mu$m")
        ax.set_xlabel("CET")
        plt.colorbar(im,ax=ax,label=ylabel)
        
        plt.show()
        
        
    #housekeeping funcs
    
    def hk_binsorter(self,size):
        
        op = self.bins - 1
        
        for i in range(self.bins):
            if self.bin_borders[i] <= size and self.bin_borders[i+1] > size:
                op = i
                
        return op
    
    def hk_dndlogdp(self,array):
        
        for i in range(len(array)):
            array[i] = array[i] / (math.log10(self.bin_borders[i+1])-math.log10(self.bin_borders[i]))
            
        return array
    
    def hk_replacezeros(self,array):
        
        smallest = 10000
        for row in array:
            for element in row:
                if element < smallest and element > 0:
                    smallest = element
        for i in range(len(array)):
            for j in range(len(array[i])):
                if array[i][j] == 0:
                    array[i][j] += smallest
                    
        return array