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
    

