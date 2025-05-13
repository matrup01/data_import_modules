# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 15:52:29 2025

@author: mrupp
"""

import numpy as np
import matplotlib.dates as md
import datetime as dt
import csv
import matplotlib.pyplot as plt
import math
from ErrorHandler import IllegalArgument


class CCS811:
    
    """full documentation see https://github.com/matrup01/data_import_modules \n
    
    file (str) ... takes a ccs811-produced csv-file\n
	
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp\n
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp\n
	title (str, optional) ... takes a str and uses it as a title for quickplots\n
	deviate (bool, optional) ... takes a bool to decide if the data should be expressed relative to mean, default-False\n"""
    
    def __init__(self,file,start="none",end="none",title="no title",deviate=False):
        
        #init
        self.title = title
        self.deviated = False
        
        #read data from csv to list
        data = csv.reader(open(file),delimiter=",")
        data = list(data)
        
        #extract x and y values from list
        self.t = [dt.datetime.strptime(data[i][1],"%H:%M:%S") for i in range(1,len(data))]
        
        self.finder = {"tvoc" : 0,
                       "co2": 1}
        
        self.y = [[[float(data[i][2]) for i in range(1,len(data))],"TVOC","ppb"],
                  [[float(data[i][3]) for i in range(1,len(data))],r"$CO_2$","ppm"]]
        
        #crop
        if start != "none":
            indices = []
            for i in range(len(self.t)):
                if dt.datetime.strptime(start,"%H:%M:%S") <= self.t[i]:
                    indices.append(i)
            start_i = indices[0]
        else: start_i = 0
        
        if end != "none":
            indices = []
            for i in range(len(self.t)):
                if dt.datetime.strptime(end,"%H:%M:%S") <= self.t[i]:
                    indices.append(i)
            end_i = indices[0]
        else: end_i = len(self.t)-1
        
        self.t = [self.t[i] for i in range(start_i,end_i)]
        for i in range(len(self.y)):
            self.y[i][0] = [self.y[i][0][j] for j in range(start_i,end_i)]
            
        #express data as relative from mean
        if deviate:
            self.deviatefrommean()
            
            
    def findplot(self,y):
        
        try:
            loc = self.finder[y]
            yy = self.y[loc]
            
            if self.deviated:
                yy[2] = "%  deviation from mean"
        except:
            raise ValueError("Invalid plottype: plot has to be one of the following strings: pm1,pm25,pm4,pm10,temp,hum")
            
        return yy
    
    
    def quickplot(self):
        
        fig,ax = plt.subplots()
        plt.title(self.title)
        yy = self.findplot("tvoc")

        ax.plot(self.t,yy[0])
        ax.set_ylabel(yy[1] + " in " + yy[2])
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        plt.show()
        
        
    def plot(self,ax,y,color="tab:brown",secondary=False):
        
        #get plotdata
        yy = self.findplot(y)
        
        #draw plot
        ax.plot(self.t,yy[0],color=color)
        ax.set_ylabel(yy[1] + " in " + yy[2])
        ax.axes.yaxis.label.set_color(color)
        ax.tick_params(axis='y', colors=color)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        if not secondary:
            ax.spines["left"].set_color(color)
        else:
            ax.spines["right"].set_color(color)
            ax.spines["left"].set_alpha(0)
            
            
    def returndata(self,y):
        
        yy = self.findplot(y)[0]
        
        return yy
    
    
    def average(self):
        
        meant,meany = [],[]
        
        for i in range(len(self.y)):
            meany.append([])
        
        for_checker = True
        
        for i in range(len(self.t)):
            
            if for_checker:
                now = self.t[i].minute
                minute_vals = []
                
            for_checker = False
            
            minute_vals.append(i)
            
            if self.t[i].minute != now:
                
                meant.append(self.t[minute_vals[math.ceil(len(minute_vals)/2)]])
                for j in range(len(self.y)):
                    meany[j].append(np.mean([self.y[j][0][k] for k in minute_vals]))
                    
                for_checker = True
                
        self.t = meant
        for i in range(len(self.y)):
            self.y[i][0] = meany[i]
            
    
    def deviatefrommean(self):
        
        for element in self.y:
            
            mean = np.mean(element[0])
            
            for i in range(len(element[0])):
                element[0][i] = ((element[0][i] / mean) - 1)*100
                
        self.deviated = True
        
        
class SEN55:
    
    """full documentation see https://github.com/matrup01/data_import_modules \n
    
    file (str) ... takes a sen55-produced csv-file\n
	
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp\n
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp\n
	title (str, optional) ... takes a str and uses it as a title for quickplots\n
	deviate (bool, optional) ... takes a bool to decide if the data should be expressed relative to mean, default-False"""
    
    def __init__(self,file,start="none",end="none",title="no title",deviate=False):
        
        #init
        self.title = title
        self.deviated = False
        
        #read data from csv to list
        data = csv.reader(open(file),delimiter=",")
        data = list(data)
        
        
        #extract x and y values from list
        self.t = [dt.datetime.strptime(data[i][1],"%H:%M:%S") for i in range(1,len(data)-2)]
        
        self.finder = {
            "pm1" : 0,
            "pm25" : 1,
            "pm4" : 2,
            "pm10" : 3,
            "temp" : 4,
            "hum" : 5}
        
        self.y = [[[float(data[i][6]) for i in range(1,len(data)-2)],"PM1",r'$\mu$g/$m^3$'],
             [[float(data[i][7]) for i in range(1,len(data)-2)],"PM2,5","$\mu$g/$m^3$"],
             [[float(data[i][8]) for i in range(1,len(data)-2)],"PM4","$\mu$g/$m^3$"],
             [[float(data[i][9]) for i in range(1,len(data)-2)],"PM10","$\mu$g/$m^3$"],
             [[float(data[i][2]) for i in range(1,len(data)-2)],"temperature","°C"],
             [[float(data[i][3]) for i in range(1,len(data)-2)],"humidity","%"]]
        
        
        #crop
        if start != "none":
            indices = []
            for i in range(len(self.t)):
                if dt.datetime.strptime(start,"%H:%M:%S") <= self.t[i]:
                    indices.append(i)
            start_i = indices[0]
        else: start_i = 0
        
        if end != "none":
            indices = []
            for i in range(len(self.t)):
                if dt.datetime.strptime(end,"%H:%M:%S") <= self.t[i]:
                    indices.append(i)
            end_i = indices[0]
        else: end_i = len(self.t)-1
        
        self.t = [self.t[i] for i in range(start_i,end_i)]
        for i in range(len(self.y)):
            self.y[i][0] = [self.y[i][0][j] for j in range(start_i,end_i)]
            
            
        #express data as relative from mean
        if deviate:
            self.deviatefrommean()
            
    def findplot(self,y):
        
        try:
            loc = self.finder[y]
            yy = self.y[loc]
            
            if self.deviated:
                yy[2] = "%  deviation from mean"
        except:
            raise ValueError("Invalid plottype: plot has to be one of the following strings: pm1,pm25,pm4,pm10,temp,hum")
            
        return yy
            
    
    def quickplot(self):
        
        fig,ax = plt.subplots()
        plt.title(self.title)

        ax.plot(self.t,self.y[1][0])
        ax.set_ylabel(self.y[1][1] + " in " + self.y[1][2])
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        plt.show()
        
        
    def plot(self,ax,y,color="tab:red",secondary=False):
        
        #get plotdata
        yy = self.findplot(y)
        
        #draw plot
        ax.plot(self.t,yy[0],color=color)
        ax.set_ylabel(yy[1] + " in " + yy[2])
        ax.axes.yaxis.label.set_color(color)
        ax.tick_params(axis='y', colors=color)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        if not secondary:
            ax.spines["left"].set_color(color)
        else:
            ax.spines["right"].set_color(color)
            ax.spines["left"].set_alpha(0)
            
            
    def returndata(self,y):
        
        yy = self.findplot(y)[0]
        
        return yy
    
    
    def average(self):
        
        meant,meany = [],[]
        
        for i in range(len(self.y)):
            meany.append([])
        
        for_checker = True
        
        for i in range(len(self.t)):
            
            if for_checker:
                now = self.t[i].minute
                minute_vals = []
                
            for_checker = False
            
            minute_vals.append(i)
            
            if self.t[i].minute != now:
                
                meant.append(self.t[minute_vals[math.ceil(len(minute_vals)/2)]])
                for j in range(len(self.y)):
                    meany[j].append(np.mean([self.y[j][0][k] for k in minute_vals]))
                    
                for_checker = True
                
        self.t = meant
        for i in range(len(self.y)):
            self.y[i][0] = meany[i]
            
                
    def deviatefrommean(self):
        
        for element in self.y:
            
            mean = np.mean(element[0])
            
            for i in range(len(element[0])):
                element[0][i] = ((element[0][i] / mean) - 1)*100
                
        self.deviated = True
    

class FlyingFlo_USB:
    
    """full documentation see https://github.com/matrup01/data_import_modules \n\n
    
    file (str) ... takes a FlyingFlo_USB-produced csv-file\n\n
	
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp\n
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp\n
	title (str, optional) ... takes a str and uses it as a title for quickplots\n
	deviate (bool, optional) ... takes a bool to decide if the data should be expressed relative to mean, default-False\n\n
    
    FlyingFlo_USB.title (str) ... Title used for quickplots\n
    FlyingFlo_USB.deviated (bool) ... Stores if the data is expressed relative to mean\n
    FlyingFlo_USB.t (np.array of dt.datetime) ... Time array\n
    FlyingFlo_USB.y (dict of str : [np.array,str,str]) ... Dictionary with Datatypes as keys storing lists in the form of [data-array, full data name, unit]"""
    
    def __init__(self,file,start="none",end="none",title="no title",deviate=False):
        """
        inits FlyingFlo_USB object

        Parameters
        ----------
        file : str
            takes a FlyingFlo_USB-produced csv-file.
        start : str, optional
            takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp. The default is "none".
        end : str, optional
            takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp. The default is "none".
        title : str, optional
            takes a str and uses it as a title for quickplots. The default is "no title".
        deviate : bool, optional
            takes a bool to decide if the data should be expressed relative to mean. The default is False.

        Returns
        -------
        None.

        """
        
        #init
        self.title = title
        self.deviated = False
        self.averaged = False
        
        
        #read data from csv to list
        data = csv.reader(open(file),delimiter=",")
        data = list(data)
        
        
        #extract x and y values from list
        self.t = np.array([dt.datetime.strptime(data[i][1],"%H:%M:%S.%f") for i in range(1,len(data)-2)])
        
        self.y = {
            "pm1" : [np.array([float(data[i][8]) for i in range(1,len(data)-2)]),"PM1",r'$\mu$g/$m^3$'],
            "pm25" : [np.array([float(data[i][9]) for i in range(1,len(data)-2)]),"PM2.5","$\mu$g/$m^3$"],
            "pm4" : [np.array([float(data[i][10]) for i in range(1,len(data)-2)]),"PM4","$\mu$g/$m^3$"],
            "pm10" : [np.array([float(data[i][11]) for i in range(1,len(data)-2)]),"PM10","$\mu$g/$m^3$"],
            "temp_bme" : [np.array([float(data[i][4]) for i in range(1,len(data)-2)]),"temperature","°C"],
            "hum_bme" : [np.array([float(data[i][6]) for i in range(1,len(data)-2)]),"humidity","%"],
            "gas" : [np.array([float(data[i][5]) for i in range(1,len(data)-2)]),"gas resistance","$\Ohm$"],
            "co2" : [np.array([float(data[i][2]) for i in range(1,len(data)-2)]),r"$CO_2$","ppm"],
            "tvoc" : [np.array([float(data[i][3]) for i in range(1,len(data)-2)]),"TVOC","ppb"],
            "press" : [np.array([float(data[i][7]) for i in range(1,len(data)-2)]),"$ambient pressure","hPa"],
            "hum_sen" : [np.array([float(data[i][12]) for i in range(1,len(data)-2)]),"humidity","%"],
            "temp_sen" : [np.array([float(data[i][13]) for i in range(1,len(data)-2)]),"temperature","°C"],
            "voc_sen" : [np.array([float(data[i][14]) for i in range(1,len(data)-2)]),"VOC-Index","a.u"],
            "nox" : [np.array([float(data[i][15]) for i in range(1,len(data)-2)]),r"$NO_X$-Index","a.u."]
            }
        
        
        #crop
        if start != "none":
            indices = []
            for i in range(len(self.t)):
                if dt.datetime.strptime(start,"%H:%M:%S") <= self.t[i]:
                    indices.append(i)
            start_i = indices[0]
        else: start_i = 0
        
        if end != "none":
            indices = []
            for i in range(len(self.t)):
                if dt.datetime.strptime(end,"%H:%M:%S") <= self.t[i]:
                    indices.append(i)
            end_i = indices[0]
        else: end_i = len(self.t)-1
        
        self.t = [self.t[i] for i in range(start_i,end_i)]
        for key in self.y:
            self.y[key][0] = [self.y[key][0][j] for j in range(start_i,end_i)]
            
            
        #express data as relative from mean
        if deviate:
            self.deviatefrommean()
            
            
    def quickplot(self,y):
        """
        draws a plot y vs time

        Parameters
        ----------
        y : str
            Type of data that should be plotted (eg TVOC).

        Raises
        ------
        ValueError
            Illegal y has been given.

        Returns
        -------
        None.

        """
        
        try:
            yy = self.y[y]
        except:
            raise ValueError(f"{y} cant be plotted! Plottable data: {', '.join([key for key in self.y])}")
        
        fig,ax = plt.subplots()
        plt.title(self.title)

        ax.plot(self.t,yy[0])
        if self.deviated:
            ax.set_ylabel(yy[1] + " in % deviation from mean")
        else:
            ax.set_ylabel(yy[1] + " in " + yy[2])
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        plt.show()
        
        
    def plot(self,ax,y,**kwargs):
        """
        draws a plot y vs time on an existing matplotlib-axis

        Parameters
        ----------
        ax : mpl-axis
            takes a matplotlib-axis, on which the graph will be drawn.
        y : str
            Type of data that should be plotted (eg TVOC).
        color : str, optional
            changes the color of the plot. The default is "tab:brown".
        secondary : bool, optional
            determines which y-axis should be colored (False-left axis/True-right axis). The default is False.

        Raises
        ------
        ValueError
            Illegal y has been given.

        Returns
        -------
        None.

        """
        #kwargs
        defaults = {"color" : "tab:brown",
                    "secondary" : False
            }
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "FlyingFlo_USB.plot()")
        
        #get plotdata
        try:
            yy = self.y[y]
        except:
            raise ValueError(f"{y} cant be plotted! Plottable data: {', '.join([key for key in self.y])}")
        
        #draw plot
        ax.plot(self.t,yy[0],color=kwargs["color"])
        if self.deviated:
            ax.set_ylabel(yy[1] + " in % deviation from mean")
        else:
            ax.set_ylabel(yy[1] + " in " + yy[2])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
            
    def average(self):
        """
        averages all the data minutewise

        Returns
        -------
        None.

        """
        
        minutes = np.array([timestamp.minute for timestamp in self.t])
        hours = np.array([timestamp.hour for timestamp in self.t])
        
        for key,val in self.y.items():
            new_array = []
            minute = None
            for m,h in zip(minutes,hours):
                if minute == None:
                    minute = m
                    checker = [mm==minute and hh==h for mm,hh in zip(minutes,hours)]
                    appender = np.where(checker,self.y[key][0],minutes*np.NaN)
                    appender = appender[~np.isnan(appender)]
                    new_array.append(np.mean(appender))
                elif minute != m:
                    minute = None
            self.y[key][0] = np.array(new_array.copy())
            
        new_array = []
        minute = None
        for timestamp in self.t:
            if minute == None:
                minute = timestamp.minute
                new_array.append(timestamp.replace(second=0))
            elif minute != timestamp.minute:
                minute = None
        self.t = np.array(new_array)
        self.averaged = True
            
    def deviatefrommean(self):
        """
        changes all values to be expressed relative to the mean

        Returns
        -------
        None.

        """
        
        for key,element in self.y.items():
            
            mean_array = np.array(self.y[key][0].copy())
            mean_array = mean_array[~np.isnan(mean_array)]
            mean = np.mean(mean_array)
            
            for i in range(len(element[0])):
                element[0][i] = ((element[0][i] / mean) - 1)*100
                
            self.y[key][0] = element[0]
                
        self.deviated = True
        
    def returndata(self):
        
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
        op_details = {}
        for key,val in self.y.items():
            y_op = np.array([val[0][i] if not np.isnan(i) else np.nan for i in mask])
            op[key] = y_op
            op_details[key] = [val[1],val[2]]
            
        return op,op_details
        
        
        
    #Housekeeping funcs
    
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