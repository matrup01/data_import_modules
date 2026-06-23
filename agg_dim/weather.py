# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 15:02:42 2025

@author: mrupp
"""

import csv
import datetime as dt
import matplotlib.dates as md
import numpy as np
from .ErrorHandler import IllegalFileFormat, IllegalArgument

    
class WeatherData:
    
    def __init__(self,file):
        """
        Object to read data from the Weatherstation

        Parameters
        ----------
        file : str
            takes a csv-file created by the weatherstation

        Attributes
        ----------
        data : {str : 1D numpy array}
            contains all data in the form of a dictionary
        details : {str : [str, str]}
            contains a description and the unit to each data array

        """
        
        if file.split(".")[1].lower() != "csv":
            raise IllegalFileFormat(file.split(".")[1], 
                                    "csv",
                                    "WeatherData argument")
        with open(file) as f:
            data = list(csv.reader(f,delimiter=","))
            
        datarange = range(1,len(data))
        def read_date(ip_str):
            return dt.datetime.strptime(ip_str,"%Y/%m/%d %H:%M")
        def float2(ip_str):
            try:
                return float(ip_str)
            except:
                return np.nan
        
        self.data = {
            "t" : np.array([read_date(data[i][0]) for i in datarange]),
            "indoortemp" : np.array([float2(data[i][1]) for i in datarange]),
            "indoorhum" : np.array([float2(data[i][2]) for i in datarange]),
            "outdoortemp" : np.array([float2(data[i][3]) for i in datarange]),
            "outdoorhum" : np.array([float2(data[i][4]) for i in datarange]),
            "dewpoint" : np.array([float2(data[i][5]) for i in datarange]),
            "felttemp" : np.array([float2(data[i][6]) for i in datarange]),
            "wind" : np.array([float2(data[i][7]) for i in datarange]),
            "gust" : np.array([float2(data[i][8]) for i in datarange]),
            "winddir" : np.array([float2(data[i][9]) for i in datarange]),
            "abspress" : np.array([float2(data[i][10]) for i in datarange]),
            "relpress" : np.array([float2(data[i][11]) for i in datarange]),
            "solarrad" : np.array([float2(data[i][12]) for i in datarange]),
            "uvi" : np.array([float2(data[i][13]) for i in datarange]),
            "rain" : np.array([float2(data[i][14]) for i in datarange])
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
            takes a day in the format ddmmyyyy. If a day is given only data 
            acquired on that day will be plotted
        setday : str, optional
            takes a day in the format ddmmyyyy. If a setday is given all data 
            will be changed to this day to make it easier to plot against 
            other data
        start : str, optional
            takes a timestamp in the format HHMMSS. if a start is given only 
            data acquired after that timestamp will be plotted
        end : str, optional
            takes a timestamp in the format HHMMSS. if an end is given only 
            data acquired before that timestamp will be plotted
        secondary : bool, optional
            if True the plot will be drawn on the right y-axis. 
            The default is False.
        color : str, optional
            decides the color of the plot. The default is "tab:blue".
        plotlabel : str, optional
            a label that is used for the plot if a legend is drawn. 
            The default is "no label".
        ylabel : str, optional
            a label that is used for the y-axis, if none is given it will 
            be "value in unit", where value and unit are retrieved from 
            the given y
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
        if isinstance(kwargs["day"],str):
            day = kwargs["day"]
            day = ".".join([day[:2],day[2:4],day[4:]])
            correctdate = dt.datetime.strptime(day, "%d.%m.%Y").date()
            for i in range(len(self.data["t"])):
                if self.data["t"][i].date() != correctdate:
                    mask[i] = False
        if isinstance(kwargs["start"],str):
            starthour = int(kwargs["start"][:2])
            startminute = int(kwargs["start"][2:4])
            startsecond = int(kwargs["start"][4:])
            for i in range(len(self.data["t"])):
                if self.data["t"][i].hour < starthour:
                    mask[i] = False
                elif (self.data["t"][i].hour == starthour and 
                      self.data["t"][i].minute < startminute):
                    mask[i] = False
                elif (self.data["t"][i].hour == starthour and 
                      self.data["t"][i].minute == startminute and 
                      self.data["t"][i].second < startsecond):
                    mask[i] = False
        if isinstance(kwargs["end"],str):
            endhour = int(kwargs["end"][:2])
            endminute = int(kwargs["end"][2:4])
            endsecond = int(kwargs["end"][4:])
            for i in range(len(self.data["t"])):
                if self.data["t"][i].hour > endhour:
                    mask[i] = False
                elif (self.data["t"][i].hour == endhour and 
                      self.data["t"][i].minute > endminute):
                    mask[i] = False
                elif (self.data["t"][i].hour == endhour and 
                      self.data["t"][i].minute == endminute and 
                      self.data["t"][i].second > endsecond):
                    mask[i] = False
                    
        xx = self.data["t"][mask]
        yy = self.data[y][mask]
        
        if isinstance(kwargs["setday"],str):
            dday = int(kwargs["setday"][:2])
            dmonth = int(kwargs["setday"][2:4])
            dyear = int(kwargs["setday"][4:])
            xx = np.array([d.replace(day=dday,
                                     month=dmonth,
                                     year=dyear) for d in xx])
            
        if not isinstance(kwargs["ylabel"],str):
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
        
    def returndata(self,secondwise=True):
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
        
        if not secondwise:
            return self.data,self.details
        op_t = [self.data["t"][0]]
        ts = op_t[0]
        indices = [0]
        while ts < self.data["t"][-1]:
            ts = op_t[-1] + dt.timedelta(seconds=1)
            op_t.append(ts)
            indices.append(np.where(self.data["t"]==ts.replace(second=0))[0][0])
        indices = np.array(indices)
        op_data = {"t" : np.array(op_t)}
        
        for key in self.data.keys():
            if key == "t":
                continue
            op_data[key] = self.data[key][indices]
        return op_data,self.details
        
        
    #housekeeping funcs
    
    def hk_errorhandling(self,kwargs,legallist,funcname):
        """Checks if all passed kwargs are legal"""

        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)
                
    def hk_func_kwargs(self,kwargs,key,default):
        """Gives kwargs a default value if they are not passed"""
 
        op = kwargs[key] if key in kwargs else default
        return op
   
