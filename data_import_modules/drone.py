import csv
import datetime as dt
import matplotlib.pyplot as plt
import folium
import branca.colormap as cm

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
            