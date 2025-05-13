import csv
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as md
import folium
from folium.plugins import HeatMap
import branca.colormap as cm
from .ErrorHandler import IllegalArgument, IllegalFileFormat
import numpy as np
from numba import njit, prange, float64

class Dronedata:
    
    """full documentation see https://github.com/matrup01/data_import_modules \n
    
    file (str) ... takes a drone-produced csv-file"""
    
    def __init__(self,file):
        
        data = csv.reader(open(file),delimiter=",")
        data = list(data)
        
        self.t = [dt.datetime.strptime(data[i][1].replace(",","."),"%I:%M:%S.%f %p") for i in range(1,len(data))]
        #data: [height,long,lat,ws]
        self.data = [[float(data[i][6].replace(",",".")) for i in range(1,len(data))],
                     [float(data[i][5].replace(",",".")) for i in range(1,len(data))],
                     [float(data[i][4].replace(",",".")) for i in range(1,len(data))],
                     [data[i][192].replace(",",".") for i in range(1,len(data))]]
        
        #correct empty parts in ws-data:
        
        for i in range(len(self.data[3])):
            if self.data[3][i] == "":
                self.data[3][i] = "0"
        self.data[3] = [float(self.data[3][i]) for i in range(len(self.data[3]))]
        
    def plot(self,ax,plot="height",color="tab:purple",secondary=False):
        
        plotx,ploty,label,ylabel = self.findplottype(plot)
        
        ax.plot(plotx,ploty,label=label,color=color)
        ax.set_ylabel(ylabel)
        ax.axes.yaxis.label.set_color(color)
        ax.tick_params(axis='y', colors=color)
        if not secondary:
            ax.spines["left"].set_color(color)
        else:
            ax.spines["right"].set_color(color)
            ax.spines["left"].set_alpha(0)
            
            
    def flightmap(self,zoomstart=21,colors=["brown","white","blue"]):
        
        #im = ax.scatter(x=self.data[1],y=self.data[2],c=self.data[0],cmap="terrain")
        #plt.colorbar(im,ax=ax,label="Drone height",orientation="horizontal",location="top")
        
        x_start = (max(self.data[2]) + min(self.data[2])) / 2
        y_start = (max(self.data[1]) + min(self.data[1])) / 2
        
        cmap = cm.LinearColormap(colors=colors,vmin=min(self.data[0]),vmax=max(self.data[0]),caption="height in m")
        
        output = folium.Map(location=(x_start,y_start),control_scale=True,zoom_start=zoomstart,max_zoom=50)
        
        for height,long,lat in zip(self.data[0],self.data[1],self.data[2]):
            folium.Circle(location=[lat,long],radius=0.1,fill=True,color=cmap(height)).add_to(output)
            
        output.add_child(cmap)
        
        output.show_in_browser()
        
    def findplottype(self,y):
        
        plottypes = [["height","Drone height","height AGL in m"],["long","Drone longitude","Drone longitude"],["lat","Drone latitude","Drone latitude"],["ws","wind speed","wind speed in km/h"]]
        
        #find correct plottype
        for i in range(len(plottypes)):
            if plottypes[i][0] == y:
                plotx = self.t
                ploty = self.data[i]
                label = plottypes[i][1]
                ylabel = plottypes[i][2]
                
                return plotx,ploty,label,ylabel
            
    def append(self,obj):
        
        for i in obj.t:
            self.t.append(i)
            
        for i in range(len(self.data)):
            for j in obj.data[i]:
                self.data[i].append(j)
                
                
    def heightVSws(self):
        
        fig,ax = plt.subplots()
        
        ax.scatter(x=self.data[0],y=self.data[3])
        
        plt.show()
        
        
        
class DroneWrapper:
    
    def __init__(self,file,**kwargs):
        
        #kwargs
        defaults = {"dronetype" : "BladeScapes",
                    "start" : "*",
                    "end" : "*"
            }
        for key,value in zip(defaults.keys(),defaults.values()):
            self.hk_kwargs(kwargs, key, value)
        self.hk_errorhandling(kwargs, defaults.keys(), "DroneWrapper")
        
        #variables
        self.data = {}
        self.details = {"Drone" : {"height" : ["Height AGL","m AGL"], "long" : ["longitude","eastern longitude"], "lat" : ["latitude","nothern latitude"]}}
        
        if file.split(".")[-1] != "csv":
            raise IllegalFileFormat(file.split(".")[-1], ".csv", "DroneWrapper arguments")
          
        data = csv.reader(open(file),delimiter=",")
        data = list(data)
            
        match self.dronetype.lower():
            case "own":
                self.data["Drone"] = {
                    "t" : np.array([dt.datetime.strptime(data[i][1].replace(",","."),"%I:%M:%S.%f %p").replace(microsecond=0) for i in range(1,len(data))]),
                    #data: [height,long,lat,ws]
                    "height" : np.array([float(data[i][6].replace(",",".")) for i in range(1,len(data))]),
                    "long" : np.array([float(data[i][5].replace(",",".")) for i in range(1,len(data))]),
                    "lat" : np.array([float(data[i][4].replace(",",".")) for i in range(1,len(data))]),
                    }
            case "bladescapes":
                current_time = data[1][1][:-4]
                takeoff_alt = float(data[1][12])
                h_appender, long_appender, lat_appender = [],[],[]
                t, h, long, lat = [], [], [], []
                for line in data[1:]:
                    if line[1][:-4] == current_time:
                        h_appender.append(float(line[12])-takeoff_alt)
                        long_appender.append(float(line[11]))
                        lat_appender.append(float(line[10]))
                    else:
                        t.append(dt.datetime.strptime(current_time.replace(".","-"),"%Y-%m-%d %H:%M:%S"))
                        h.append(np.mean(h_appender))
                        long.append(np.mean(long_appender))
                        lat.append(np.mean(lat_appender))
                        h_appender = [float(line[12])-takeoff_alt]
                        long_appender = [float(line[11])]
                        lat_appender = [float(line[10])]
                        current_time = line[1][:-4]
                        
                    self.data["Drone"] = {
                        "t" : np.array(t),
                        "height" : np.array(h),
                        "long" : np.array(long),
                        "lat" : np.array(lat)
                        }
                    
        #crop
        if self.start != "*":
            for i in range(len(self.data["Drone"]["t"])):
                if dt.datetime.strptime(self.start,"%H:%M:%S").time() <= self.data["Drone"]["t"][i].time():
                    break
            start_i = i
        else: start_i = 0
        
        if self.end != "*":
            for i in range(len(self.data["Drone"]["t"])):
                if dt.datetime.strptime(self.end,"%H:%M:%S") <= self.data["Drone"]["t"][i]:
                    break
            end_i = i
        else: end_i = len(self.data["Drone"]["t"])-1
        
        for key in self.data["Drone"]:
            self.data["Drone"][key] = self.data["Drone"][key][start_i:end_i]
                 
                
    def wrap(self,name,obj):
        
        y,details = obj.returndata()
        
        self.data[name] = y
        self.details[name] = details
        
    
    def returndata(self,nested=False):
        
        if nested:
            return self.data,self.details
        else:
            return self.data["Drone"],self.details["Drone"]
        
        
    def flightmap(self,zoomstart=21,colors=["brown","white","blue"]):
        
        _lat = self.data["Drone"]["lat"]
        _long = self.data["Drone"]["long"]
        for i in range(len(_lat)):
            if np.isnan(_lat[i]):
                _lat[i] = _lat[i-1] if i != 0 else _lat[-1]
            if np.isnan(_long[i]):
                _long[i] = _long[i-1] if i != 0 else _lat[-1]
        
        x_start = (max(self.data["Drone"]["lat"]) + min(self.data["Drone"]["lat"])) / 2
        y_start = (max(self.data["Drone"]["long"]) + min(self.data["Drone"]["long"])) / 2
        
        cmap = cm.LinearColormap(colors=colors,vmin=min(self.data["Drone"]["height"]),vmax=max(self.data["Drone"]["height"]),caption="Height AGL in m")
        
        output = folium.Map(location=(x_start,y_start),control_scale=True,zoom_start=zoomstart,max_zoom=50)
        
        for height,long,lat in zip(self.data["Drone"]["height"],self.data["Drone"]["long"],self.data["Drone"]["lat"]):
            folium.Circle(location=[lat,long],radius=0.1,fill=True,color=cmap(height)).add_to(output)
            
        output.add_child(cmap)
        
        output.show_in_browser()
        
        
    def advancedflightmap(self,y,**kwargs):
        
        #import kwargs
        defaults = {"zoomstart" : 21,
                    "colors" : ["purple","blue","yellow","red"],
                    "target_height" : "none",
                    "height_deviation" : 1,
                    "bettermap" : False,
                    "bettermap_resolution" : 15
            }
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "DroneWrapper.advancedflightmap()")
        
        name,yy = y.split("_")
        y = self.data[name][yy]
        
        xt = [self.data["Drone"]["t"][i].time() for i in range(len(self.data["Drone"]["t"]))]
        yt = [self.data[name]["t"][i].time() for i in range(len(self.data[name]["t"]))]
        
        if xt[0] in yt:
            x_start = 0
            y_start = yt.index(xt[0])
            if len(yt) >= y_start + len(xt):
                x_end = len(xt)
                y_end = y_start + len(xt)
            else:
                y_end = len(yt)
                x_end = x_start + (y_end - y_start)
        else:
            y_start = 0
            x_start = xt.index(yt[0])
            if len(xt) >= x_start + len(yt):
                y_end = len(yt)
                x_end = x_start + len(yt)
            else:
                x_end = len(xt)
                y_end = y_start + (x_end - x_start)
                
        lat = self.data["Drone"]["lat"][x_start:x_end]
        long = self.data["Drone"]["long"][x_start:x_end]
        y = self.data[name][yy][y_start:y_end]
        
        m1 = np.isfinite(lat)
        m2 = np.isfinite(long)
        m3 = np.isfinite(y)
        m = m1 & m2 & m3
        
        lat = lat[m]
        long = long[m]
        y = y[m]
        
        if type(kwargs["target_height"]) != str:
            height = self.data["Drone"]["height"][x_start:x_end]
            height = height[m]
            m1 = np.greater_equal(height,kwargs["target_height"]-kwargs["height_deviation"])
            m2 = np.less_equal(height,kwargs["target_height"]+kwargs["height_deviation"])
            m = m1 & m2
            lat = lat[m]
            long = long[m]
            y = y[m]
            
        if not kwargs["bettermap"]:
            x1_start = (max(lat) + min(lat)) / 2
            x2_start = (max(long) + min(long)) / 2
            
            cmap = cm.LinearColormap(colors=kwargs["colors"],vmin=min(y),vmax=max(y),caption=f"{self.details[name][yy][0]} in {self.details[name][yy][1]}")
            output = folium.Map(location=(x1_start,x2_start),control_scale=True,zoom_start=kwargs["zoomstart"],max_zoom=50)
    
            for _y,_long,_lat in zip(y,long,lat):
                folium.Circle(location=[_lat,_long],radius=0.1,fill=True,color=cmap(_y)).add_to(output)
                    
            output.add_child(cmap)
            
            output.show_in_browser()
        else:
            res = kwargs["bettermap_resolution"]
            map_array = np.zeros((res,res,2))
            min_lat = min(lat)
            max_lat = max(lat)
            min_long = min(long)
            max_long = max(long)
            lats = np.array([ min_lat + (max_lat-min_lat)/res*i for i in range(res+1)],float)
            longs = np.array([min_long + (max_long-min_long)/res*i for i in range(res+1)],float)
            
            #@njit(float64[:,:,:],(float64[:,:,:],float64[:],float64[:],float64[:],float64[:],float64[:]))
            def calcmap(nb_map_array,nb_lats,nb_longs,nb_y,nb_lat,nb_long):
                for i in range(len(nb_y)):
                    for x in range(res):
                        if nb_lat[i] >= nb_lats[x] and nb_lat[i] <= nb_lats[x+1]:
                            for y in range(res):
                                if nb_long[i] >= nb_longs[y] and nb_long[i] <= nb_longs[y+1]:
                                    nb_map_array[x][y][0] += nb_y[i]
                                    nb_map_array[x][y][1] += 1
                a=2
                return nb_map_array
             
            map_array = calcmap(map_array,lats,longs,y,lat,long)
            map_array_2d = np.zeros((res,res))
            for xx in range(len(map_array)):
                for yi in range(len(map_array)):
                    map_array_2d[xx][yi] = map_array[xx][yi][0] / map_array[xx][yi][1] if map_array[xx][yi][1] != 0 else 0
                    
            x1_start = (max(lat) + min(lat)) / 2
            x2_start = (max(long) + min(long)) / 2
            
            cmap = cm.LinearColormap(colors=kwargs["colors"],vmin=min(y),vmax=max(y),caption=f"{self.details[name][yy][0]} in {self.details[name][yy][1]}")
            output = folium.Map(location=(x1_start,x2_start),control_scale=True,zoom_start=kwargs["zoomstart"],max_zoom=50)
    
            for x in range(res):
                for y in range(res):
                    if map_array_2d[x][y] != 0:
                        folium.Rectangle([(lats[x],longs[y]),(lats[x+1],longs[y+1])],fill=True,color=cmap(map_array_2d[x][y])).add_to(output)
                    
            output.add_child(cmap)
            
            output.show_in_browser()
        
        
    def plot(self,ax,y,**kwargs):
        
        #import kwargs   
        defaults = {"quakes" : [],
                    "quakeslabel" : "no label",
                    "quakecolor" : "tab:purple",
                    "color" : "tab:green",
                    "plotlabel" : "no label",
                    "ylabel" : "*",
                    "secondary" : False,
                    "masknan" : True}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "DroneWrapper.plot()")
        
        name,yy = y.split("_")
        y = self.data[name][yy]
        x = self.data[name]["t"]     
        
        if kwargs["masknan"]:
            m = np.isfinite(y)
            y = y[m]
            x = x[m]
        
        if kwargs["ylabel"] == "*":
            kwargs["ylabel"] = f"{self.details[name][yy][0]} in {self.details[name][yy][1]}"
        
        #draw plot
        ax.plot(x,y,label=kwargs["plotlabel"],color=kwargs["color"])
        ax.set_ylabel(kwargs["ylabel"])
        ax.set_xlabel("CET")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        if len(kwargs["quakes"]) != 0:
            ax.vlines(x=[dt.datetime.strptime(element, "%H:%M:%S")for element in kwargs["quakes"]],ymin=min(y),ymax=max(y),color=kwargs["quakecolor"],ls="dashed",label=kwargs["quakeslabel"])
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
        
        
    def advancedplot(self,ax,x,y,**kwargs):
        
        #import kwargs   
        defaults = {"color" : "tab:green",
                    "plotlabel" : "no label",
                    "xlabel" : "*",
                    "ylabel" : "*",
                    "scatter" : False,
                    "secondary" : False,
                    "masknan" : True}
        for key,default in zip(defaults.keys(),defaults.values()):
            kwargs[key] = self.hk_func_kwargs(kwargs,key,default)
        self.hk_errorhandling(kwargs, defaults.keys(), "DroneWrapper.advancedplot()")
        
        xname,xx = x.split("_")
        yname,yy = y.split("_")
        xt = [self.data[xname]["t"][i].time() for i in range(len(self.data[xname]["t"]))]
        yt = [self.data[yname]["t"][i].time() for i in range(len(self.data[yname]["t"]))]
        
        if xt[0] in yt:
            x_start = 0
            y_start = yt.index(xt[0])
            if len(yt) >= y_start + len(xt):
                x_end = len(xt)
                y_end = y_start + len(xt)
            else:
                y_end = len(yt)
                x_end = x_start + (y_end - y_start)
        else:
            y_start = 0
            x_start = xt.index(yt[0])
            if len(xt) >= x_start + len(yt):
                y_end = len(yt)
                x_end = x_start + len(yt)
            else:
                x_end = len(xt)
                y_end = y_start + (x_end - x_start)
                
        x = self.data[xname][xx][x_start:x_end]
        y = self.data[yname][yy][y_start:y_end]
        if kwargs["masknan"]:
            xmask = np.isfinite(x)
            ymask = np.isfinite(y)
            mask = ymask & xmask
            x = x[mask]
            y = y[mask]
        
        if kwargs["xlabel"] == "*":
            kwargs["xlabel"] = f"{self.details[xname][xx][0]} in {self.details[xname][xx][1]}"
        if kwargs["ylabel"] == "*":
            kwargs["ylabel"] = f"{self.details[yname][yy][0]} in {self.details[yname][yy][1]}"
            
        #draw plot
        if kwargs["scatter"]:
            ax.scatter(x,y,label=kwargs["plotlabel"],color=kwargs["color"])
        else:
            ax.plot(x,y,label=kwargs["plotlabel"],color=kwargs["color"])
        ax.set_ylabel(kwargs["ylabel"])
        ax.set_xlabel(kwargs["xlabel"])
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
        
            
    #housekeeping funcs
    def hk_kwargs(self,kwargs,key,default):
        
        op = kwargs[key] if key in kwargs else default
        exec(f"self.{key} = op")
        
    def hk_errorhandling(self,kwargs,legallist,funcname):
        
        for key in kwargs:
            if key not in legallist:
                raise IllegalArgument(key,funcname,legallist)
                
    def hk_func_kwargs(self,kwargs,key,default):
        
        op = kwargs[key] if key in kwargs else default
        return op
            