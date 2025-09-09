# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 15:02:42 2025

@author: mrupp
"""

import csv
import datetime as dt
from .ErrorHandler import IllegalFileFormat, IllegalArgument
import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np

class WeatherData:
    
    def __init__(self,file,**kwargs):
        """
        inits WeatherData object

        Parameters
        ----------
        file : str
            takes a csv-file created by the weatherstation

        Returns
        -------
        None.

        """
        
        if file.split(".")[1].lower() != "csv":
            raise IllegalFileFormat(file.split(".")[1], "csv","WeatherData argument")
        data = csv.reader(open(file),delimiter=",")
        data = list(data)
        
        self.data = {
            "t" : np.array([dt.datetime.strptime(data[i][0],"%Y/%m/%d %H:%M") for i in range(1,len(data))]),
            "indoortemp" : np.array([float(data[i][1]) for i in range(1,len(data))]),
            "indoorhum" : np.array([float(data[i][2]) for i in range(1,len(data))]),
            "outdoortemp" : np.array([float(data[i][3]) for i in range(1,len(data))]),
            "outdoorhum" : np.array([float(data[i][4]) for i in range(1,len(data))]),
            "dewpoint" : np.array([float(data[i][5]) for i in range(1,len(data))]),
            "felttemp" : np.array([float(data[i][6]) for i in range(1,len(data))]),
            "wind" : np.array([float(data[i][7]) for i in range(1,len(data))]),
            "gust" : np.array([float(data[i][8]) for i in range(1,len(data))]),
            "winddir" : np.array([float(data[i][9]) for i in range(1,len(data))]),
            "abspress" : np.array([float(data[i][10]) for i in range(1,len(data))]),
            "relpress" : np.array([float(data[i][11]) for i in range(1,len(data))]),
            "solarrad" : np.array([float(data[i][12]) for i in range(1,len(data))]),
            "uvi" : np.array([float(data[i][13]) for i in range(1,len(data))]),
            "rain" : np.array([float(data[i][14]) for i in range(1,len(data))])
            }
        self.details = {
            "indoortemp" : ["temperature (indoors)","°C"],
            "indoorhum" : ["relative humidity (indoors)", "%"],
            "outdoortemp" : ["temperature (outdoors)","°C"],
            "outdoorhum" : ["relative humidity (outdoors)", "%"],
            "dewpoint" : ["dewpoint","°C"],
            "felttemp" : ["felt temperature","°C"],
            "wind" : ["windspeed","m/s"],
            "gust" : ["windspeed (gust)", "m/s"],
            "winddir" : ["wind direction","°"],
            "abspress" : ["absolute ambient pressure","hPa"],
            "relpress" : ["relative ambient pressure","hPa"],
            "solarrad" : ["solar radiation","W/m${}^2$"],
            "uvi" : ["UV Index", "A.U."],
            "rain" : ["hourly precipitation","mm"]
            }
        
        
    def plot(self,ax,y,**kwargs):
        """
        

        Parameters
        ----------
        ax : mpl-axis
            takes a mpl-axis on which the data will be plotted.
        y : str
            decides which data should be plotted.
        day : str, optional
            takes a day in the format ddmmyyyy. If a day is given only data acquired on that day will be plotted
        setday : str, optional
            takes a day in the format ddmmyyyy. If a setday is given all data will be changed to this day to make it easier to plot against other data
        start : str, optional
            takes a timestamp in the format HHMMSS. if a start is given only data acquired after that timestamp will be plotted
        end : str, optional
            takes a timestamp in the format HHMMSS. if an end is given only data acquired before that timestamp will be plotted
        secondary : bool, optional
            if True the plot will be drawn on the right y-axis. The default is False.
        color : str, optional
            decides the color of the plot. The default is "tab:blue".
        plotlabel : str, optional
            a label that is used for the plot if a legend is drawn. The default is "no label".
        ylabel : str, optional
            a label that is used for the y-axis, if none is given it will be "value in unit", where value and unit are retrieved from the given y
        Returns
        -------
        None.

        """
        
        defaults = {
            "day" : None,
            "setday" : None,
            "start" : None,
            "end" : None,
            "secondary" : False,
            "color" : "tab:blue",
            "plotlabel" : "no label",
            "ylabel" : None
            }
        
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "WeatherData.plot()")
        
        mask = np.full(len(self.data["t"]),True)
        if type(kwargs["day"]) == str:
            day = kwargs["day"]
            day = ".".join([day[:2],day[2:4],day[4:]])
            correctdate = dt.datetime.strptime(day, "%d.%m.%Y").date()
            for i in range(len(self.data["t"])):
                if self.data["t"][i].date() != correctdate:
                    mask[i] = False
        if type(kwargs["start"]) == str:
            starthour,startminute,startsecond = int(kwargs["start"][:2]),int(kwargs["start"][2:4]),int(kwargs["start"][4:])
            for i in range(len(self.data["t"])):
                if self.data["t"][i].hour < starthour:
                    mask[i] = False
                elif self.data["t"][i].hour == starthour and self.data["t"][i].minute < startminute:
                    mask[i] = False
                elif self.data["t"][i].hour == starthour and self.data["t"][i].minute == startminute and self.data["t"][i].second < startsecond:
                    mask[i] = False
        if type(kwargs["end"]) == str:
            endhour,endminute,endsecond = int(kwargs["end"][:2]),int(kwargs["end"][2:4]),int(kwargs["end"][4:])
            for i in range(len(self.data["t"])):
                if self.data["t"][i].hour > endhour:
                    mask[i] = False
                elif self.data["t"][i].hour == endhour and self.data["t"][i].minute > endminute:
                    mask[i] = False
                elif self.data["t"][i].hour == endhour and self.data["t"][i].minute == endminute and self.data["t"][i].second > endsecond:
                    mask[i] = False
                    
        xx = self.data["t"][mask]
        yy = self.data[y][mask]
        
        if type(kwargs["setday"]) == str:
            date = [kwargs["setday"][:2],kwargs["setday"][2:4],kwargs["setday"][4:]]
            xx = np.array([d.replace(day=int(date[0]),month=int(date[1]),year=int(date[2])) for d in xx])
            
        if type(kwargs["ylabel"]) != str:
            kwargs["ylabel"] = f"{self.details[y][0]} in {self.details[y][1]}"
        
        ax.plot(xx,yy,label=kwargs["plotlabel"],color=kwargs["color"])
        ax.set_ylabel(kwargs["ylabel"])
        ax.set_xlabel("CET")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
        
        
    #housekeeping funcs
    
    def hk_errorhandling(self,kwargs,legallist,funcname):
        
        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)
                
    def hk_func_kwargs(self,kwargs,key,default):
        
        op = kwargs[key] if key in kwargs else default
        return op