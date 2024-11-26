1.    pops.py:


1.1   Pops(file)

	creates a Pops-Object
	
	file (str) ... Takes a POPS-produced csv-file (eg '112233.csv')

	title (str,optional) ... Takes a str and uses it as a title for quickplots
	start (str,optional) ... Takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... Takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	bgobj (Pops,optional) ... Takes another Pops-Object and corrects the data using the given Pops-Objects as Background
	box (bool,optional) ... Takes a Boolean to determine which file is given (True ... produced by the box;False ... produced by the POPS hooked to a laptop) default-True
	timecorr (int,optional) ... Takes an int and corrects popstime by it, default-23
	relobj(Pops,optional) ... Takes a Pops object and displays all data as relative to the mean of it (see 1.22)
	deviate(bool,optional) ... decides if values should be expressed as relatives to mean, default-False

1.2   Pops.internalbg(startmeasurementtime)

	shouldn't be used since there is the more flexible method to import a bgobj (see 1.1)
	takes data before startmeasurementtime-timestamp and treats it as bg to correct the data after it (crops bg in the process)

	startmeasurementtime (str) ... Takes a str in 'hh:mm:ss'-format and uses it to split the data from the bg

	bgcrop (int,optional) ... Takes an int and crops the start of the background by its amount seconds

1.3   Pops.externalbg(bgfile)

	shouldn't be used since there is the more flexible method to import a bgobj (see 1.1) and this function isn't compatible with data sampled using the POPS and a laptop
	takes data from another file and treats it as bg to correct the data from the Pops-object

	bgfile (str) ... Takes a POPS-produced csv-file (zB '112233.csv')

	startcrop (int,optional) ... Takes an int and crops the start of the background by its amount seconds
	endcrop (int,optional) ... Takes an int and crops the end of the background by its amount seconds 

1.4   Pops.exportbg()

	treats the data from the Pops-file as bg and returns the bg in the format [[ch0-ch15],total]
	can be used, however the method to import a bgobj (see 1.1) is better

1.5   Pops.importbg(bg)

	uses data in the format [[ch0-ch15],total] and corrects the Pops-objects data by it
	just use the method to import a bgobj, trust me it's better (see 1.1)

	bg (nested list of floats) ... Takes a list containing the data for bg-correction 

1.6   Pops.quickplot(y)

	draws a plot y vs time

	y (str) ... takes a string to determine which y should be plotted (for accepted strings see 1.16)

	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount seconds
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount seconds

1.7   Pops.plot(ax,y)

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

1.8   Pops.quickheatmap()

	draws a dndlogdp-heatmap over time 

	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount seconds
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount seconds

1.9   Pops.heatmap(ax)

	draws a dndlogdp-heatmap over time on an existing matplotlib-axis
	
	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn

	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount seconds
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount seconds
	togglexticks (bool, optional) ... takes a boolean to decide if the x-ticks of ax should be visible, default-True
	orientation (str, optional) ... takes a str to change the orientation of the colorbar, default - "horizontal"
	location (str, optional) ... takes a str to change the location of the colorbar relative to the plot, default-"top"
	togglecbar (bool, optional) ... takes a bool to determine if the cbar should be drawn, default-True
	pad (float, optional) ... takes a float and moves the cbar further away from the heatmap the higher the pad is, default-0
	
1.10  Pops.dndlogdp(ax)

	draws a barplot of dndlogdp-distribution on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn

1.11  Pops.quickdndlogdp()

	draws a barplot of dndlogdp-distribution

1.12  Pops.cumulativeparticles()

	prints and returns the sum of the means of all bins
	no real usecase, was used before "total"-channel was implemented

1.13  Pops.crop(startcrop,endcrop)

	Shouldn't be used any more, use start and end in init (see 1.1)
	crops the data by startcrop seconds at the start and endrop seconds at the end

	startcrop (int) ... Takes an int and crops the beginning of the plot by its amount seconds
	endcrop (int) ... Takes an int and crops the end of the plot by its amount seconds

1.14  Pops.stats(y)

	prints mean, std and var of the given data to the console

	y (str) ... takes a string to determine which y should be plotted (for accepted strings see 1.16)

1.15  Pops.returnstats(y)

	return mean, std and var of the given data in the format [mean,std,var]

	y (str) ... takes a string to determine which y should be plotted (for accepted strings see 1.16)

1.16  Pops.findplot(y)

	matches the given str with the correct data and returns [xdata,ydata,label,ylabel]

	y (str) ... takes a string to determine which y should be plotted 

	Accepted strings: temp_bme680, hum_bme680, temp_sen55, hum_sen55, druck, gas, pm1, pm25, pm4, pm10, voc, nox, co2, tvoc, popstemp, boardtemp, total, pops_pm25, pops_underpm25, every other str containing one of the numbers 0-15 will be interpreted as a bin

1.17  Pops.replacezeros(data)

	inputs data and replaces every 0 with the lowest value in the data
	is used to avoid blank spots in the heatmap, apart from that no reasonable usecase

	data (nested list of floats) ... input data array
	
1.18  Pops.append(obj)
	
	takes another Pops-Object and appends its data to the first one to create one object that contains all data 
	
	obj (Pops-obj) ... takes a Pops object whichs data should be appended
	
1.19  Pops.add(obj)	
	
	takes another Pops-Object and returns a new Pops-Object containing data of both objects without changing them 
	
	obj (Pops-obj) ... takes a Pops object whichs data should be appended
	
1.20  Pops.average()
	
	averages all the data minutewise

1.21  Pops.returndata(y)

	returns a list of the data y
	
1.22  Pops.relativevals(bgobj)

	changes all data to relative to the mean of the bgobj
	
	bgobj (Pops-obj) ... takes a Pops object to whichs mean data should be relative to
	
1.23  Pops.deviatefrommean()

	changes all values to be expressed relative to the mean
	
1.24  Pops.newheatmap(ax)

	creates a heatmap with consistant y-increments on an existing axis
	
	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	
	orientation (str, optional) ... takes a str to change the orientation of the colorbar, default - "horizontal"
	location (str, optional) ... takes a str to change the location of the colorbar relative to the plot, default-"top"
	pad (float, optional) ... takes a float and moves the cbar further away from the heatmap the higher the pad is, default-0


2.    fluoreszenz.py


2.1   FData(file) 

	creates an FData-object

	file (str) ... takes an FSpec-produced csv-file

	title (str, optional) ... takes a str and uses it as a title for quickplots
	encoding_artifacts (bool, optional) ... takes a boolean to determine if there are encoding artifacts that need to be removed, default-True
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	skiprows (int, optional) ... takes an int and skips the first rows (may be used if the first rows are corrupted), default-0

2.2   FData.internalbg(startmeasurementtime)

	takes data before startmeasurementtime-timestamp and treats it as bg to correct the data after it (crops bg in the process)

	startmeasurementtime (str) ... Takes a str in 'hh:mm:ss'-format and uses it to split the data from the bg

	bgcrop (int,optional) ... Takes an int and crops the start of the background by its amount datapoints

2.3   FData.externalbg(bgfile)

	takes data from another file and treats it as bg to correct the data from the FData-object

	bgfile (str) ... Takes a FSpec-produced csv-file

	startcrop (int,optional) ... Takes an int and crops the start of the background by its amount datapoints
	endcrop (int,optional) ... Takes an int and crops the end of the background by its amount datapoints

2.4   FData.quickplot(channelno)

	draws a plot of the intensity of the given channel vs time

	channelno (int) ... decides which channel should be plotted

	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount datapoints
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount datapoints

2.5   FData.plot(channelno,ax)

	draws a plot of the intensity of the given channel vs time on an existing matplotlib-axis

	channelno (int) ... decides which channel should be plotted
	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn

	quakes (list of str, optional) ... takes a list of string in the format 'hh:mm:ss' and draws vertical, dashed lines at those timestamps
	quakeslabel (str, optional) ... takes a str and uses it as a label for the quakes if a legend is used
	quakecolor (str, optional) ... changes the color of the quakes, default-"tab:purple"
	color (str, optional) ... changes the color of the plot, default-"tab:green"
	startcrop (int, optional) ... Takes an int and crops the beginning of the plot by its amount datapoints
	endcrop (int, optional) ... Takes an int and crops the end of the plot by its amount datapoints

2.6   FData.crop(startcrop,endcrop)

	Shouldn't be used any more, use start and end in init (see 2.1)
	crops the data by startcrop datapoints at the start and endrop datapoints at the end

	startcrop (int) ... Takes an int and crops the beginning of the plot by its amount datapoints
	endcrop (int) ... Takes an int and crops the end of the plot by its amount datapoints


3.    ccs811.py


3.1   CCS811(file)

	creates a CCS811-object

	file (str) ... takes a ccs811-produced csv-file
	
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	title (str, optional) ... takes a str and uses it as a title for quickplots
	deviate (bool, optional) ... takes a bool to decide if the data should be expressed relative to mean, default-False

3.2   CCS811.plot(ax,y)

	draws a plot of tvoc vs time or co2 vs time on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	y (str) ... determines which plot should be drawn (legal strings: 'tvoc','co2')

	color (str, optional) ... changes the color of the plot, default-"tab:brown"
	secondary (bool, oprional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False
	
3.3   CCS811.quickplot()
	
	draws a plot of tvoc vs time
	
3.4   CCS811.findplot(y)
	
	matches the given str with the correct data and returns it
	
	y (str) ... plottype (legal strings: 'tvoc','co2')
	
3.5   CCS811.average()
	
	averages all the data minutewise

3.6   CCS811.returndata(y)

	returns a list of the data y
	
3.7   CCS811.deviatefrommean()

	changes all values to be expressed relative to the mean


4.    drone.py


4.1   Dronedata(file)

	creates a Dronedata-object

	file (str) ... takes a drone-produced csv-file

4.2   Dronedata.plot(ax)

	draws a plot of data vs time on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	
	plot (str) ... decides which data should be drawn (height,lat,long,ws), default - height
	color (str, optional) ... changes the color of the plot, default-"tab:purple"
	secondary (bool, optional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False
	
4.3   Dronedata.flightmap()
	
	opens your flight in openstreetmap in the browser with colors indicating height
	
	zoomstart (int, optional) ... changes the zoomlevel of the map (can be further changed manually once the map is opened), default-21 
	colors (list of strings, optional) ... changes the colors for the height colormap, default-("brown","blue","white")
	
4.4   Dronedata.append()	
	
	takes another Dronedata-Object and appends its data to the first one to create one object that contains all data
	
	obj (Dronedata-obj) ... takes a Dronedata-Object whichs data should be appended


5.    sen55.py


5.1   SEN55(file)

	creates a SEN55-object

	file (str) ... takes a sen55-produced csv-file
	
	start (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired after that timestamp
	end (str,optional) ... takes a str in 'hh:mm:ss'-format and only imports data acquired before that timestamp
	title (str, optional) ... takes a str and uses it as a title for quickplots
	deviate (bool, optional) ... takes a bool to decide if the data should be expressed relative to mean, default-False

5.2   SEN55.plot(ax,y)

	draws a plot of tvoc vs time or co2 vs time on an existing matplotlib-axis

	ax (axis) ... takes a matplotlib-axis, on which the graph will be drawn
	y (str) ... determines which plot should be drawn (legal strings: 'pm1','pm25','pm4','pm10','temp','hum')

	color (str, optional) ... changes the color of the plot, default-"tab:red"
	secondary (bool, optional) ... determines which y-axis should be colored (False-left axis/True-right axis), default-False
	
5.3   SEN55.quickplot()
	
	draws a plot of tvoc vs time
	
5.4   SEN55.findplot(y)
	
	matches the given str with the correct data and returns it
	
	y (str) ... plottype (legal strings: 'pm1','pm25','pm4','pm10','temp','hum')
	
5.5   SEN55.average()
	
	averages all the data minutewise

5.6   SEN55.returndata(y)

	returns a list of the data y
	
5.7   SEN55.deviatefrommean()

	changes all values to be expressed relative to the mean
	
	
6.    getdata.py

6.1   getdata(day,height,loc,bgstart,pops,sen55,ccs811,file,absvals)

	returns a dictionary containing lists of data-objects (Pops,SEN55,CCS811) of all flights that meet certain criteria (day,height,loc) which are specified on a lookuptable
	
	day (list of str) ... only flights on days in this list are returned (if no day is given, flights from all days are returned) - legal strings: "1106","1206","1306","1406","0807","0907","1007","1107"
	height (list of str) ... only flights on heights AGL in this list are returned (if no day is given, flights from all days are returned) - legal strings: "15","25","40","50","80"
	loc (list of str) ... only flights on locations in this list are returned (if no day is given, flights from all days are returned) - legal strings: "canopyTU","canopyVT","meadow"
	bgstart (str) ... only flight with exact bgstart is returned (can be used to filter for exact flights) - check lookuptable for legal strings
	pops (bool) ... decides if the output-dict should have an entry "pops" containing a list of Pops-obj with data relative to ground, default-True
	sen55 (bool) ... decides if the output-dict should have an entry "sen55" containing a list of SEN55-obj, default-False
	ccs811 (bool) ... decides if the output-dict should have an entry "ccs811" containing a list of CCS811-obj, default-False
	file (str) ... takes a csv-file and uses it as a lookuptable for days, heights, locs and filenames of different flights, default-"flights_lookuptable.csv" (see owncloud)
	absvals (bool) ... takes a boolean to decide if data should be expressed as absolute values rather than relative to bg, default - False
	
6.2   flightvals(day,flight,file)

	takes a day and a flightnumber and returns a list with getdata()-readable data: [day,bgstart,loc,height]
	
	day (str) ... decides the day - legal strings: "1106","1206","1306","1406","0807","0907","1007","1107"
	flight (int) ... decides which flight (assumes flights on each day are numbered 1-n) - for legal ints see lookuptable
	file (str) ... takes a csv-file and uses it as a lookuptable for days, heights, locs and filenames of different flights, default-"flights_lookuptable.csv" (see owncloud)
	
6.3   flightsummary(day,flight,y,file,ylims,averaged,absvals,title)

	takes a day and a flightnumber and draws boxplots of the data y of every height and loc on the given flight
	
	day (str) ... decides the day - legal strings: "1106","1206","1306","1406","0807","0907","1007","1107"
	flight (int) ... decides which flight (assumes flights on each day are numbered 1-n) - for legal ints see lookuptable
	y (str) ... decides which data should be shown in the boxplot - for legal strings see 1.16
	file (str) ... takes a csv-file and uses it as a lookuptable for days, heights, locs and filenames of different flights, default - "flights_lookuptable.csv" (see owncloud)
	ylims (list of int) ... takes a list of int with two entrys and uses them as ylims for the boxplot-graph, default - [-100,300]
	averaged (bool) ... if True boxplots will be drawn from minutewise averaged data instead of raw data, default - False
	absvals (bool) ... takes a boolean to decide if data should be expressed as absolute values rather than relative to bg, default - False
	title (bool) ... if True plot will get the title "date flightno y", default - True
	
6.4   means(flightlist,y,outputfilename,file)

	takes a list of linenumbers of the lookuptable and returns a list of lists in the form [[mean,rawdata],...] for each flight and saves it as /json/y/outputfilename.json
	
	flightlist(list of int) ... decides which flights (linenumbers of lookuptable) should be used
	y (str) ... decides which data should be used - for legal strings see 1.16
	outputfilename (str) ... data will be saved as outputfilename.json (to have the labeling in getdata.plotmeans() work properly files should be named name_Altitude.json, eg canopy_40.json)
	file (str) ... takes a csv-file and uses it as a lookuptable for flights, default - "flights_lookuptable.csv" (see owncloud)
	
6.5   plotmeans(jsonlist,y)

	takes a list of getdata.means()-generated .json-files and plots them
	
	jsonlist (list of str) ... imports given .json-files
	y (str) ... decides which data should be plotted - for legal strings see 1.16 (technically strings are only legal after the corresponding .json-file has been created)
	
	title (str, optional) ... if a title is given, the plot will have a title
	customlabels (list of str, optional) ... if customlabels are given they will be used as xlabels (if the jsonfiles are named in the form name_Altitude.json xlabels will be the altitudes by default)