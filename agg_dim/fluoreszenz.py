import csv
import datetime as dt
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.colors import LogNorm
from .ErrorHandler import IllegalArgument, IllegalFileFormat
import pickle
from numba import njit, prange, float64


#jit-compiled housekeeping funcs



class FData:
    
    """full documentation see https://github.com/matrup01/data_import_modules"""
    
    def __init__(self,file,title="kein Titel",encoding_artifacts=True,start="none",end="none",skiprows=0,layout=[3,18]):
        
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
        self.channels = [[data[i][j] for i in range(1+skiprows,len(data))] for j in range(layout[0],layout[1]+1)]
        for i in range(len(self.channels)):
            for j in range(len(self.channels[i])):
                try:
                    self.channels[i][j] = int(self.channels[i][j]) - 1000
                except ValueError:
                    self.channels[i][j] = 0
        
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
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
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
            
            
            
class NewFData:
    
    def __init__(self,file,bg_file="blank.blank",**kwargs):
        
        #check if data is loaded from .csv or .fspec
        filetype = file.split(".")[-1]
        if filetype == "csv":
        
            #kwargs
            defaults = {"sigma" : 1,
                        "measurement_frequency" : 100,
                        "start" : "none",
                        "end" : "none",
                        "jit" : True,
                        "debugging" : False,
                        "bg_start" : "*",
                        "bg_end" : "*",
                        "layout" : [3,18]}
            for key,value in zip(defaults.keys(),defaults.values()):
                self.hk_kwargs(kwargs, key, value)
            self.hk_errorhandling(kwargs, defaults.keys(), "NewFData")
            
            #error handling
            for key in kwargs:
                if key not in ["sigma","measurement_frequency","start","end","debugging","jit","bg_start","bg_end"]:
                    raise IllegalArgument(key,"NewFData")
            
            #import background-data
            bg_filetype = bg_file.split(".")[-1]
            if bg_filetype == "csv":
                bgdata_all = list(csv.reader(open(bg_file,encoding="ansi"),delimiter=";"))
                bgdata_time = [bgdata_all[i][1] for i in range(len(bgdata_all))]
                bgdata = bgdata_all[1:]
                bg_start_index = 100
                bg_end_index = len(bgdata)
                if self.bg_start != "*" or self.bg_end != "*":
                   
                    for i in range(len(bgdata_time)):
                        match bgdata_time[i][:8]:
                            case self.bg_start:
                                bg_start_index = i
                            case self.bg_end:
                                bg_end_index = i
                            case _:
                                pass
                bgdata = bgdata[bg_start_index:bg_end_index]
                for i in range(len(bgdata)):
                    if len(bgdata[i]) != 19:
                        if len(bgdata[i]) < 19:
                            for j in range(19-len(bgdata[i])):
                                bgdata[i].append(0)
                        elif len(bgdata[i]) > 19:
                            j = len(bgdata[i]) - 19
                            bgdata[i] = bgdata[i][:-j]
                bgdata = np.array(bgdata).transpose()
                bgdata = bgdata[3:].astype("int")
                self.bg = np.array([np.mean(channel)+np.std(channel)*self.sigma for channel in bgdata])
                self.bg = self.bg - 1000
            elif bg_filetype == "fspec":
                bg_ip = pickle.load(open(bg_file,"rb"))
                self.bg = np.array([mean+std*self.sigma for mean,std in zip(bg_ip["bg_means"],bg_ip["bg_stds"])])
            else:
                raise IllegalFileFormat(bg_filetype, "csv or .fspec", "bg_file")
            
            #import raw data
            data = list(csv.reader(open(file,encoding="ansi"),delimiter=";",))[1:]
            for i in range(len(data)):
                if len(data[i]) != 19:
                    if len(data[i]) < 19:
                        for j in range(19-len(data[i])):
                            data[i].append(0)
                    elif len(data[i]) > 19:
                        j = len(data[i]) - 19
                        data[i] = data[i][:-j]
            data = np.array(data).transpose()
            self.rawtime = np.array([dt.datetime.strptime(time,"%H:%M:%S.%f").replace(microsecond=0) for time in data[1]])
            self.rawchannels = data[self.layout[0]:self.layout[1]]
            for i in range(len(self.rawchannels)):
                for j in range(len(self.rawchannels[i])):
                    try:
                        self.rawchannels[i][j] = int(self.rawchannels[i][j])
                    except ValueError:
                        self.rawchannels[i][j] = 1000
            self.rawchannels = np.array(self.rawchannels,int)
            self.rawchannels = self.rawchannels - 1000
            
            #crop
            t_start = 0
            t_end = len(self.rawtime)
            if self.start != "none":
                tcounter = -1
                for element in self.rawtime:
                    tcounter += 1
                    if str(element)[11:19] == self.start:
                        t_start = tcounter
                
            if self.end != "none":
                tcounter = -1
                for element in self.rawtime:
                    tcounter += 1
                    if str(element)[11:19] == self.end:
                        t_end = tcounter
            
            self.rawtime = self.rawtime[t_start:t_end]
            self.rawchannels = [channel[t_start:t_end] for channel in self.rawchannels]
            
            #process data
            secs = []
            for t in self.rawtime:
                if t not in secs:
                    secs.append(t)
            self.t = np.array(secs)
            
            if self.jit:
                numba_t = np.array([(i - dt.datetime(1970, 1, 1)).total_seconds() for i in self.t],float)
                numba_rt = np.array([(i - dt.datetime(1970, 1, 1)).total_seconds() for i in self.rawtime],float)
                numba_rc = np.array(self.rawchannels,float)
                numba_bg = np.array(self.bg,float)
                numba_ch = np.array([[float(0) for j in range(len(numba_t))] for i in range(len(numba_rc))])
                self.channels = self.hk_process_data(numba_t,numba_rc,numba_bg,numba_rt,numba_ch)
                self.channels /= self.measurement_frequency
            else:
                self.channels = np.array([[0 for j in range(len(self.t))] for i in range(len(self.rawchannels))],float)
                for t in range(len(self.t)):
                    for channel in range(len(self.rawchannels)):
                        
                        counter = 0
                        for val in range(len(self.rawchannels[channel])):
                            if self.rawchannels[channel][val] > self.bg[channel] and self.rawtime[val] == self.t[t]:
                                counter += 1
                        self.channels[channel][t] = counter / self.measurement_frequency
                    
        elif filetype == "fspec":
                
            ip = pickle.load(open(file,"rb"))
            
            self.hk_kwargs(ip,"sigma",1)
            self.hk_kwargs(ip,"measurement_frequency", 100)
            self.hk_kwargs(ip,"bg", "null")
            self.hk_kwargs(ip,"rawtime", "null")
            self.hk_kwargs(ip,"rawchannels", "null")
            self.hk_kwargs(ip,"t", "null")
            self.hk_kwargs(ip,"channels","null")
            
            self.hk_kwargs(kwargs, "start", "none")
            self.hk_kwargs(kwargs, "end", "none")
            
            #crop
            t_start = 0
            t_end = len(self.t)
            if self.start != "none":
                tcounter = -1
                for element in self.t:
                    tcounter += 1
                    if str(element)[11:19] == self.start:
                        t_start = tcounter
                
            if self.end != "none":
                tcounter = -1
                for element in self.t:
                    tcounter += 1
                    if str(element)[11:19] == self.end:
                        t_end = tcounter
            
            self.t = self.t[t_start:t_end]
            self.channels = [channel[t_start:t_end] for channel in self.channels]
            
        else:
            raise IllegalFileFormat(filetype, "csv-file or .fspec", file)
            
                   
    
    def save(self,filename,**kwargs):
        
        #kwargs
        defaults = {"start" : "none",
                    "end" : "none"}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "NewFData.save()")

        
        #crop
        t_start = 0
        t_end = len(self.t)
        if kwargs["start"] != "none":
            tcounter = -1
            for element in self.t:
                tcounter += 1
                if str(element)[11:19] == kwargs["start"]:
                    t_start = tcounter
            
        if kwargs["end"] != "none":
            tcounter = -1
            for element in self.t:
                tcounter += 1
                if str(element)[11:19] == kwargs["end"]:
                    t_end = tcounter
                    
        raw_start = 0
        raw_end = len(self.rawtime)
        if kwargs["start"] != "none":
            tcounter = -1
            for element in self.rawtime:
                tcounter += 1
                if str(element)[11:19] == kwargs["start"]:
                    raw_start = tcounter
            
        if kwargs["end"] != "none":
            tcounter = -1
            for element in self.rawtime:
                tcounter += 1
                if str(element)[11:19] == kwargs["end"]:
                    raw_end = tcounter
        
        save_t = self.t[t_start:t_end]
        save_channels = [channel[t_start:t_end] for channel in self.channels]
        
        #create background params
        bg_means = np.array([np.mean(channel) for channel in self.rawchannels[raw_start:raw_end]])
        bg_stds = np.array([np.std(channel) for channel in self.rawchannels[raw_start:raw_end]])
        
        op = {"sigma" : self.sigma,
              "measurement_frequency" : self.measurement_frequency,
              "bg" : self.bg,
              "rawtime" : self.rawtime,
              "rawchannels" : self.rawchannels,
              "t" : save_t,
              "channels" : save_channels,
              "bg_means" : bg_means,
              "bg_stds" : bg_stds}
        
        if filename[-6:] != ".fspec":
            filename += ".fspec"
        
        pickle.dump(op,open(filename,"wb"),4)
        
        
    def quickplot(self,channelno):
        
        channelname = "ch" + str(channelno)
        channelno -= 1
        
        #draw plot        
        fig,ax = plt.subplots()
        ax.plot(self.t,self.channels[channelno],label=channelname)
        ax.set_xlabel("CET")
        ax.set_ylabel("Fluorescence Index")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        plt.legend()
        plt.show()
        
        
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
        
        plt.colorbar(im,ax=ax,label="Fluorescence Index")
        
        plt.show()
        
        
    def plot(self,channelno,ax,**kwargs):
        
        #import kwargs   
        defaults = {"quakes" : [],
                    "quakeslabel" : "no label",
                    "quakecolor" : "tab:purple",
                    "color" : "tab:green"}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "NewFData.plot()")
        
        
        channelname = "ch" + str(channelno)
        channelno -= 1
        
        #draw plot
        ax.plot(self.t,self.channels[channelno],label=channelname,color=kwargs["color"])
        ax.set_ylabel("fluorescence index (channel " + str(channelno+1) + ")")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        if len(kwargs["quakes"]) != 0:
            ax.vlines(x=[dt.datetime.strptime(element, "%H:%M:%S")for element in kwargs["quakes"]],ymin=min(self.channels[channelno]),ymax=max(self.channels[channelno]),color=kwargs["quakecolor"],ls="dashed",label=kwargs["quakeslabel"])
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        
        
    def meanplot(self,ax,min_ch=1,max_ch=16,**kwargs):
        
        #import kwargs
        defaults = {"min_ch" : 1,
                    "max_ch" : 16,
                    "quakes" : [],
                    "quakeslabel" : "tab:purple",
                    "quakecolor" : "tab:purple",
                    "color" : "tab:green"}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "NewFData.meanplot()")
        
        meanchannel = [0 for i in range(len(self.t))]
        
        min_ch -= 1
        ch_len = len(list(range(min_ch,max_ch)))
        
        for i in range(len(self.t)):
            for ch in range(min_ch,max_ch):
                meanchannel[i] += self.channels[ch][i]
        for i in range(len(meanchannel)):
            meanchannel[i] /= ch_len
                
        #draw plot
        label = "mean of channels " + str(min_ch + 1) + " - " + str(max_ch)
        ax.plot(self.t,meanchannel,label=label,color=kwargs["color"])
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("Fluorescence Index (" + label + ")")
        if len(kwargs["quakes"]) != 0:
            ax.vlines(x=[dt.datetime.strptime(element, "%H:%M:%S")for element in kwargs["quakes"]],ymin=min(meanchannel),ymax=max(meanchannel),color=kwargs["quakecolor"],ls="dashed",label=kwargs["quakeslabel"])
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        
        
    def heatmap(self,ax,**kwargs):
        
        #import kwargs
        defaults = {"smooth" : True,
                   "cmap" : "RdYlBu_r",
                   "pad" : 0.01,
                   "togglecbar" : True,
                   "xlims" : "none"}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "NewFData.heatmap()")
        
        #prepare data
        xx,yy = np.meshgrid(self.t,[i+0.5 for i in range(len(self.channels))])
        heatmap_data = deepcopy(self.channels)
        heatmap_data = self.hk_replacezeros(heatmap_data)
        if type(kwargs["xlims"]) == list:
            ax.set_xlim([dt.datetime.strptime(element, "%H:%M:%S") for element in kwargs["xlims"]])
        
        #draw
        if kwargs["smooth"]:
            im = ax.pcolormesh(xx,yy,heatmap_data,cmap=kwargs["cmap"],norm=LogNorm(),shading="gouraud")
        else:
            im = ax.pcolormesh(xx,yy,heatmap_data,cmap=kwargs["cmap"],norm=LogNorm(),shading="nearest")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("Channels")
        ax.set_xlabel("CET")
        
        ticks = [i+0.5 for i in range(len(self.channels))]
        ticklabels = [i+1 for i in range(len(ticks))]
        ax.set_yticks(ticks,labels=ticklabels)
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        if kwargs["togglecbar"]:
            plt.colorbar(im,ax=ax,label="Fluorescence Index",pad=kwargs["pad"])
        
        
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
    
    
    def hk_errorhandling(self,kwargs,legallist,funcname):
        
        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)
    
    
    @staticmethod
    @njit(float64[:,:](float64[:],float64[:,:],float64[:],float64[:],float64[:,:]))
    def hk_process_data(tt,rc,bg,rt,channels):

        for t in prange(len(tt)):
            for channel in prange(len(rc)):
                for val in prange(len(rc[channel])):
                    if rc[channel][val] > bg[channel] and rt[val] == tt[t]:
                        channels[channel][t] += 1
             
        return channels
        
