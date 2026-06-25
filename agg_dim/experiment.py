# -*- coding: utf-8 -*-
"""
This Submodule Provides a `Wrapper` that can wrap data from other submodules 
and make them accessable in an easy way.

It also provides functions that allow to save wrapped obj to a .experiment
file.
"""

import datetime as dt
import pickle
import numpy as np
from matplotlib import colormaps
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from .ErrorHandler import IllegalArgument


def save_experiment(wrapper,path):
    """
    Saves a `Wrapper` into a .experiment file.

    Parameters
    ----------
    wrapper : Wrapper
        Wrapper object that should be saved.
    path : str
        Path where the obj should be saved.

    Returns
    -------
    None
    """
    
    if path[-11:] != ".experiment":
        path.append(".experiment")
    with open(path,"wb") as dumppath:
        pickle.dump(wrapper,dumppath,4)
        
def load_experiment(path):
    """
    Loads a .experiment file and returns a `Wrapper`.

    Parameters
    ----------
    path : str
        Path from where the .experiment file should be loaded.

    Returns
    -------
    Wrapper
        Wrapper obj that is loaded from the file.
    """
    
    
    if path[-11:] != ".experiment":
        raise ValueError("This is not a .experiment file!")
    with open(path,"rb") as loadpath:
        return pickle.load(loadpath)

class Wrapper:
    
    def __init__(self,day=1,month=1,year=1900):
        """
        inits a Wrapper object.

        Parameters
        ----------
        day : int, optional
            Sets the day in all time arrays that will be loaded to its value. 
            The default is `1`.
        month : int, optional
            Sets the month in all time arrays that will be loaded to its value. 
            The default is `1`.
        year : int, optional
            Sets the year in all time arrays that will be loaded to its value. 
            The default is `1900`.
            
        Attributes
        ----------
        data : dict
            Dictionary that contains all data arrays from wrapped objects.
        details : dict
            Dictionary that contains all `details` dictionaries from wrapped
            objects.

        Returns
        -------
        None
        """
        
        self.data = {}
        self.details = {}
        
        self.day = day
        self.month = month
        self.year = year
        
        
    def wrap(self,obj,name):
        """
        Includes an Object into the Wrapper, by including its data and details
        into the corresponding dicts and saving the object in Wrapper.name

        Parameters
        ----------
        obj : agg_dim.wibs.WIBS, agg_dim.particle_counters.OPC, agg_dim.particle_counters.Pops, agg_dim.weather.WeatherData or agg_dim.lowcostsensors.FlyingFlo_USB
            This object will be included in the `Wrapper`.
        name : str
            This str will be used as a key in `Wrapper.data` and 
            `Wrapper.details` and it will be the attribute name for the object.

        Returns
        -------
        None
        
        Examples
        --------
        >>> from agg_dim import Wrapper,WIBS
        >>> w = WIBS('example.wibs')
        >>> exp = Wrapper()
        >>> exp.wrap(w,'wibs')
        
        The `agg_dim.wibs.WIBS` obj is now wrapped by the `Wrapper` obj.
        It can be accessed via `exp.wibs` and its data can be accessed through
        `Wrapper` methods.
        """
        
        
        data,details = obj.returndata()
        self.data[name] = data
        self.details[name] = details
        for i in range(len(self.data[name]["t"])):
            self.data[name]["t"][i] = self.data[name]["t"][i].replace(
                day = self.day,
                month = self.month,
                year = self.year
                )
        
        setattr(self,name,obj)
        
    def plot(self,ax,x,y,**kwargs):
        """
        Plots two data arrays against each other.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        x : str
            Takes a str in the format `'plottype@instrument'` and uses it on the 
            x-axis. E.g.: `'total_partconc@wibs'`
        y : str
            Takes a str in the format `'plottype@instrument'` and uses it on the 
            y-axis. E.g.: `'total_partconc@wibs'`
        
        Other Parameters
        ----------------
        start : str, optional
            Takes a str in the format "HH:MM:SS" and only plots data acquired
            after it.
        end : str, optional
            Takes a str in the format "HH:MM:SS" and only plots data acquired
            before it.
        scatter : bool, optonal
            If True a scatter plot will be drawn, else a line plot will be 
            drawn. The default is True.
        color : str, optional
            The plot will be drawn in this color. The default is `'tab:blue'`.
        pearson : bool, optional
            If True Pearsons R for the given data will be printed to console.
            The default is `True`.
        return_arrs : bool, optional
            If True, the function will return the arrays for the x and the y
            axis. The default is `False`.

        Returns
        -------
        xx : np.array
            Array that contains the data from the x-axis. Will only be returned
            if the kwarg `return_arrs` is True.
        yy : np.array
            Array that contains the data from the y-axis. Will only be returned
            if the kwarg `return_arrs` is True.
        """
        
        
        #kwargs
        defaults = {
            "start" : None,
            "end" : None,
            "scatter": True,
            "color" : "tab:blue",
            "pearson" : True,
            "return_arrs" : False
            }
        for key,default in defaults.items():
            kwargs[key] = self.hk_func_kwargs(kwargs, key, default)
        self.hk_errorhandling(kwargs, defaults.keys(), "Wrapper.plot()")
        
        x_val,x_instrument = x.split("@")
        y_val,y_instrument = y.split("@")
        
        # check x and y
        if x_instrument not in self.data.keys():
            loaded = ",".join(list(self.data.keys()))
            raise KeyError(f"{x_instrument} is not loaded. Try one of: "
                           + loaded)
        if x_val not in self.data[x_instrument].keys():
            loaded = ",".join(list(self.data[x_instrument].keys()))
            raise KeyError(f"{x_val} is not legal for {x_instrument}. Try: "
                           + loaded)
        if y_instrument not in self.data.keys():
            loaded = ",".join(list(self.data.keys()))
            raise KeyError(f"{y_instrument} is not loaded. Try one of: "
                           + loaded)
        if y_val not in self.data[y_instrument].keys():
            loaded = ",".join(list(self.data[y_instrument].keys()))
            raise KeyError(f"{y_val} is not legal for {y_instrument}. Try: "
                           + loaded)
            
        # crop
        kwargs["start"],kwargs["end"] = self.hk_checktime(
            x_instrument, 
            y_instrument, 
            kwargs["start"], 
            kwargs["end"])
        if isinstance(kwargs["start"],str) or isinstance(kwargs["end"],str):
            xm = self.hk_timemask(x_instrument, 
                                  kwargs["start"], 
                                  kwargs["end"])
            ym = self.hk_timemask(y_instrument,
                                  kwargs["start"],
                                  kwargs["end"])
        else:
            xm = np.array([True for t in self.data[x_instrument]["t"]])
            ym = np.array([True for t in self.data[y_instrument]["t"]])
            
        # find x and y data
        if x_instrument == y_instrument:
            xx = self.data[x_instrument][x_val][xm]
            yy = self.data[y_instrument][y_val][ym]
        else:
            xt = self.data[x_instrument]["t"][xm]
            yt = self.data[y_instrument]["t"][ym]
            xdata = self.data[x_instrument][x_val][xm]
            ydata = self.data[y_instrument][y_val][ym]
            xm = np.isin(xt,yt)
            ym = np.isin(yt,xt)
            
            xx = xdata[xm]
            yy = ydata[ym]
            
        # plot
        if kwargs["scatter"]:
            ax.scatter(xx,yy,color=kwargs["color"])
        else:
            ax.plot(xx,yy,color=kwargs["color"])
        ax.set_xlabel(self.details[x_instrument][x_val][0]
                      + " in "
                      + self.details[x_instrument][x_val][1])
        ax.set_ylabel(self.details[y_instrument][y_val][0]
                      + " in "
                      + self.details[y_instrument][y_val][1])
            
        if kwargs["pearson"]:
            x = xx - np.mean(xx)
            y = yy - np.mean(yy)
            sp = np.sum(x*y)
            sqx = np.sum(x**2)
            sqy = np.sum(y**2)
            r = sp/(np.sqrt(sqx*sqy))
            print(f"Pearson's R: {r:.3f}")
            
        if kwargs["return_arrs"]:
            return xx,yy
        
        
    def windrose(self,ax,y,**kwargs):
        """
        Plots a heatmap of y on a windrose plot, where the theta angle
        corresponds to the cardinal direction and the radius corresponds to 
        the wind speed.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis. This axis has to be of the 
            projection `'polar'`.
        y : str
            Takes a str in the format `'plottype@instrument'` and uses it to
            determine which data shold be plotted. E.g.: 
            `'total_partconc@wibs'`
            
        Other Parameters
        ----------------
        weatherdata : str, optional
            The given str is used as the instrument name of the weatherstation,
            which is expected to have the data rows `'wind'` and `'winddir'`.
            The default is `'weather'`.
        theta : str, optional
            Specifies which data row should be used for the theta axis. It has
            to be either in rad or in degrees (If it is given in degrees, 
            `Wrapper.details['weather']['theta'][1]` has to be `'°'`). The 
            default is `'winddir'`.
        radius : str, optional
            Specifies which data should be used for the binning along the 
            radius. The default is `'wind'`.
        start : str, optional
            Takes a str in the format "HH:MM:SS" and only plots data acquired
            after it.
        end : str, optional
            Takes a str in the format "HH:MM:SS" and only plots data acquired
            before it.
        scatter : bool, optional
            If True, a scatter plot of the raw winddata is plotted over the 
            heatmap, which can be used to get an overview over how dense the 
            data is. The default is `True`.
        scatter_color : str, optional
            Changes the color of the scatter plot (only in effect if `scatter`
            is `True`). The default is `'tab:blue'`.
        colormap : str, optional
            Changes the colormap, that is used for the heatmap. The default is
            'viridis'.
        min_threshold : int, optional
            If a min_threshold is given, only bins with at least min_threshold
            are shown. The default is `0`.
        sectors : int, optional
            The windrose will be devided into this many sectors along the 
            theta axis. The default is `4`.
        bins : int, optional
            The windrose will be devided into this many bins along the radius.
            The default is `3`.
        heatmap_lim : list or tuple of float with len 2, optional
            If a `heatmap_lim` is given, the limits of the colorbar will be set
            to its values. If no `heatmap_lim` is given, the minimum and the 
            maximum values will be used as limits.
        windspeed_lim : int or float, optional
            If a `windspeed_lim` is passed, it will be used as the maximum 
            radius of the windrose. Otherwise the maximum windspeed in the 
            dataset will be used.
        startangle : int or float, optional
            Will turn the sectors clockwise by its value degrees. The default 
            is `0`, which means that the first sector has its lower boundary at 
            exactly North.
        usedegrees : bool, optional
            If `True` the plot will use degrees as theta axis ticks instead of
            cardinal directions (N,E,S,W). The default is `False`.
        inverted : bool, optional
            If `True` the theta values will be inverted. E.g. if the raw data
            gives the angle from which the wind blows, `inverted = True` will
            plot the angle the wind blows to. The default is `False`.

        Returns
        -------
        None
        """
        
        
        #kwargs
        defaults = {
            "weatherdata" : "weather",
            "start" : None,
            "end" : None,
            "scatter": True,
            "scatter_color" : "tab:blue",
            "colormap" : "viridis",
            "min_threshold" : 0,
            "sectors" : 4,
            "bins" : 3,
            "heatmap_lim" : None,
            "windspeed_lim" : None,
            "startangle" : 0,
            "usedegrees" : False,
            "theta" : "winddir",
            "radius" : "wind",
            "inverted" : False
            }
        for key,default in defaults.items():
            kwargs[key] = self.hk_func_kwargs(kwargs, key, default)
        self.hk_errorhandling(kwargs, defaults.keys(), "Wrapper.windrose()")
        
        #check ax and y
        if ax.name != "polar":
            msg = "The passed ax has to be polar for Wrapper.windrose() to"
            msg += " work properly."
            raise ValueError(msg)
        y_data,y_instrument = y.split("@")
        try:
            self.data[y_instrument][y_data]
        except:
            legallist = []
            for key in self.data:
                for data in self.data[key]:
                    if data != "t":
                        legallist.append(f"{data}@{key}")
            legalstr = ",".join(legallist)
            raise ValueError(f"{y} is no legal y. Try one of {legalstr}")

        #crop
        kwargs["start"],kwargs["end"] = self.hk_checktime(
            kwargs["weatherdata"], 
            y_instrument, 
            kwargs["start"], 
            kwargs["end"])
        if isinstance(kwargs["start"],str) or isinstance(kwargs["end"],str):
            wind_m = self.hk_timemask(kwargs["weatherdata"], 
                                      kwargs["start"],
                                      kwargs["end"])
            y_m = self.hk_timemask(y_instrument, 
                                   kwargs["start"], 
                                   kwargs["end"])
        else:
            wind_m = np.array(
                [True for i in self.data[kwargs["weatherdata"]]["t"]]
                )
            y_m = np.array(
                [True for i in self.data[y_instrument]["t"]]
                )
        
        #load data
        winddir = kwargs["theta"]
        if self.details[kwargs["weatherdata"]][winddir][1] == "°":
            theta = np.radians(
                self.data[kwargs["weatherdata"]][winddir][wind_m]
                )
        else:
            theta = self.data[kwargs["weatherdata"]][winddir][wind_m]
        if kwargs["inverted"]:
            theta = (theta + np.pi) % (2*np.pi)
        r = self.data[kwargs["weatherdata"]][kwargs["radius"]][wind_m]
        z = self.data[y_instrument][y_data][y_m]
        
        if (np.count_nonzero(wind_m) == 0 
            or np.count_nonzero(y_m) == 0):
            raise ValueError("There are no values in the given timeframe")
        
        #transform data an plot
        kwargs["startangle"] = kwargs["startangle"]%(360/kwargs["sectors"])
        kwargs["startangle"] = np.radians(kwargs["startangle"])
        sector_borders = np.linspace(kwargs["startangle"], 
                                     2*np.pi+kwargs["startangle"],
                                     kwargs["sectors"]+1)
        sector_borders = sector_borders % (2*np.pi)
        if kwargs["windspeed_lim"] is None:
            bin_borders = np.linspace(0,np.max(r),kwargs["bins"]+1)
        else:
            bin_borders = np.linspace(0,
                                      kwargs["windspeed_lim"],
                                      kwargs["bins"]+1)
        
        darr = np.zeros((kwargs["bins"],kwargs["sectors"]))
        for b in range(kwargs["bins"]):
            bm = np.where(r>=bin_borders[b],True,False)
            bm = np.where(r<=bin_borders[b+1],bm,False)
            for sec in range(kwargs["sectors"]):
                if sector_borders[sec] < sector_borders[sec+1]:
                    sm = np.where(theta>=sector_borders[sec],bm,False)
                    sm = np.where(theta<=sector_borders[sec+1],sm,False)
                else:
                    sm1 = np.where(theta>=sector_borders[sec],
                                  True,
                                  False)
                    sm2 =  np.where(theta<=sector_borders[sec+1],
                                  True,
                                  False)
                    sm = sm1 | sm2
                    sm = sm & bm
                
                if np.count_nonzero(sm) < kwargs["min_threshold"]:
                    darr[b][sec] = np.nan
                else:
                    darr[b][sec] = np.nanmean(z[sm])
        cm = colormaps[kwargs["colormap"]]
        if (kwargs["heatmap_lim"] is not None 
            and len(kwargs["heatmap_lim"]) == 2):
            minval = kwargs["heatmap_lim"][0]
            maxval = kwargs["heatmap_lim"][1]
        else:
            minval = np.nanmin(darr)
            maxval = np.nanmax(darr)
        
        for b in range(kwargs["bins"]):
            for sec in range(kwargs["sectors"]):
                color = (darr[b][sec]-minval)/(maxval-minval)
                if sector_borders[sec] < sector_borders[sec+1]:
                    ax.bar(
                        x=(sector_borders[sec]+sector_borders[sec+1])/2, 
                        height=bin_borders[b+1]-bin_borders[b], 
                        width=sector_borders[sec+1]-sector_borders[sec], 
                        bottom=bin_borders[b], 
                        color=cm(color)
                    )
                else:
                    ax.bar(
                        x=(sector_borders[sec]+2*np.pi)/2, 
                        height=bin_borders[b+1]-bin_borders[b], 
                        width=2*np.pi-sector_borders[sec], 
                        bottom=bin_borders[b], 
                        color=cm(color)
                    )
                    ax.bar(
                        x=sector_borders[sec+1]/2, 
                        height=bin_borders[b+1]-bin_borders[b], 
                        width=sector_borders[sec+1], 
                        bottom=bin_borders[b], 
                        color=cm(color)
                    )
                    
        #misc plotting
        if kwargs["scatter"]:
            ax.scatter(theta,r,color=kwargs["scatter_color"])
        if not kwargs["usedegrees"]:
            ax.set_thetagrids([0,90,180,270],["N","E","S","W"])
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("N")
        ffig = ax.figure
        c = ScalarMappable(Normalize(minval,maxval),kwargs["colormap"])
        label = self.details[y_instrument][y_data][0] 
        label += " in "
        label += self.details[y_instrument][y_data][1]
        ffig.colorbar(c,
                      ax=ax,
                      label=label)
        ffig.tight_layout()
        
            
    ## Housekeeping Funcs
    
    def hk_func_kwargs(self,kwargs,key,default):
        """
        Housekeeping Func --> Should not be used outside the object
        
        Gives kwargs a default value if they are not passed
        """

        op = kwargs[key] if key in kwargs else default
        return op
    
    def hk_errorhandling(self,kwargs,legallist,funcname):
        """
        Housekeeping Func --> Should not be used outside the object
        
        Checks if all passed kwargs are legal
        """

        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)
                
    def hk_checktime(self,x_instrument,y_instrument,start_str,end_str):
        """
        Housekeeping Func --> Should not be used outside the object
        
        Checks if the given time window is outside one of the instruments
        time windows and returns corrected start and end strings
        """
        
        x_t = self.data[x_instrument]["t"]
        y_t = self.data[y_instrument]["t"]
        
        if start_str is not None:
            start = dt.datetime.strptime(start_str, "%H:%M:%S").replace(
                year = x_t[0].year,
                month = x_t[0].month,
                day = x_t[0].month
                )
        else:
            start = x_t[0]
        if end_str is not None:
            end = dt.datetime.strptime(end_str, "%H:%M:%S").replace(
                year = x_t[0].year,
                month = x_t[0].month,
                day = x_t[0].month
                )
        else:
            end = x_t[-1]
        if start < x_t[0]:
            start = x_t[0]
        if end > x_t[-1]:
            end = x_t[-1]
            
        start = start.replace(
            year = y_t[0].year,
            month = y_t[0].month,
            day = y_t[0].month
            )
        end = end.replace(
            year = y_t[0].year,
            month = y_t[0].month,
            day = y_t[0].month
            )
        if start < y_t[0]:
            start = y_t[0]
        if end > y_t[-1]:
            end = y_t[-1]
        
        return start.strftime("%H:%M:%S"),end.strftime("%H:%M:%S")
                
                
    def hk_timemask(self,y,start_str,end_str):
        """
        Housekeeping Func --> Should not be used outside the object
        
        Returns a mask within start and end for an instrument y
        """
        
        try:
            t = self.data[y]["t"]
        except:
            raise ValueError(f"Instrument {y} is not loaded.")
            
        try:
            if start_str is None:
                start = t[0]
            else:
                start = dt.datetime.strptime(start_str,"%H:%M:%S").replace(
                    year = t[0].year,
                    month = t[0].month,
                    day = t[0].day
                    )
        except:
            msg = f"{start_str} is no legal format for the 'start' "
            msg += "kwarg. It needs to be 'HH:MM:SS'."
            raise ValueError(msg)
        try:
            if end_str is None:
                end = t[-1]
            else:
                end = dt.datetime.strptime(end_str,"%H:%M:%S").replace(
                    year = t[0].year,
                    month = t[0].month,
                    day = t[0].day
                    )
        except:
            msg = f"{end_str} is no legal format for the 'end' "
            msg += "kwarg. It needs to be 'HH:MM:SS'."
            raise ValueError(msg)
        
        m = np.where(t>=start,
                     True,
                     False)
        m = np.where(t<=end,
                     m,
                     False)
        return m
        