import csv
import datetime as dt
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.colors import LogNorm
from copy import copy
from .ErrorHandler import IllegalArgument,SensorNotMounted,UnknownLayoutError

class Pops:
    
    """full documentation see https://github.com/matrup01/data_import_modules"""
    
    def __init__(self,file,**kwargs):

        #init vars
        self.filename = file
        self.relative = False
        self.deviated = False
        self.d_categories = [element * 1000 for element in [0.115,0.125,0.135,0.150,0.165,0.185,0.210,0.250,0.350,0.475,0.575,0.855,1.220,1.53,1.99,2.585,3.37]]
        self.plottypes = [["temp_bm680","temperature (bm680)","°C"],["hum_bm680","rel. humidity (bm680)","%"],["temp_sen55","temperature","°C"],["hum_sen55","rel. humidity","%"],["press","ambient pressure","hPa"],["gas","Gaswiderstand",r"$\Ohm$"],["pm1","PM1.0",r"$\mu$g/$m^3$"],["pm25","PM2.5",r"$\mu$g/$m^3$"],["pm4","PM4.0",r"$\mu$g/$m^3$"],["pm10","PM10.0",r"$\mu$g/$m^3$"],["voc","VOC-Index",""],["nox",r"$NO_X$-Index",""],["co2",r"$CO_2$","ppm"],["tvoc","TVOC","ppb"]]
        self.plottypes2 = [["total","part. conc." , r"Counts/$cm^3$"],["popstemp","temperature inside POPS-box","°C"],["boardtemp","boardtemp","°C"],["pm25","PM2.5 from POPS",r"Counts/$cm^3$"],["underpm25","particles smaller than 350 nm",r"Counts/$cm^3$"]]
        
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
                                   "ydata2" : [6,21,12],
                                   "popstime" : 3,
                                   "t" : 1,
                                   "flow" : 16}
                case _:
                    raise UnknownLayoutError(self.layout, ["desktopmode","box_pallnsdorfer","FlyingFlo2.0"], "POPS")
        
        
        #reads data from csv to list
        data = csv.reader(open(file),delimiter=",")
        data = list(data)
        newdata = []
        for dat in data:
            if dat[0] != "Raspi-Date":
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
            for element in [data[i][1] for i in range(1,len(data))]:
                tcounter += 1
                if self.start == element:
                  t_start = tcounter
            popscounter = -1
            unixstart = str(int(self.start[0:2])*3600+int(self.start[3:5])*60+int(self.start[6:8])-7200 + self.timecorr)
            for element in [data[i][23][0:5] for i in range(1,len(data))]:
                popscounter += 1
                if unixstart == element:
                    pops_start = popscounter
        else:
            t_start = 0
            pops_start = 0
            
        if self.end != "none":
            tcounter = -1
            for element in [data[i][1] for i in range(1,len(data))]:
                tcounter += 1
                if self.end == element:
                  t_end = tcounter
            popscounter = -1
            unixend = str(int(self.end[0:2])*3600+int(self.end[3:5])*60+int(self.end[6:8])-7200 + self.timecorr)
            for element in [data[i][23][0:5] for i in range(1,len(data))]:
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
        
        bins = np.array(self.pops_bins)
        bg = np.array([np.mean(element) for element in bins])
        totalbg = np.mean(np.array(self.ydata2[0]))
        return [bg,totalbg]
    
    
    def importbg(self,bg):
        
        for i in range(len(self.pops_bins)):
            self.pops_bins[i] = [self.pops_bins[i][j]-bg[0][i] for j in range(len(self.pops_bins[i]))]
        self.ydata2[0] = [self.ydata2[0][i] - bg[1] for i in range(len(self.ydata2[0]))]
        
        
    def quickplot(self,y,**kwargs):
        
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
        
        #kwargs
        defaults = {"orientation" : "horizontal",
                    "location" : "top",
                    "pad" : 0}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "Pops.newheatmap()")
        
        heatmapdata = [[self.pops_bins[j][i] / (math.log10(self.d_categories[j+1])-math.log10(self.d_categories[j])) for i in range(len(self.pops_bins[0])-1)] for j in range(len(self.pops_bins))]
        heatmapdata = self.hk_replacezeros(heatmapdata)
        
        xlims = [self.popstime[0],self.popstime[-1]]
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
        
        #calculate needed values
        means = np.array([np.mean(self.pops_bins[i]) for i in range(len(self.pops_bins))])
        cparticles = np.sum(means)
        print(self.title + ": " + str(cparticles) + " counts/cm3 (cumulative)")
        
        return cparticles
        
    
    def crop(self,startcrop,endcrop):
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
        
        placeholder1,data,label,unit = self.hk_findplottype(y)
        mean = np.mean(data)
        std = np.std(data,ddof=1)
        var = np.var(data,ddof=1)
        print(label + " in " + unit + " (mean,std,var): " + str(mean) + ", " + str(std) + ", " + str(var))
    
        
    def returnstats(self,y):
        
        placeholder1,data,label,unit = self.hk_findplottype(y)
        mean = np.mean(data)
        std = np.std(data,ddof=1)
        var = np.var(data,ddof=1)
        
        return mean,std,var
    
    
    def append(self,obj):
        
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
            