1.    particle_counters.py:


1.1   Pops(file,**kwargs)

	creates a Pops-Object
	
	file (str) ... Takes a POPS-produced csv-file (eg '112233.csv')

	title (str,optional) ... Takes a str and uses it as a title for quickplots
	start (str,optional) ... Takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... Takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	bgobj (Pops,optional) ... Takes another Pops-Object and corrects the data using the given Pops-Objects as Background
	timecorr (int,optional) ... Takes an int and corrects popstime by it, default-23
	relobj(Pops,optional) ... Takes a Pops object and displays all data as relative to the mean of it (see 1.22)
	deviate(bool,optional) ... decides if values should be expressed as relatives to mean, default-False
	layout (dict or str,optional) ... decides which columns from the csv should be taken as input. You can use one of the provided ones (see lookuptable) by entering a str or use a custom one by entering a dict, default - "FlyingFlo2.0"
        Layout-Lookuptable:
            desktopmode ... {"bins" : [pbin for pbin in range(33,49)],
                            "ydata" : "NULL",
                            "ydata2" : [5,20,11],
                            "popstime" : 1,
                            "t" : -1,
                            "flow" : 15}
            box_pallnsdorfer ... {"bins" : [pbin for pbin in range(56,72)],
                                "ydata" : [2,3,11,10,4,5,6,7,8,9,12,13,14,15],
                                "ydata2" : [28,43,34],
                                "popstime" : 23,
                                "t" : 1,
                                "flow" : 38}
            FlyingFlo2.0  ... {"bins" : [pbin for pbin in range(36,52)],
                                "ydata" : "NULL",
                                "ydata2" : [6,21,12],
                                "popstime" : 3,
                                "t" : 1,
                                "flow" : 16}

1.1.1   Pops.exportbg()

	treats the data from the Pops-file as bg and returns the bg in the format [[ch0-ch15],total]
	can be used, however the method to import a bgobj (see 1.1) is better

1.1.2   Pops.importbg(bg)

	uses data in the format [[ch0-ch15],total] and corrects the Pops-objects data by it
	just use the method to import a bgobj, trust me it's better (see 1.1)

	bg (nested list of floats) ... Takes a list containing the data for bg-correction 

1.1.3   Pops.quickplot(y)

	draws a plot y vs time

	y (str) ... takes a string to determine which y should be plotted (for accepted strings see 1.16)

	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount seconds
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount seconds

1.1.4   Pops.plot(ax,y)

	draws a plot y vs time on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	y (str) ... takes a string to determine which y should be plotted (for accepted strings see 1.16)

	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount seconds
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount seconds
	quakes (list of str, optional) ... takes a list of string in the format 'hh:mm:ss' and draws vertical, dashed lines at those timestamps
	quakeslabel (str, optional) ... takes a str and uses it as a label for the quakes if a legend is used
	quakecolor (str, optional) ... changes the color of the quakes, default-"tab:pink"
	color (str, optional) ... changes the color of the plot, default-"tab:blue"
	togglexticks (bool, optional) ... takes a boolean to decide if the x-ticks of ax should be visible, default-True
	printstats (bool, optional) ... takes a boolean to decide if mean, std and var of the plot should be printed to the console, default-False
	secondary (bool, optional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False
	plotlabel (str, optional) ... changes label of the plot (used for legend) into the given string. If none is given, it uses one fitting the given y
	usepopstime (bool, optional) ... if True, popstime is used rather than raspi-time

1.1.5   Pops.quickheatmap()

	draws a dndlogdp-heatmap over time 

1.1.6   Pops.heatmap(ax)

	draws a dndlogdp-heatmap over time on an existing matplotlib-axis
	
	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn

	togglexticks (bool, optional) ... takes a boolean to decide if the x-ticks of ax should be visible, default-True
	orientation (str, optional) ... takes a str to change the orientation of the colorbar, default - "horizontal"
	location (str, optional) ... takes a str to change the location of the colorbar relative to the plot, default-"top"
	togglecbar (bool, optional) ... takes a bool to determine if the cbar should be drawn, default-True
	pad (float, optional) ... takes a float and moves the cbar further away from the heatmap the higher the pad is, default-0
	
1.1.7  Pops.dndlogdp(ax)

	draws a barplot of dndlogdp-distribution on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn

1.1.8  Pops.quickdndlogdp()

	draws a barplot of dndlogdp-distribution

1.1.9  Pops.cumulativeparticles()

	prints and returns the sum of the means of all bins
	no real usecase, was used before "total"-channel was implemented

1.1.10  Pops.crop(startcrop,endcrop)

	Shouldn't be used any more, use start and end in init (see 1.1)
	crops the data by startcrop seconds at the start and endrop seconds at the end

	startcrop (int) ... Takes an int and crops the beginning of the plot by its amount seconds
	endcrop (int) ... Takes an int and crops the end of the plot by its amount seconds

1.1.11  Pops.stats(y)

	prints mean, std and var of the given data to the console

	y (str) ... takes a string to determine which y should be plotted (for accepted strings see 1.16)

1.1.12  Pops.returnstats(y)

	return mean, std and var of the given data in the format [mean,std,var]

	y (str) ... takes a string to determine which y should be plotted (for accepted strings see 1.16)
	
1.1.13  Pops.append(obj)
	
	takes another Pops-Object and appends its data to the first one to create one object that contains all data 
	
	obj (Pops-obj) ... takes a Pops object whichs data should be appended
	
1.1.14  Pops.add(obj)	
	
	takes another Pops-Object and returns a new Pops-Object containing data of both objects without changing them 
	
	obj (Pops-obj) ... takes a Pops object whichs data should be appended
	
1.1.15  Pops.average()
	
	averages all the data minutewise

1.1.16  Pops.returndata()

	up to v0.1.1: takes an argument y and returns a list of the data y
	
	v0.1.2 or newer: returns a dict of all data
	
1.1.17  Pops.relativevals(bgobj)

	changes all data to relative to the mean of the bgobj
	
	bgobj (Pops-obj) ... takes a Pops object to whichs mean data should be relative to
	
1.1.18  Pops.deviatefrommean()

	changes all values to be expressed relative to the mean
	
1.1.19  Pops.newheatmap(ax)

	creates a heatmap with consistant y-increments on an existing axis
	
	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	
	orientation (str, optional) ... takes a str to change the orientation of the colorbar, default - "horizontal"
	location (str, optional) ... takes a str to change the location of the colorbar relative to the plot, default-"top"
	pad (float, optional) ... takes a float and moves the cbar further away from the heatmap the higher the pad is, default-0
	
	
1.2   OPC(file,**kwargs)

    creates an OPC-object
    
    file (str) ... takes an OPC-produced ...-C.dat file
    
    mfile (str, optional) ... takes an OPC-produced ...-M.dat file (if no mfile is given, the program will replace the C in the ...-C.dat file with an M and look for the filename at the same path)
    dmfile (str, optional) ... takes an OPC-produced ...-dM.dat file (if no dmfile is given, the program will replace the C in the ...-C.dat file with dM and look for the filename at the same path)
    start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	bins (list of float, optional) ... takes a list of the geometric means of the bins, if none is given it will assume the standard bins (bins=[0.253,0.298,0.352,0.414,0.488,0.576,0.679,0.8,0.943,1.112,1.31,1.545,1.821,2.146,2.53,2.982,3.515,4.144,4.884,5.757,6.787,8,9.43,11.12,13.1,15.45,18.21,21.46,25.3,29.82,35.15])
	
1.2.1 OPC.save(name)

    saves the OPC-object to an .opc file
    
    name (str) ... specifies the name and path where the file should be saved to
    
1.2.2 OPC.plot(ax,y,**kwargs)

    plots a plot y vs time over an existing mpl axis
    
    ax (Axes object of mpl.axes module) ... axis on which the plot should be drawn
    y (str) ... takes a string to determine which y should be plotted
    
    quakes (list of str, optional) ... takes a list of string in the format 'hh:mm:ss' and draws vertical, dashed lines at those timestamps
	quakeslabel (str, optional) ... takes a str and uses it as a label for the quakes if a legend is used
	quakecolor (str, optional) ... changes the color of the quakes, default-"tab:purple"
	color (str, optional) ... changes the color of the plot, default-"tab:orange"
	plotlabel (str, optional) ... changes label of the plot (used for legend) into the given string. If none is given, default-"no label"
	ylabel (str, optional) ... changes the label of the y axis, if no ylabel is given it will say the Type of Value that is plotted and which Unit it uses
	secondary (bool, optional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False
	setday (str, optional) ... takes a string in the format "ddmmyy" and changes the date to it
	
1.2.3 OPC.heatmap(ax,**kwargs)

    plots a dndlogdp heatmap over an existing mpl axis
    
    ax ... (Axes object of mpl.axes module) ... axis on which the plot should be drawn
    
    ylabel (str, optional) ... changes the label of the y-axis, if no ylabel is give it will say "dN/dlogDp in ccm^-3"
    orientation (str, optional) ... takes a str to change the orientation of the colorbar, default - "horizontal"
	location (str, optional) ... takes a str to change the location of the colorbar relative to the plot, default-"top"
	pad (float, optional) ... takes a float and moves the cbar further away from the heatmap the higher the pad is, default-0
	cbar (str, optional) ... decides which colormap should be used, default-"RdYlBu_r"
	
1.2.4 OPC.dndlogdp(ax, **kwargs)

    plots a bar plot of the average dndlogdp numbe size distribution
    
    ax ... (Axes obj of mpl.axes module)
    
    start (str, optional) ... takes a str of the form "HH:MM:SS" and only uses data acquired after this time for the average distribution
    end (str, optional) ... takes a str of the form "HH:MM:SS" and only uses data acquired before this time for the average distribution
    logy (bool, optional) ... if True, only the y axis is scaled logarithmicly, default-False
    ylabel (str, optional) ... changes the label of the y-axis, if no ylabel is give it will say "dN/dlogDp in ccm^-3"
    scatter (bool, optional) ... if True, the plot will be a scatter plot rather than a bar plot, default-False


2.    fluoreszenz.py


2.1   FData(file) 

	creates an FData-object

	file (str) ... takes an FSpec-produced csv-file

	title (str, optional) ... takes a str and uses it as a title for quickplots
	encoding_artifacts (bool, optional) ... takes a boolean to determine if there are encoding artifacts that need to be removed, default-True
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	skiprows (int, optional) ... takes an int and skips the first rows (may be used if the first rows are corrupted), default-0
	layout (list,optional) ... decides which columns from the csv should be taken (Syntax: [firstcolumn,lastcolumn]), default-[3,18]
        Layout-Lookuptable:
            FlyingFlo 1.0 (Peter) ... [3,18]
            FlyingFlo 2.0 (Vanessa) ... [3,18]

2.1.1 FData.internalbg(startmeasurementtime)

	takes data before startmeasurementtime-timestamp and treats it as bg to correct the data after it (crops bg in the process)

	startmeasurementtime (str) ... Takes a str in 'hh:mm:ss'-format and uses it to split the data from the bg

	bgcrop (int,optional) ... Takes an int and crops the start of the background by its amount datapoints

2.1.2 FData.externalbg(bgfile)

	takes data from another file and treats it as bg to correct the data from the FData-object

	bgfile (str) ... Takes a FSpec-produced csv-file

	startcrop (int,optional) ... Takes an int and crops the start of the background by its amount datapoints
	endcrop (int,optional) ... Takes an int and crops the end of the background by its amount datapoints

2.1.3 FData.quickplot(channelno)

	draws a plot of the intensity of the given channel vs time

	channelno (int) ... decides which channel should be plotted

	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount datapoints
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount datapoints

2.1.4 FData.plot(channelno,ax)

	draws a plot of the intensity of the given channel vs time on an existing matplotlib-axis

	channelno (int) ... decides which channel should be plotted
	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn

	quakes (list of str, optional) ... takes a list of string in the format 'hh:mm:ss' and draws vertical, dashed lines at those timestamps
	quakeslabel (str, optional) ... takes a str and uses it as a label for the quakes if a legend is used
	quakecolor (str, optional) ... changes the color of the quakes, default-"tab:purple"
	color (str, optional) ... changes the color of the plot, default-"tab:green"
	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount datapoints
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount datapoints

2.1.5 FData.crop(startcrop,endcrop)

	Shouldn't be used any more, use start and end in init (see 2.1)
	crops the data by startcrop datapoints at the start and endrop datapoints at the end

	startcrop (int) ... Takes an int and crops the beginning of the plot by its amount datapoints
	endcrop (int) ... Takes an int and crops the end of the plot by its amount datapoints
	
2.1.6 FData.quickheatmap()

    draws a heatmap of fluorescence intensity over all channels
    
2.1.7 FData.heatmap(ax,**kwargs)

    draws a heatmap of fluorescence intensity over all channels on an existing mpl-axis
    
    ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
    
    smooth (bool) ... decides if heatmap should be smoothed (gouraud) or show raw data, default-True
    cmap (str) ... decides which colormap should be used, default-"RdYlBu_r"
    pad (float) ... moves the colormap away from the axis, default-0
    togglecbar (bool) ... toggles colorbar, default-True
    xlims (list of str) ... takes 2 strings in "H:M:S"-format and uses them as xlims

2.2   NewFData(file,bg_file,**kwargs)

    creates a NewFData-object (forced trigger mode)
    In contrast to FData all data is represented using Fluorescence Index, which is calculated using all the counts within a second whose fluorescence is higher than mean + std * sigma of the background and normalized by the measurement_frequency
    
    file (str) ... takes a Fspec produced .csv-file or a .fspec-file (if a .fspec-file is given, every other argument will be ignored)
    bg_file (str) ... takes a FSpec-produced .csv-file or a .fspec-file
    
    sigma (float) ... decides when a count differs from background (similar to WIBS), default-CCS811
    measurement_frequency (int) ... if none is given, it uses calculates it
    start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
    end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
    jit (bool, optional) ... decides if Numba JIT-compiler should be used, default-True
    bg_start (str,optional) ... only uses data from bg_file which was acquired after bg_start (only works if a csv-bg_file is used, format:"HH:MM:SS")
    bg_end (str,optional) ... only uses data from bg_file which was acquired before bg_start (only works if a csv-bg_file is used, format:"HH:MM:SS")
    layout (list,optional) ... decides which columns from the csv should be taken (Syntax: [firstcolumn,lastcolumn]), default-[3,18]
        Layout-Lookuptable:
            FlyingFlo 1.0 (Peter) ... [3,18]
            FlyingFlo 2.0 (Vanessa) ... [3,18]
	
2.2.1 NewFData.save(filename,**kwargs)

    saves the NewFData-object as an .fspec-file
    
    file(str) ... filename
    
    start (str,optional) ... takes a str in 'hh:mm:ss'-format and only saves data acquired after that timestamp
    end (str,optional) ... takes a str in 'hh:mm:ss'-format and only saves data acquired before that timestamp
	
2.2.2 NewFData.quickplot(channelno)

    draws the Fluorescence Index of one channel over time
    
    channelno (int) ... decides which channel should be plotted
    
2.2.3 NewFData.quickheatmap()

    draws a heatmap of all channels over time

2.2.4 NewFData.plot(channelno,ax,**kwargs)

    draws the Fluorescence Index of one channel over time on an existing axis
    
    channelno (int) ... decides which channel should be plotted
    ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
    
    quakes (list of str, optional) ... takes a list of string in the format 'hh:mm:ss' and draws vertical, dashed lines at those timestamps
    quakeslabel (str, optional) ... takes a str and uses it as a label for the quakes if a legend is used
    quakecolor (str, optional) ... changes the color of the quakes, default-"tab:purple"
    color (str, optional) ... changes the color of the plot, default-"tab:green"
    
2.2.5 NewFData.meanplot(ax,**kwargs)

    draws the mean Fluorescence Index (over all or some channels) over time on an existing axis
    
    ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
    
    min_ch (int, optional) ... all channels lower than this wont be taken into account for calculating the mean, default-1
    max_ch (int, optional) ... all channels bigger than this wont be taken into account for calculating the mean, default-16
    quakes (list of str, optional) ... takes a list of string in the format 'hh:mm:ss' and draws vertical, dashed lines at those timestamps
    quakeslabel (str, optional) ... takes a str and uses it as a label for the quakes if a legend is used
    quakecolor (str, optional) ... changes the color of the quakes, default-"tab:purple"
    color (str, optional) ... changes the color of the plot, default-"tab:green"
    rolling (int, optional) ... if a positive int is given, the plot will show the rolling average of rolling values, default-0
    
2.2.6 NewFData.heatmap(ax,**kwargs)

    draws a heatmap of all channels over time on an existing axis
    
    ax (axis) ... takes a matplotlib-axis, on which the heatmap will be drawn

    smooth (bool) ... decides if heatmap should be smoothed (gouraud) or show raw data, default-True
    cmap (str) ... decides which colormap should be used, default-"RdYlBu_r"
    pad (float) ... moves the colormap away from the axis, default-0
    togglecbar (bool) ... toggles colorbar, default-True
    xlims (list of str) ... takes 2 strings in "H:M:S"-format and uses them as xlims
    
2.2.7 NewFData.returndata()

    returns a dict of all data
    

3.    lowcostsensors.py


3.1   CCS811(file)

	creates a CCS811-object

	file (str) ... takes a ccs811-produced csv-file
	
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	title (str, optional) ... takes a str and uses it as a title for quickplots
	deviate (bool, optional) ... takes a bool to decide if the data should be expressed relative to mean, default-False

3.1.1   CCS811.plot(ax,y)

	draws a plot of tvoc vs time or co2 vs time on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	y (str) ... determines which plot should be drawn (legal strings: 'tvoc','co2')

	color (str, optional) ... changes the color of the plot, default-"tab:brown"
	secondary (bool, oprional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False
	
3.1.2   CCS811.quickplot()
	
	draws a plot of tvoc vs time
	
3.1.3   CCS811.findplot(y)
	
	matches the given str with the correct data and returns it
	
	y (str) ... plottype (legal strings: 'tvoc','co2')
	
3.1.4   CCS811.average()
	
	averages all the data minutewise

3.1.5   CCS811.returndata(y)

	returns a list of the data y
	
3.1.6   CCS811.deviatefrommean()

	changes all values to be expressed relative to the mean
	
3.2   SEN55(file)

	creates a SEN55-object

	file (str) ... takes a sen55-produced csv-file
	
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	title (str, optional) ... takes a str and uses it as a title for quickplots
	deviate (bool, optional) ... takes a bool to decide if the data should be expressed relative to mean, default-False

3.2.1   SEN55.plot(ax,y)

	draws a plot of tvoc vs time or co2 vs time on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	y (str) ... determines which plot should be drawn (legal strings: 'pm1','pm25','pm4','pm10','temp','hum')

	color (str, optional) ... changes the color of the plot, default-"tab:red"
	secondary (bool, optional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False
	
3.2.2   SEN55.quickplot()
	
	draws a plot of pm25 vs time
	
3.2.3   SEN55.findplot(y)
	
	matches the given str with the correct data and returns it
	
	y (str) ... plottype (legal strings: 'pm1','pm25','pm4','pm10','temp','hum')
	
3.2.4   SEN55.average()
	
	averages all the data minutewise

3.2.5   SEN55.returndata(y)

	returns a list of the data y
	
3.2.6   SEN55.deviatefrommean()

	changes all values to be expressed relative to the mean
	
3.3   FlyingFlo_USB(file, kwargs)
    
	creates a FlyingFlo_USB object
    
    file (str) ... takes a FlyingFlo_USB-produced csv-file
    
    start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
    end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
    title (str, optional) ... takes a str and uses it as a title for quickplots
    deviate (bool, optional) ... takes a bool to decide if the data should be expressed relative to mean, default-False 
   
    FlyingFlo_USB.title (str) ... Title used for quickplots
    FlyingFlo_USB.deviated (bool) ... Stores if the data is expressed relative to mean
    FlyingFlo_USB.t (np.array of dt.datetime) ... Time array
    FlyingFlo_USB.y (dict of str : [np.array,str,str]) ... Dictionary with Datatypes as keys storing lists in the form of [data-array, full data name, unit]

3.3.1 FlyingFlo_USB.quickplot(y)

    draws a plot y vs time
    
    y (str) ... plottype

3.3.2 FlyingFlo_USB.plot(ax,y,kwargs)

    draws a plot of y time on an existing matplotlib-axis
    
    ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
    y (str) ... determines which plot should be drawn (legal strings: 'pm1','pm25','pm4','pm10','tempbme','humbme','gas','co2','tvoc','press','humsen','tempsen','vocsen','nox') (up to v0.1.2.1 some were different: 'temp_bme', 'hum_bme', 'temp_sen', 'hum_sen', 'voc_sen')
    
    color (str, optional) ... changes the color of the plot, default-"tab:brown"
    secondary (bool, optional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False 
   
3.3.3 FlyingFlo_USB.average()  

	averages all the data minutewise
	
3.3.4 FlyingFlo_USB.deviatefrommean() 

	changes all values to be expressed relative to the mean
	
3.3.5 FlyingFlo_USB.returndata()

   returns a dict of all data
   

4.    drone.py


4.1   Dronedata(file)

	creates a Dronedata-object

	file (str) ... takes a drone-produced csv-file

4.1.1   Dronedata.plot(ax)

	draws a plot of data vs time on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	
	y (str) ... decides which data should be drawn (height,lat,long,ws), default - height
	color (str, optional) ... changes the color of the plot, default-"tab:purple"
	secondary (bool, optional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False
	
4.1.2   Dronedata.flightmap()
	
	opens your flight in openstreetmap in the browser with colors indicating height
	
	zoomstart (int, optional) ... changes the zoomlevel of the map (can be further changed manually once the map is opened), default-21 
	colors (list of strings, optional) ... changes the colors for the height colormap, default-("brown","blue","white")
	
4.1.3   Dronedata.append()	
	
	takes another Dronedata-Object and appends its data to the first one to create one object that contains all data
	
	obj (Dronedata-obj) ... takes a Dronedata-Object whichs data should be appended
	
4.2     DroneWrapper(file,kwargs)

    creates a DroneWrapper object
    
    file (str) ... takes a Drone produced csv file
    
    dronetype (str, optional) ... specifies which drone was used to read csv correctly (currently implemented: "BladeScapes","Own") - default: "BladeScapes"
    start (str, optional) ... if a str of the form "HH:MM:SS" is given, all data acquired before this timestamp wont be used
    end (str, optional) ... if a str of the form "HH:MM:SS" ist given, all data acquired after this timestamp wont be used

4.2.1   DroneWrapper.wrap(name,obj,kwargs)

    adds an instance of a data class (Pops,NewFData or FlyingFlo_USB) to the DroneWrapper
    
    name (str) ... name that is used to find the data from the wrapped object   
    obj (Pops|NewFData|FlyingFlo_USB) ... obj that should be wrapped

4.2.2   DroneWrapper.returndata(kwargs)

    returns a dict of the Drone-produced data or all the Drone data and all the wrapped data if nested=True
    
    nested (bool, optional) ... if nested, the wrapped data of other objects is also returned

4.2.3   DroneWrapper.flightmap(kwargs)

    plots the height AGL of the drone over an OSM Map in your browser
    
    zoomstart (int, optional) ... decides on which zoomlevel the map should be rendered (can be changed while using the map by turning the mousewheel) - default: 21
    colors (list of str, optional) ... changes the color used for the colormap - default: ["brown","white","blue"]

4.2.5   DroneWrapper.advancedflightmap(y,kwargs)

    plots data of any wrapped obj over an OSM Map in your browser
    
    y (str) ... decides which data should be plotted. Takes str in the form of name_yy where name is the name of a wrapped obj (or "Drone" if data from the drone is used) and yy is a plottype (must be legal for the class the wrapped obj is an instance of)
    
    zoomstart (int, optional) ... decides on which zoomlevel the map should be rendered (can be changed while using the map by turning the mousewheel) - default: 21
    colors (list of str, optional, optional) ... changes the color used for the colormap - default: ["brown","white","blue"]
    target_height (int|float, optional) ... if a target height is given, only data in the height-range of target_height+-height_deviation is plotted
    height_deviation (int|float, optional) ... specifies the range for the target height (only usefull if a target_height is given) - default: 1
    bettermap (bool, optional) ... if True a grid of the values is calculated and plotted instead of single datapoints
    bettermap_resolution (int, optional) ... only usefull if bettermap=True. A grid of bettermap_resolution x bettermap_resolution will be used to plot the data - default: 15
    mapimage (str, optional) ... draws a picture on the map. The str must contain a path to a file without a file ending, but a .png and a .tfw have to exist. e.g mapimage="mypath/myfilename" to import mypath/myfilename.png and mypath/myfilename.tfw
    save_loc (str, optional) ... if a path (with filename) is given, the map will be saved as an .html rather than printed in the browser

4.2.6   DroneWrapper.plot(ax,y,**kwargs)

    plots Drone-produced data over time on an mpl-axis
    
    ax (mpl-axis) ... takes a mpl-axis on which the data will be plotted
    y (str) ... decides which data will be plotted (legal: "height", "long", "lat")
    
    quakes (list of str, optional) ... takes a list of "HH:MM:SS"-strings and draws vertical lines at these times
    quakeslabel (str, optional) ... a label that is used for the quakes if a legend is drawn
    quakecolor (str, optional) ... decides the color of the quake-lines - default: "tab:purple"
    color (str, optional) ... decides the color of the plot - default: "tab:green"
    plotlabel (str, optional) ... a label that is used for the plot if a legend is drawn
    ylabel (str, optional) ... a label that is used for the y-axis, if none is given it will be "value in unit", where value and unit are retrieved from the given y
    secondary (bool, optional) ... if True the plot will be drawn on the right y-axis - default: False
    masknan (bool, optional) ... if True NaN values are masked out to draw a uninterupted plot - default: True
    targetfunc (func, optional) ... decides how to check target1, target2 and targety (only works if these variables are given). the function must take two floats and an np array of floats and it must output an array of bools (mask) Default:
                                            ```python
                                            def targetfunc(target1,target2,ty): #ty is the data corresponding to targety
                                                m = np.where(target1<ty,True,False)
                                                m = np.where(ty<target2,m,False)
                                                return m
                                            ```
    target1 (float, optional) ... takes a value that is checked in targetfunc
    target2 (float, optional) ... takes a value that is checked in targetfunc
    targety (str, optional) ... takes a legal y-string (depends on wrapped objects) and hands the corresponding data to targetfunc

4.2.7   DroneWrapper.advancedplot(ax,x,y,kwargs)

    ax (mpl-axis) ... takes a mpl-axis on which the data will be plotted
    y (str) ... decides which data should be plotted. Takes str in the form of name_yy where name is the name of a wrapped obj (or "Drone" if data from the drone is used) and yy is a plottype (must be legal for the class the wrapped obj is an instance of)
    x (str) ... decides over which data should be plotted. Takes str in the form of name_yy where name is the name of a wrapped obj (or "Drone" if data from the drone is used) and yy is a plottype (must be legal for the class the wrapped obj is an instance of; if the plot should be over time use "name_t")
    
    color (str, optional) ... decides the color of the plot - default: "tab:green"
    plotlabel (str, optional) ... a label that is used for the plot if a legend is drawn
    xlabel (str, optional) ... a label that is used for the x-axis, if none is given it will be "value in unit", where value and unit are retrieved from the given x
    ylabel (str, optional) ... a label that is used for the y-axis, if none is given it will be "value in unit", where value and unit are retrieved from the given y
    scatter (bool, optional) ... if True the data is plotted as a scatterplot - default: False
    secondary (bool, optional) ... if True the plot will be drawn on the right y-axis - default: False
    masknan (bool, optional) ... if True NaN values are masked out to draw a uninterupted plot - default: True
    showpearsonr (bool, optional) ... if True Pearsons R is calculated and shown in the plot - default: True
    targetfunc (func, optional) ... decides how to check target1, target2 and targety (only works if these variables are given). the function must take two floats and an np array of floats and it must output an array of bools (mask) Default:
                                            ```python
                                            def targetfunc(target1,target2,ty): #ty is the data corresponding to targety
                                                m = np.where(target1<ty,True,False)
                                                m = np.where(ty<target2,m,False)
                                                return m
                                            ```
    target1 (float, optional) ... takes a value that is checked in targetfunc
    target2 (float, optional) ... takes a value that is checked in targetfunc
    targety (str, optional) ... takes a legal y-string (depends on wrapped objects) and hands the corresponding data to targetfunc
   
4.2.8 DroneWrapper.save(filename)

    saves the DroneWrapper object as a .flight file
    
    filename (str) ... determines the filename of the outputted file
    
4.2.9 DroneWrapper.returntarget(y,**kwargs)

    returns target array
    
    y (str) ... decides which data should be returned
    
    targetfunc (func, optional) ... decides how to check target1, target2 and targety (only works if these variables are given). the function must take two floats and an np array of floats and it must output an array of bools (mask) Default:
                                            ```python
                                            def targetfunc(target1,target2,ty): #ty is the data corresponding to targety
                                                m = np.where(target1<ty,True,False)
                                                m = np.where(ty<target2,m,False)
                                                return m
                                            ```
    target1 (float, optional) ... takes a value that is checked in targetfunc
    target2 (float, optional) ... takes a value that is checked in targetfunc
    targety (str, optional) ... takes a legal y-string (depends on wrapped objects) and hands the corresponding data to targetfunc

	
6.    wibs.py

6.1   WIBS(file,FT_file,**kwargs)

    creates a WIBS-object
    
    file (str or list of str) ... Either the path to a wibs produced .h5 file or to a preprocessed .wibs file or a list of paths to wibs produced .h5 files.
    FT_file (str) ... Path to a wibs produced forcedtrigger-file. Can be left if a preprocessed .wibs file is passed as file
    FT_time (str) ... String in the form of 'hh:mm:ss' of the time when the forced trigger was started, which is used to correct the time. Can be left if a preprocessed .wibs file is passed as file.
    
    FT_sigma (int or float, optional) ... Will be used as sigma for data processing, default-3
    bin_borders (list of int, optional) ... Particles will be classified according to the bins given here (in micrometers), default-[0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,1.7,2,2.5,3,3.5,4,5,10,15,20]
    flow (float,optional) ... Flow in ccm/s. Will be used to calculate partconc and dndlogdp, default-0.018
    fixed (list of float with len=3, optional) ... If fixed is passed, the values will be treated as bg and FT_file will only be used for time correction
    start (str, optional) ... String in the form 'hh:mm:ss'. If start is given, all data acquired before this timestamp will be ignored
    end (str, optional) ... String in the form 'hh:mm:ss'. If end is given, all data acquired after this timestamp will be ignored
    FT_date (str, optional) ... Sets the FT_time to be this date (str format: 'dd.mm.yyyy'), only relevant if the data is going to be compared with other data, default-'01.01.2000'
    channels (list of str, optional) ... Decides which channels should be processed, by default all channels are processed, but it can be reduced for large files (give [] if no channels should be processed). default - ["a","b","c","ab","ac","bc","abc"]
    
6.1.1   WIBS.quickplot(y)

    draws a plot of y vs time
    
    y (str) ... decides which variable y should be plotted
    
6.1.2   WIBS.quickheatmap(y)

    draws a heatmap of y
    
    y (str) ... decides which variable y should be plotted
    
6.1.3   WIBS.heatmap(ax,y,**kwargs)

    Draws a dndlogdp number size distribution heatmap over an existing mpl axis
    
    ax (Axes obj of mpl.axes module) ... takes a matplotlib-axis, on which the graph will be drawn
    y (str) ... decides which variable y should be plotted
    
    cmap (str, optional) ... decides which colormap should be used, default-"RdYlBu_r"
    pad (int or float, optional) ... moves the colormap away from the axis, default-0
    togglecbar (bool, optional) ... toggles colorbar, default-True
    orientation (str, optional) ... changes the colorbars orientation, default-'horizontal'
    location (str, optional) ... changes the colorbars location, default-'top'
    
6.1.4   WIBS.plot(ax,y,**kwargs)

    draws a plot of y on an existing mpl-axis
    
    ax (Axes obj of mpl.axes module) ... takes a matplotlib-axis, on which the graph will be drawn
    y (str) ... decides which variable y should be plotted
    
    label (str,optional) ... gives the plot a label used in a legend, default-'no label'
    color (str, optional) ... changes the color of the plot, default-"tab:purple"
    secondary (bool, optional) ... should be toggled if the plot uses the right-hand yaxis, default-False
    
6.1.5   WIBS.save(path)

    Saves the obj as a preprocessed .wibs file
    
    path (str) ... Determines the path and name, where the .wibs file should be saved


7.    weather.py

7.1   WeatherData(file)

    creates a WeatherData-object
    
    file (str) ... takes a csv-file created by the weatherstation
    
7.1.1 WeatherData.plot(ax,y,**kwargs)

    draws a plot of y on an existing mpl-axis
    
    y (str) ... decides which data should be plotted
    ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
    
    day (str, optional) ... takes a day in the format ddmmyyyy. If a day is given only data acquired on that day will be plotted
    setday (str, optional) ... takes a day in the format ddmmyyyy. If a setday is given all data will be changed to this day to make it easier to plot against other data
    start (str, optional) ... takes a timestamp in the format HHMMSS. if a start is given only data acquired after that timestamp will be plotted
    end (str, optional) ... takes a timestamp in the format HHMMSS. if a end is given only data acquired before that timestamp will be plotted
    secondary (bool, optional) ... if True the plot will be drawn on the right y-axis. The default is False
    color (str, optional) ... decides the color of the plot. The default is "tab:blue"
    plotlabel (str, optional) ... a label that is used for the plot if a legend is drawn. The default is "no label"
    ylabel (str,optional) ... a label that is used for the y-axis, if none is given it will be "value in unit", where value and unit are retrieved from the given y