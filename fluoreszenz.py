import csv
import datetime as dt
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.colors import LogNorm
from ErrorHandler import IllegalArgument

class FData:
    
    """full documentation see https://github.com/matrup01/data_import_modules \n \n
    
    file (str) ... takes an FSpec-produced csv-file\n\n

	title (str, optional) ... takes a str and uses it as a title for quickplots\n
	encoding_artifacts (bool, optional) ... takes a boolean to determine if there are encoding artifacts that need to be removed, default-True\n
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp\n
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp\n
	skiprows (int, optional) ... takes an int and skips the first rows (may be used if the first rows are corrupted), default-0"""
    
    def __init__(self,file,title="kein Titel",encoding_artifacts=True,start="none",end="none",skiprows=0):
        
        #reads data from csv to list
        self.title = title
        self.file = file
        data = csv.reader(open(file,encoding="ansi"),delimiter=";")
        data = list(data)
        
        #get rid of encoding-artifacts
        if encoding_artifacts:
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = data[i][j].replace('\x00','')
                    #if j == 2 and i > 0:
                        #data[i][j] = data[i][j][126:130]
        
        #extract x and y values from list
        self.t = [dt.datetime.strptime(data[i][1],"%H:%M:%S.%f") for i in range(1+skiprows,len(data))]
        self.channels = [[int(data[i][j])-1000 for i in range(1+skiprows,len(data))] for j in range(3,19)]
        
        #crop
        t_start = 0
        t_end = len(self.t)
        if start != "none":
            tcounter = -1
            for element in self.t:
                tcounter += 1
                if str(element)[11:19] == start:
                  t_start = tcounter
            
        if end != "none":
            tcounter = -1
            for element in self.t:
                tcounter += 1
                if str(element)[11:19] == end:
                  t_end = tcounter

        self.crop(t_start,len(self.t)-t_end)
        
        
    def internalbg(self,startmeasurementtime,bgcrop=0):
        
        #find point in list where measurement starts
        for i in range(len(self.t)):
            if str(self.t[i])[11:19].rsplit(".")[0] == startmeasurementtime:
                startmeasurement = i
        
        #correct bg
        length = len(self.t)
        for i in range(len(self.channels)):
            correctorarray = np.array([self.channels[i][j] for j in range(bgcrop,startmeasurement)])
            corrector = np.mean(correctorarray)
            self.channels[i] = np.array([self.channels[i][j]-corrector for j in range(startmeasurement,length)])
        self.t = [self.t[i] for i in range(startmeasurement,length)]
            
        
    def externalbg(self,bgfile,startcrop=0,endcrop=0):
        
        #reads data from csv to list
        data = csv.reader(open(bgfile),delimiter=";")
        data = list(data)
            
        #get rid of encoding-artifacts
        for i in range(len(data)):
            for j in range(len(data[i])):
                if j == 2 and i > 0:
                    data[i][j] = data[i][j][126:130]
        
        #extract data from list
        bgdata = np.array([[int(data[i][j])-1000 for i in range(1+startcrop,len(data)-endcrop)] for j in range(2,18)])
        bg = np.array([np.mean(element) for element in bgdata])
        
        #correct bg
        for i in range(len(self.channels)):
            self.channels[i] = [self.channels[i][j]-bg for j in range(len(self.channels[i]))]
            
            
    def quickplot(self,channelno,startcrop=0,endcrop=0):
        
        channelname = "ch" + str(channelno)
        channelno -= 1
        
        #crop data
        self.crop(startcrop,endcrop)
        
        #draw plot        
        fig,ax = plt.subplots()
        plt.title(self.title)
        ax.plot(self.t,self.channels[channelno],label=channelname)
        ax.set_ylabel("Intensität")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        plt.legend()
        plt.show()
        
        
    def plot(self,channelno,ax,quakes=[],quakeslabel="kein Label",quakecolor="tab:purple",color="tab:green",startcrop=0,endcrop=0):
        
        channelname = "ch" + str(channelno)
        channelno -= 1
        
        #crop data
        self.crop(startcrop,endcrop)
        
        #draw plot
        ax.plot(self.t,self.channels[channelno],label=channelname,color=color)
        ax.set_ylabel("Intensität in " + channelname)
        if len(quakes) != 0:
            ax.vlines(x=[dt.datetime.strptime(element, "%H:%M:%S")for element in quakes],ymin=min(self.channels[channelno]),ymax=max(self.channels[channelno]),color=quakecolor,ls="dashed",label=quakeslabel)
            
            
    def crop(self,startcrop,endcrop):
        length = len(self.t)
        self.t = [self.t[i] for i in range(startcrop,length-endcrop)]
        for i in range(len(self.channels)):
            self.channels[i] = [self.channels[i][j] for j in range(startcrop,length-endcrop)]
            
            
    def quickheatmap(self):
        
        xx,yy = np.meshgrid(self.t,[i+0.5 for i in range(len(self.channels))])
        heatmap_data = deepcopy(self.channels)
        heatmap_data = self.hk_replacezeros(heatmap_data)
        
        fig,ax = plt.subplots()
        
        im = ax.pcolormesh(xx,yy,heatmap_data,cmap="RdYlBu_r",norm=LogNorm(),shading="nearest")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("Channels")
        ax.set_xlabel("CET")
        
        ticks = [i+0.5 for i in range(len(self.channels))]
        ticklabels = [i+1 for i in range(len(ticks))]
        ax.set_yticks(ticks,labels=ticklabels)
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        
        plt.colorbar(im,ax=ax,label="Fluorescence Intensity")
        
        plt.show()
            
        
    def heatmap(self,ax,**kwargs):
        
        #import kwargs
        smooth = kwargs["smooth"] if "smooth" in kwargs else True
        cmap = kwargs["cmap"] if "cmap" in kwargs else "RdYlBu_r"
        pad = kwargs["pad"] if "pad" in kwargs else 0.01
        togglecbar = kwargs["togglecbar"] if "togglecbar" in kwargs else True
        xlims = kwargs["xlims"] if "xlims" in kwargs else "none"
        
        #error handling
        for key in kwargs.keys():
            if key not in ["smooth","cmap","pad","togglecbar","xlims"]:
                raise IllegalArgument(key,"FData.heatmap()")
        
        #prepare data
        xx,yy = np.meshgrid(self.t,[i+0.5 for i in range(len(self.channels))])
        heatmap_data = deepcopy(self.channels)
        heatmap_data = self.hk_replacezeros(heatmap_data)
        if type(xlims) == list:
            ax.set_xlim([dt.datetime.strptime(element, "%H:%M:%S") for element in xlims])
        
        #draw
        if smooth:
            im = ax.pcolormesh(xx,yy,heatmap_data,cmap=cmap,norm=LogNorm(),shading="gouraud")
        else:
            im = ax.pcolormesh(xx,yy,heatmap_data,cmap=cmap,norm=LogNorm(),shading="nearest")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("Channels")
        ax.set_xlabel("CET")
        
        ticks = [i+0.5 for i in range(len(self.channels))]
        ticklabels = [i+1 for i in range(len(ticks))]
        ax.set_yticks(ticks,labels=ticklabels)
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        if togglecbar:
            plt.colorbar(im,ax=ax,label="Fluorescence Intensity",pad=pad)
        
        
        
    #housekeeping funcs
    def hk_replacezeros(self,arr):
        
        array = deepcopy(arr)
        
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
            
            
            

