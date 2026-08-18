# -*- coding: utf-8 -*-
"""
This Submodule provides the `WIBS` obj that can be used to read in wibs data
"""

import math
import pickle
from datetime import datetime,timezone
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md

from .ErrorHandler import IllegalValue,IllegalArgument

class WIBS:
    
    def __init__(self,file,FT_file="",FT_time="hh:mm:ss",**kwargs):
        """
        Inits the WIBS obj

        Parameters
        ----------
        file : str or list of str
            Either the path to a wibs produced .h5 file or to a preprocessed 
            .wibs file or a list of paths to wibs produced .h5 files.
        FT_file : str
            Path to a wibs produced forcedtrigger-file. Can be left if a 
            preprocessed .wibs file is passed as file.
        FT_time : str
            String in the form of 'hh:mm:ss' of the time when the forced 
            trigger was started, which is used to correct the time. Can be 
            left if a preprocessed .wibs file is passed as file.
            
        Other Parameters
        ----------------
        FT_sigma : int or float, optional
            Will be used as sigma for data processing. The default is 3.
        bin_borders : list of float, optional
            Particles will be classified according to the bins given here 
            (in micrometers). 
            The default is [0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,
                            1.7,2,2.5,3,3.5,4,5,10,15,20,100]
        flow : float, optional
            Flow in ccm/s. Will be used to calculate partconc and dndlogdp. 
            The default is 0.018 ccm/s (=0.3 lpm).
        fixed : list of floats with len 3, optional
            If fixed is passed, the values will be treated as bg and FT_file 
            will only be used for time correction.
        start : str, optional
            String in the form 'hh:mm:ss'. If start is given, all data acquired
            before this timestamp will be ignored.
        end : str, optional
            String in the form 'hh:mm:ss'. If end is given, all data acquired 
            after this timestamp will be ignored.
        FT_date : str, optional
            Sets the FT_time to be this date (str format: 'dd.mm.yyyy'), only 
            relevant if the data is going to be compared with other data. 
            The default is '01.01.2000'
        channels : list of str, optional
            Decides which channels should be processed, by default all channels
            are processed, but it can be reduced for large files. 
            The default is  ["a","b","c","ab","ac","bc","abc","nonfluor"].
            
        Attributes
        ----------
        bins : int
            Number of bins
        bin_means : list of float
            Geometric means of bins. Used for dndlogdp stuff.
        bin_borders : list of float
            The list of bin borders that is passed as a kwarg at init. It is 
            only saved as an attribute in agg_dim 0.1.18 or higher.
        data : {str : 1D numpy array}
            contains all processed data in the form of a dictionary 
            (processed for every second)
        details : {str : [str, str]}
            contains a description and the unit to each data array
        rawdata : {str : 1D numpy array}
            conains all the raw data used for data processing
        fl1_FTbg : float
            Contains the fluorescence of the chamber for fl1, calculated from 
            the forced trigger.
        fl2_FTbg : float
            Contains the fluorescence of the chamber for fl2, calculated from 
            the forced trigger.
        fl3_FTbg : float
            Contains the fluorescence of the chamber for fl3, calculated from 
            the forced trigger. 
        chunklen : int
            Time in seconds, how long a chunk is. It can be reduced to reduce
            peak RAM usage. The default is 600.
        """
        
        if file[-5:] == ".wibs":
            
            with open(file,"rb") as openfile:
                ip = pickle.load(openfile)
            
            for arg in ip.keys():
                setattr(self, arg, ip[arg])
            
            #catch legacy .wibs obj that did not save self.bin_borders
            try:
                self.bin_borders
            except AttributeError:
                msg = "Caution! The loaded .wibs file was saved before the "
                msg += "attribute 'bin_borders' was introduced. If WIBS.dndlog"
                msg += "dp() is used, you have to pass the bin borders "
                msg += "manually."
                print(msg)
                
                #default Value
                self.bin_borders = [0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,
                                    1.7,2,2.5,3,3.5,4,5,10,15,20,100]
                
        else:
        
            #import kwargs
            defaults = {
                "FT_sigma" : 3,
                "bin_borders" : [0.5,0.55,0.6,0.7,0.8,0.9,1,1.2,1.4,
                                 1.7,2,2.5,3,3.5,4,5,10,15,20,100],
                "flow" : 0.3*1000/60,
                "fixed" : None, #[float,flat,float]
                "start" : None,
                "end" : None,
                "FT_date" : "01.01.2000",
                "channels" :  ["a","b","c","ab","ac","bc","abc","nonfluor"],
                "chunklen" : 600
                }
            for key,value in defaults.items():
                self.hk_kwargs(kwargs, key, value)
            self.hk_errorhandling(kwargs, defaults.keys(), "WIBS")
            
            #setup variables
            self.bins = len(self.bin_borders)-1
            bm = [math.sqrt(self.bin_borders[i] * self.bin_borders[i+1]) 
                  for i in range(self.bins)]
            self.bin_means = bm
            self.data = {}
            self.rawdata = {}
            self.details = {} #[name,unit]
            if self.fixed is not None:
                self.fl1_FTbg = self.fixed[0]
                self.fl2_FTbg = self.fixed[1]
                self.fl3_FTbg = self.fixed[2]
                      
            #load Forced Trigger
            
            if FT_file == "":
                msg = "WIBS needs a FT_file unless preprocessed data "
                msg += "(.wibs-file) is used"
                raise KeyError(msg)
    
            try:
                ft = h5py.File(FT_file,"r")
            except Exception as exc:
                msg = "Cant find FT_file at given path"
                raise FileNotFoundError(msg) from exc
            ft2 = ft["NEO"]
            ft3 = ft2["ParticleData"]
            
            ft_xe1 = np.transpose(list(ft3["Xe1_FluorPeak"]))
            ft_xe2 = np.transpose(list(ft3["Xe2_FluorPeak"]))
            self.start_FT = datetime.fromtimestamp(
                list(ft3["Seconds"]
                     )[0],
                tz=timezone.utc).replace(
                    year=int(self.FT_date[-4:]),
                    month=int(self.FT_date[3:5]),
                    day=int(self.FT_date[:2])
                    )
            
            f = f"{self.FT_date}-{FT_time}/+0000"
            FT_time = datetime.strptime(f,"%d.%m.%Y-%H:%M:%S/%z")
            timecorr = FT_time - self.start_FT
            
            if self.fixed is None:
                f1 = ft_xe1[0]
                self.fl1_FTbg = np.nanmean(f1) + self.FT_sigma * np.nanstd(f1)
                f2 = ft_xe1[1]
                self.fl2_FTbg = np.nanmean(f2) + self.FT_sigma * np.nanstd(f2)
                f3 = ft_xe2[1]
                self.fl3_FTbg = np.nanmean(f3) + self.FT_sigma * np.nanstd(f3)
            
            
            #load file
            if isinstance(file,str):
                try:
                    f = h5py.File(file,"r")
                except Exception as exc:
                    msg = "Cant find file at given path"
                    raise FileNotFoundError(msg) from exc
                f2 = f["NEO"]
                f3 = f2['ParticleData']
                
                wibstime = list(f3["Seconds"])
                self.timehandler = np.array(wibstime).astype(np.uint32)
                
                xe1 = np.transpose(list(f3["Xe1_FluorPeak"]))
                xe2 = np.transpose(list(f3["Xe2_FluorPeak"]))
                
                self.rawdata["size"] = np.array(list(f3["Size_um"]))
                self.rawdata["excited"] = np.array(
                    list(f3["Flag_Excited"])
                    ).astype(bool)
                self.rawdata["Fl1"] = np.where(xe1[0] >= self.fl1_FTbg, 
                                               True, False)
                self.rawdata["Fl2"] = np.where(xe1[1] >= self.fl2_FTbg, 
                                               True, False)
                self.rawdata["Fl3"] = np.where(xe2[1] >= self.fl3_FTbg, 
                                               True, False)
                
    
            #load files
            elif isinstance(file,list):
    
                firstfile = True
                
                for ff in file:
                    f = h5py.File(ff,"r")
                    f2 = f["NEO"]
                    f3 = f2['ParticleData']
                    
                    filetime = list(f3["Seconds"])
                    th = np.array(filetime).astype(np.uint32)
                    
                    xe1 = np.transpose(list(f3["Xe1_FluorPeak"]))
                    xe2 = np.transpose(list(f3["Xe2_FluorPeak"]))
                    if len(xe1) == 0 or len(xe2) == 0:
                        continue
                    
                    filecounts = np.array(list(f3["Size_um"]))
                    file_excited = np.array(
                        list(f3["Flag_Excited"])
                        ).astype(bool)
                    filefl1 = np.where(xe1[0] >= self.fl1_FTbg, True, False)
                    filefl2 = np.where(xe1[1] >= self.fl2_FTbg, True, False)
                    filefl3 = np.where(xe2[1] >= self.fl3_FTbg, True, False)
                    
                    if firstfile:
                        self.timehandler = th.astype(np.uint32)
                        self.rawdata["size"] = filecounts
                        self.rawdata["excited"] = file_excited
                        self.rawdata["Fl1"] = filefl1
                        self.rawdata["Fl2"] = filefl2
                        self.rawdata["Fl3"] = filefl3
                        firstfile = False
                    else:
                        self.timehandler = np.append(
                            self.timehandler,
                            th
                            ).astype(np.uint32)
                        self.rawdata["size"] = np.append(self.rawdata["size"],
                                                         filecounts)
                        self.rawdata["excited"] = np.append(
                            self.rawdata["excited"],
                            file_excited
                            )
                        self.rawdata["Fl1"] = np.append(self.rawdata["Fl1"],
                                                        filefl1)
                        self.rawdata["Fl2"] = np.append(self.rawdata["Fl2"],
                                                        filefl2)
                        self.rawdata["Fl3"] = np.append(self.rawdata["Fl3"],
                                                        filefl3)
               
             
            if isinstance(self.start,str):
                wb_date = datetime.utcfromtimestamp(self.timehandler[0])
                f = f"{self.FT_date}-{self.start}/+0000"
                starttime = datetime.strptime(f,"%d.%m.%Y-%H:%M:%S/%z")
                starttime = int(starttime.replace(
                    year=wb_date.year,
                    month=wb_date.month,
                    day=wb_date.day
                    ).timestamp())
                if int(timecorr.total_seconds()) >= 0:
                    start_m = np.where(
                        (self.timehandler 
                         + int(timecorr.total_seconds())) > starttime, 
                        True, 
                        False
                        )
                else:
                    offset = abs(int(timecorr.total_seconds()))
                    start_m = np.where(
                        (self.timehandler - offset) > starttime, 
                        True, 
                        False
                        )
                self.timehandler = self.timehandler[start_m]
                self.rawdata["size"] = self.rawdata["size"][start_m]
                self.rawdata["excited"] = self.rawdata["excited"][start_m]
                self.rawdata["Fl1"] = self.rawdata["Fl1"][start_m]
                self.rawdata["Fl2"] = self.rawdata["Fl2"][start_m]
                self.rawdata["Fl3"] = self.rawdata["Fl3"][start_m]
                del start_m
            if isinstance(self.end,str):
                wb_date = datetime.utcfromtimestamp(self.timehandler[0])
                f = f"{self.FT_date}-{self.end}/+0000"
                endtime = datetime.strptime(f,"%d.%m.%Y-%H:%M:%S/%z")
                endtime = np.uint32(endtime.replace(
                    year=wb_date.year,
                    month=wb_date.month,
                    day=wb_date.day
                    ).timestamp())
                
                if int(timecorr.total_seconds()) >= 0:
                    end_m = np.where(
                        (self.timehandler 
                         + int(timecorr.total_seconds())) < endtime,
                        True,
                        False
                        )
                else:
                    offset = abs(int(timecorr.total_seconds()))
                    end_m = np.where((self.timehandler - offset) < endtime,
                                     True,
                                     False)
                self.timehandler = self.timehandler[end_m] 
                self.rawdata["size"] = self.rawdata["size"][end_m]
                self.rawdata["excited"] = self.rawdata["excited"][end_m]
                self.rawdata["Fl1"] = self.rawdata["Fl1"][end_m]
                self.rawdata["Fl2"] = self.rawdata["Fl2"][end_m]
                self.rawdata["Fl3"] = self.rawdata["Fl3"][end_m]
                del end_m
    
                
            #process data
            self.data["t"] = np.array(
                [datetime.utcfromtimestamp(timestamp) 
                 for timestamp in range(self.timehandler[0],
                                        self.timehandler[-1])]
                ) + timecorr
            self.date = [self.data["t"][0].day,
                         self.data["t"][0].month,
                         self.data["t"][0].year]
            
            lower=int(self.timehandler[0]//1)
            upper=lower+self.chunklen
            chunkmask=np.where(self.timehandler>=lower,True,False)
            chunkmask=np.where(self.timehandler<upper,chunkmask,False)
            chunktime = self.timehandler[chunkmask]
            chunksize = self.rawdata["size"][chunkmask]
            chunkexc = self.rawdata["excited"][chunkmask]
            chunkfl1 = self.rawdata["Fl1"][chunkmask]
            chunkfl2 = self.rawdata["Fl2"][chunkmask]
            chunkfl3 = self.rawdata["Fl3"][chunkmask]
            del chunkmask
            
            time_mask = np.array(
                [np.where(chunktime==i,True,False) 
                 for i in range(lower,upper)]
                )
                    
            #part_conc & #/s
            for bin_no in range(self.bins):
                m = np.where(self.bin_borders[bin_no] < chunksize,
                             True,
                             False)
                m = np.where(self.bin_borders[bin_no+1] > chunksize,
                             m,
                             False)
                bin_handler = time_mask & m
                self.data[f"bin{bin_no}_cps"] = np.array(
                    [np.count_nonzero(arr) for arr in bin_handler]
                    )
                del bin_handler
                pc = f"bin{bin_no}_partconc"
                cps = f"bin{bin_no}_cps"
                self.data[pc] = self.data[cps] / self.flow
                self.details[pc] = [f"Particle Conc. (bin{bin_no}) ",
                                    "#/cm${}^3$"]
                self.details[cps] = [f"Particle Counts (Bin{bin_no})","#/s"]
                
            #dndlogdp
            for bin_no in range(self.bins):
                log_binwidth = np.log10(
                    self.bin_borders[bin_no+1]
                    )-np.log10(self.bin_borders[bin_no])
                dn = f"bin{bin_no}_dndlogdp"
                pc = f"bin{bin_no}_partconc"
                self.data[dn] = self.data[pc] / log_binwidth
                self.details[dn] = [f"dN/dlog$D_P$ (Bin{bin_no})",
                                    "µm${}^{-1}$"]
                
            #total
            m = np.where(self.bin_borders[0] < chunksize,True,False)
            m = np.where(self.bin_borders[-1] > chunksize,m,False)
            total_handler = time_mask & m
            self.data["total_cps"] = np.array(
                [np.count_nonzero(arr) for arr in total_handler]
                )
            del total_handler
            self.details["total_cps"] = ["Particle Counts","#/s"]
            
            
            #excited
            ex_handler = time_mask & chunkexc
            self.data["excited"] = np.array(
                [np.count_nonzero(arr) for arr in ex_handler]
                )
            del ex_handler
            self.details["excited"] = ["Particle Counts (excited)","#/s"]
            self.data["excited_fraction"] = np.divide(
                self.data["excited"],
                self.data["total_cps"],
                out=np.ones(self.data["excited"].shape,dtype=float),
                where=self.data["total_cps"]!=0
                )
            self.details["excited_fraction"] = [
                "Fraction of excited Particles", 
                "No Unit"
                ]
            
            
            #fluorescence channels
            fl1_handler = time_mask & chunkfl1
            fl2_handler = time_mask & chunkfl2
            fl3_handler = time_mask & chunkfl3
            
            self.data["fl1"] = np.array(
                [np.count_nonzero(arr) for arr in fl1_handler]
                )/self.data["excited_fraction"]
            self.data["fl2"] = np.array(
                [np.count_nonzero(arr) for arr in fl2_handler]
                )/self.data["excited_fraction"]
            self.data["fl3"] = np.array(
                [np.count_nonzero(arr) for arr in fl3_handler]
                )/self.data["excited_fraction"]
            for i in [1,2,3]:
                self.details[f"fl{i}"] = [f"Particle Counts (Fl{i})","#/s"]
                self.details[f"fl{i}_fraction"] = [
                    f"Fluorescent Fraction (Fl{i})",
                    "No Unit"
                    ]
            
            def createmask(a,b,c,string):
                a = a if "a" in string else ~a
                b = b if "b" in string else ~b
                c = c if "c" in string else ~c
                
                op = a&b
                return op&c
            
            for channel in self.channels:
                channel_mask = createmask(fl1_handler,
                                          fl2_handler,
                                          fl3_handler,
                                          channel)
                for bin_no in range(self.bins):
                    m =np.where(
                        self.bin_borders[bin_no] < chunksize,
                        True,
                        False
                        )
                    m = np.where(
                        self.bin_borders[bin_no+1] > chunksize,
                        m,
                        False)
                    m = channel_mask & m
                    cps = f"{channel}_bin{bin_no}_cps"
                    
                    self.data[cps] = np.array(
                        [np.count_nonzero(arr) for arr in m]
                        )
                    del m
                    self.details[cps] = [
                        f"Counts of {channel}-Particles (Bin{bin_no})",
                        "#/s"
                        ]
                    
                   
                del channel_mask
                
                
                
            lower = upper
            upper = lower + self.chunklen
            
            while lower <= self.timehandler[-1]:
                chunkmask=np.where(self.timehandler>=lower,True,False)
                chunkmask=np.where(self.timehandler<upper,chunkmask,False)
                chunktime = self.timehandler[chunkmask]
                chunksize = self.rawdata["size"][chunkmask]
                chunkexc = self.rawdata["excited"][chunkmask]
                chunkfl1 = self.rawdata["Fl1"][chunkmask]
                chunkfl2 = self.rawdata["Fl2"][chunkmask]
                chunkfl3 = self.rawdata["Fl3"][chunkmask]
                del chunkmask
                
                if upper < self.timehandler[-1]:
                    time_mask = np.array(
                        [np.where(chunktime==i,True,False) 
                         for i in range(lower,upper)]
                        )
                else:
                    time_mask = np.array(
                        [np.where(chunktime==i,True,False) 
                         for i in range(lower,self.timehandler[-1])]
                        )
                        
                #part_conc & #/s & dndlogdp
                for bin_no in range(self.bins):
                    m = np.where(self.bin_borders[bin_no] < chunksize,
                                 True,
                                 False)
                    m = np.where(self.bin_borders[bin_no+1] > chunksize,
                                 m,
                                 False)
                    bin_handler = time_mask & m
                    dat = np.array(
                        [np.count_nonzero(arr) for arr in bin_handler]
                        )
                    del bin_handler
                    pc = f"bin{bin_no}_partconc"
                    cps = f"bin{bin_no}_cps"
                    self.data[cps] = np.append(self.data[cps],dat)
                    dat = dat / self.flow
                    self.data[pc] = np.append(self.data[pc],dat)
                    
                    log_binwidth = np.log10(
                        self.bin_borders[bin_no+1]
                        )-np.log10(self.bin_borders[bin_no])
                    dn = f"bin{bin_no}_dndlogdp"
                    dat = dat / log_binwidth
                    self.data[dn] = np.append(self.data[dn],dat)
                    
                #total
                m = np.where(self.bin_borders[0] < chunksize,True,False)
                m = np.where(self.bin_borders[-1] > chunksize,m,False)
                total_handler = time_mask & m
                dat = np.array(
                    [np.count_nonzero(arr) for arr in total_handler]
                    )
                del total_handler
                self.data["total_cps"] = np.append(self.data["total_cps"],dat)
                
                #excited
                ex_handler = time_mask & chunkexc
                ex = np.array(
                    [np.count_nonzero(arr) for arr in ex_handler]
                    )
                self.data["excited"] = np.append(self.data["excited"],ex)
                del ex_handler
                exfrac = np.divide(
                    ex,
                    dat,
                    out=np.ones(ex.shape,dtype=float),
                    where=dat!=0
                    )
                self.data["excited_fraction"] = np.append(
                    self.data["excited_fraction"],
                    exfrac
                    )
                
                
                #fluorescence channels
                fl1_handler = time_mask & chunkfl1
                fl2_handler = time_mask & chunkfl2
                fl3_handler = time_mask & chunkfl3
                
                fl1 = np.array(
                    [np.count_nonzero(arr) for arr in fl1_handler]
                    )/exfrac
                self.data["fl1"] = np.append(self.data["fl1"],fl1)
                fl2 = np.array(
                    [np.count_nonzero(arr) for arr in fl2_handler]
                    )/exfrac
                self.data["fl2"] = np.append(self.data["fl2"],fl2)
                fl3 = np.array(
                    [np.count_nonzero(arr) for arr in fl3_handler]
                    )/exfrac
                self.data["fl3"] = np.append(self.data["fl3"],fl3)
                
                
                for channel in self.channels:
                    channel_mask = createmask(fl1_handler,
                                              fl2_handler,
                                              fl3_handler,
                                              channel)
                    for bin_no in range(self.bins):
                        m =np.where(
                            self.bin_borders[bin_no] < chunksize,
                            True,
                            False
                            )
                        m = np.where(
                            self.bin_borders[bin_no+1] > chunksize,
                            m,
                            False)
                        m = channel_mask & m
                        cps = f"{channel}_bin{bin_no}_cps"                        
                        dat = np.array(
                            [np.count_nonzero(arr) for arr in m]
                            )
                        self.data[cps] = np.append(self.data[cps],dat)
                        del m
                       
                    del channel_mask
                    
                    
                lower = upper
                upper = lower + self.chunklen
                    
            self.data["total_partconc"] = self.data["total_cps"] / self.flow
            self.details["total_partconc"] = ["Particle Conc.","#/cm${}^3$"]
            
            self.data["fl1_fraction"] = np.divide(
                self.data["fl1"],
                self.data["total_cps"],
                out=np.zeros(self.data["fl1"].shape,dtype=float),
                where=self.data["total_cps"]!=0
                )
            self.data["fl2_fraction"] = np.divide(
                self.data["fl2"],
                self.data["total_cps"],
                out=np.zeros(self.data["fl2"].shape,dtype=float),
                where=self.data["total_cps"]!=0
                )
            self.data["fl3_fraction"] = np.divide(
                self.data["fl3"],
                self.data["total_cps"],
                out=np.zeros(self.data["fl3"].shape,dtype=float),
                where=self.data["total_cps"]!=0
                )
            
            for channel in self.channels:
                cps = f"{channel}_total_cps"
                pc = f"{channel}_total_partconc"
                fr = f"{channel}_fraction"
                cps = f"{channel}_total_cps"
                self.data[cps] = np.sum(
                    [self.data[f"{channel}_bin{i}_cps"] 
                     for i in range(self.bins)],
                    axis=0
                    )
                self.data[pc] = self.data[cps] / self.flow
                self.data[fr] = np.divide(
                    self.data[cps],
                    self.data["total_cps"],
                    out=np.zeros(self.data[f"{channel}_total_cps"].shape,
                                 dtype=float),
                    where=self.data["total_cps"]!=0
                    )
                self.details[cps] = [f"Particle Counts of {channel}-Particles",
                                     "#/s"]
                self.details[pc] = [f"Particle Conc. of {channel}-Particles",
                                    "#/cm${}^3$"]
                self.details[fr] = [f"Fluorescent Fraction ({channel})",
                                    "No Unit"]
                for bin_no in range(self.bins):
                    cps = f"{channel}_bin{bin_no}_cps"
                    pc = f"{channel}_bin{bin_no}_partconc"
                    dn = f"{channel}_bin{bin_no}_dndlogdp"
                    self.data[pc] = self.data[cps] / self.flow
                    self.details[pc] = [
                        f"Particle Conc. of {channel}-Particles (bin{bin_no})",
                        "#/cm${}^3$"
                        ]
                    log_binwidth = np.log10(
                        self.bin_borders[bin_no+1]
                        )-np.log10(self.bin_borders[bin_no])
                    self.data[dn] = self.data[pc] / log_binwidth
                    self.details[dn] = [
                        f"dN/dlog$D_P$ of {channel}-Particles (Bin{bin_no})",
                        "cm$^{-3}$"
                        ]
                
            del self.timehandler
            del self.start
            del self.end
            del self.FT_date
            
    
    def quickplot(self,y):
        """
        Plots the given y over time

        Parameters
        ----------
        y : str
            Determines which data should be plotted.

        Returns
        -------
        None.

        """
        
        #error handling
        xx = self.data["t"]
        try:
            yy = self.data[y]
        except KeyError as kerr:
            raise IllegalValue(y, "WIBS.quickplot()",list(self.data)) from kerr
                
        #draw plot
        _,ax = plt.subplots()

        ax.set_xlabel("CET")
        if self.details[y][1] != "No Unit":
            ylabel = f"{self.details[y][0]} in {self.details[y][1]}"
        else:
            ylabel = self.details[y][0]
        ax.set_ylabel(ylabel)
        
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        ax.plot(xx,yy)
        
        plt.show()
        
        
    def quickheatmap(self,y):
        """
        Draws a dndlogdp number size distribution heatmap

        Parameters
        ----------
        y : str
            Determines which data should be plotted.

        Returns
        -------
        None.

        """
        
        #error handling
        try:
            yy = np.array(
                [self.data[f"{y}_bin{i}_dndlogdp"] for i in range(self.bins)]
                ) if y != "allparticles" else np.array(
                    [self.data[f"bin{i}_dndlogdp"] for i in range(self.bins)]
                    )
        except KeyError as kerr:
            raise IllegalValue(y, 
                               "WIBS.quickheatmap", 
                               ["allparticles","a","b","c",
                                "ab","ac","bc","abc"]) from kerr
        
        xlims = [self.data["t"][0],self.data["t"][-1]]
        xlims = md.date2num(xlims)
            
        #draw plot
        _,ax = plt.subplots()
        
        im = ax.imshow(yy,
                       aspect="auto",
                       norm="log",
                       extent=[xlims[0],xlims[1],0,self.bins]
                       ,cmap="RdYlBu_r",
                       interpolation="none",
                       origin="lower")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("$D_P$ in µm")
        ax.set_xlabel("CET")
        
        labels = [str(round(label,2)) for label in self.bin_means]
        ticks = [tick+0.5 for tick in range(self.bins)]
        ax.set_yticks(ticks,labels=labels)
        
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        plt.colorbar(im,ax=ax,label="dN/dlog$D_P$ in cm${}^{-3}$")
        
        plt.show()
        
        
    def heatmap(self,ax,y,**kwargs):
        """
        Draws a dndlogdp number size distribution heatmap over an existing 
        mpl axis

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The heatmap will be drawn on this axis.
        y : str
            Determines which data should be plotted.
            
        Other Parameters
        ----------------
        cmap : str, optional
            Changes the colormap. The default is 'RdYlBu_r'
        pad : float, optional
            Changes the padding between colorbar and plot. The default is 0.
        orientation : str, optional
            Changes the orientation of the colorbar.
        location : str, optional
            Changes the location of the colorbar. The default is 'top'.
        togglecbar : bool, optional
            If False, the colorbar wont be shown. The default is True.

        Returns
        -------
        None.

        """
        
        defaults = {"cmap" : "RdYlBu_r",
                    "pad" : 0,
                    "orientation" : "horizontal",
                    "location" : "top",
                    "togglecbar" : True}
        for key,default in defaults.items():
            kwargs[key] = self.hk_func_kwargs(kwargs, key, default)
        self.hk_errorhandling(kwargs, defaults.keys(), "WIBS.heatmap()")
        
        try:
            yy = np.array(
                [self.data[f"{y}_bin{i}_dndlogdp"] for i in range(self.bins)]
                ) if y != "allparticles" else np.array(
                    [self.data[f"bin{i}_dndlogdp"] for i in range(self.bins)]
                    )
        except KeyError as kerr:
            raise IllegalValue(y, 
                               "WIBS.heatmap()", 
                               ["allparticles","a","b","c",
                                "ab","ac","bc","abc"]) from kerr
        
        xlims = [self.data["t"][0],self.data["t"][-1]]
        xlims = md.date2num(xlims)
            
        #draw plot
        im = ax.imshow(yy,
                       aspect="auto",
                       norm="log",
                       extent=[xlims[0],xlims[1],0,self.bins],
                       cmap=kwargs["cmap"],
                       interpolation="none",
                       origin="lower")
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        ax.set_ylabel("$D_P$ in µm")
        ax.set_xlabel("CET")
        
        labels = [str(round(label,2)) for label in self.bin_means]
        ticks = [tick+0.5 for tick in range(self.bins)]
        ax.set_yticks(ticks,labels=labels)
        
        ax.yaxis.set_tick_params(which='minor', size=0)
        ax.yaxis.set_tick_params(which='minor', width=0)
        plt.colorbar(im,
                     ax=ax,
                     label="dN/dlog$D_P$ in cm${}^{-3}$",
                     pad=kwargs["pad"],
                     orientation=kwargs["orientation"],
                     location=kwargs["location"])
        
    
    def plot(self,ax,y,**kwargs):
        """
        Plots y over time on an existing mpl axis.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        y : str
            Determines which data should be plotted.
            
        Other Parameters
        ----------------
        label : str, optional
            Changes the label of the plot. If a legend is created, this label 
            will be shown there. The default is 'no label'.
        color : str
            Changes the color of the plot. The default is 'tab:purple'.
        secondary : bool, optional
            If True, the plot will draw the axis on the right-hand side. 
            Should be used if the given ax is a twinx(). The default is False.
        
        Returns
        -------
        None.

        """

        defaults = {"label" : "no label",
                    "color" : "tab:purple",
                    "secondary" : False}
        for key,default in defaults.items():
            kwargs[key] = self.hk_func_kwargs(kwargs, key, default)
        self.hk_errorhandling(kwargs, defaults.keys(), "WIBS.plot()")
        
        xx = self.data["t"]
        try:
            yy = self.data[y]
        except KeyError as kerr:
            raise IllegalValue("y", "WIBS.plot()",list(self.data)) from kerr
            
        if self.details[y][1] != "No Unit":
            ylabel = f"{self.details[y][0]} in {self.details[y][1]}"
        else:
            ylabel = self.details[y][0]
            
        #draw plot
        ax.plot(xx,yy,label=kwargs["label"],color=kwargs["color"])
        
        ax.set_xlabel("CET")
        ax.set_ylabel(ylabel)
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        
        ax.tick_params(axis='y', colors=kwargs["color"])
        ax.axes.yaxis.label.set_color(kwargs["color"])
        if not kwargs["secondary"]:
            ax.spines["left"].set_color(kwargs["color"])
        else:
            ax.spines["right"].set_color(kwargs["color"])
            ax.spines["left"].set_alpha(0)
            
    
    ## needs docstring and improvement and testing
    def stackedplot(self,ax,**kwargs):
        """
        Creates a Stacked Plot on an existing axis.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        
        Other Parameters
        ----------------
        start : str
            Takes a str in the format "HH:MM:SS" and only plots data acquired
            after it.
        end : str, optional
            Takes a str in the format "HH:MM:SS" and only plots data acquired
            before it.
        log : bool, optional
            If True the x-axis of the plot will be scaled logarithmicly. The 
            default is True.
        ylog : bool, optional
            If True the y-axis will be scaled logarithmically. The default is
            False.
        xlabel : str, optional
            Sets the xlabel of the plot. The default is "D$_p$ in µm".
        ylabel : str, optional
            Sets the xlabel of the plot. The default is "Fraction".
        legend : bool, optional
            If True a Legend will be drawn on the upper right. The default is 
            True.
        normalize : bool, optional
            If True the stackedplot will be normalized to 1, if False it will
            show the raw dndlogdp. The default is True.
        legacy : bool, optional
            If True, partconc is used instead of dndlogdp to calculate the 
            stacked areas. The default is False.

        Returns
        -------
        None
        """
        
        
        defaults = {"start" : None,
                    "end" : None,
                    "log" : True,
                    "xlabel" : "D$_p$ in µm",
                    "ylabel" : "Fraction",
                    "legend" : True,
                    "normalize" : True,
                    "legacy" : False,
                    "ylog" : False}
        for key,default in defaults.items():
            kwargs[key] = self.hk_func_kwargs(kwargs, key, default)
        self.hk_errorhandling(kwargs, defaults.keys(), "WIBS.stackedplot()")
        
        m = np.array([True for i in self.data["t"]])
        if isinstance(kwargs["start"],str):
            kwargs["start"] = datetime.strptime(kwargs["start"],"%H:%M:%S")
            kwargs["start"] = kwargs["start"].replace(
                year=self.data["t"][0].year,
                month = self.data["t"][0].month,
                day = self.data["t"][0].day
                )
            m = np.where(kwargs["start"]<self.data["t"],m,False)
        if isinstance(kwargs["end"],str):
            kwargs["end"] = datetime.strptime(kwargs["end"],"%H:%M:%S")
            kwargs["end"] = kwargs["end"].replace(
                year = self.data["t"][0].year,
                month = self.data["t"][0].month,
                day = self.data["t"][0].day
                )
            m = np.where(kwargs["end"]>self.data["t"],m,False)
        
        leg = "partconc" if kwargs["legacy"] else "dndlogdp"
        xx = self.bin_means
        totals = []
        for i in range(len(xx)):
            totals.append(np.nanmean(self.data[f"bin{i}_{leg}"][m]))
            totals[i] = 1 if totals[i] == 0 else totals[i]
        vals = np.array([0 for i in xx])
        for ch in ["a","b","c","ab","bc","ac","abc"]:
            new_vals = []
            for i in range(len(xx)):
                new_vals.append(
                    np.nanmean(self.data[f"{ch}_bin{i}_{leg}"][m])
                    )
            new_vals = np.array(new_vals) + vals
            if kwargs["normalize"]:
                ax.fill_between(xx,vals/totals,new_vals/totals,label=ch)
            else:
                ax.fill_between(xx,vals,new_vals,label=ch)
            vals = new_vals
        if kwargs["normalize"]:
            ax.fill_between(xx,vals/totals,
                            [1 for i in xx],
                            label="non fluorescent")
        else:
            totals = [
                np.nanmean(self.data[f"bin{i}_{leg}"][m]) 
                for i in range(len(xx))
                ]
            ax.fill_between(xx,vals,
                            totals,
                            label="non fluorescent")
        
        if kwargs["log"]:
            ax.set_xscale("log")
        if kwargs["ylog"]:
            ax.set_yscale("log")
        if kwargs["legend"]:
            ax.legend(loc="upper right")
        ax.set_xlabel(kwargs["xlabel"])
        ax.set_ylabel(kwargs["ylabel"])
        
        
    def dndlogdp(self,ax, **kwargs):
        """
        Creates a dN/dlogDp plot on an existing mpl axis.

        Parameters
        ----------
        ax : Axes obj of mpl.axes module
            The plot will be drawn on this axis.
        
        Other Parameters
        ----------------
        start : str, optional
            If a str in the format "HH:MM:SS" is given, only data acquired 
            after this timestamp will be used for the dNdlogDp curve.
        end : str, optional
            If a str in the format "HH:MM:SS" is given, only data acquired
            before this timestamp will be used for the dNdlogDp curve.
        log : bool, optional
            If True the x-axis will be expressed logarithmicly. The default is
            True.
        xlabel : str, optional
            Sets the x label to the given str. The default is 'D$_p$ in μm'.
        ylable : str, optional
            Sets the y label to the given str. The default is 
            'dN/dlogD$_p$ in cm{^{-3}$'.
        scatter : bool, optional
            If True, a scatterplot will be drawn instead of a bar plot. The 
            default is False.
        scatter_color : str, optional
            Changes the color of the scatter plot. Only in effect if 
            `scatter=True`. The default is 'tab:blue'.
        scatter_line : bool, optional
            If True a dashed line that connects the points will be drawn. Only
            in effect if `scatter=True`. The default is True.
        bin_borders : list of float, optional
            Should only be passed if the `WIBS` object was created from a .wibs
            file that was created before agg_dim 0.1.18 and does not have the 
            `bin_borders` attribute. If no list is passed, it will try to 
            use the `bin_borders` attribute from the `WIBS` obj and if it 
            has none, an `AttributeError` will be raised.
        particle_type : str, optional
            Decides which particle type should be plotted. (legal values are: 
            a,b,c,ab,ac,bc,abc). If all particles should be plotted without 
            considering particle type, dont pass this kwarg.

        Returns
        -------
        None
        """
        
        
        #kwargs
        defaults = {"start" : None,
                    "end" : None,
                    "log" : True,
                    "xlabel" : "D$_p$ in μm",
                    "ylabel" : "dN/dlogD$_p$ in cm{^{-3}$",
                    "scatter" : False,
                    "scatter_color" : "tab:blue",
                    "scatter_line" : True,
                    "bin_borders" : None,
                    "particletype" : None}
        
        for key,default in defaults.items():
            kwargs[key] = self.hk_func_kwargs(kwargs, key, default)
        self.hk_errorhandling(kwargs, defaults.keys(), "WIBS.dndlogp()")
        
        xx = np.array(self.bin_means)
        m = np.array([True for t in self.data["t"]])
        
        if isinstance(kwargs["start"],str):
            dd = self.data["t"][0].day
            mm = self.data["t"][0].month
            yy = self.data["t"][0].year
            start = datetime.strptime(kwargs["start"],
                                      "%H:%M:%S"
                                      ).replace(day=dd,
                                                month=mm,
                                                year=yy)
            m = np.where(self.data["t"]>=start,m,False)
        if isinstance(kwargs["end"],str):
            dd = self.data["t"][0].day
            mm = self.data["t"][0].month
            yy = self.data["t"][0].year
            end = datetime.strptime(kwargs["end"],
                                    "%H:%M:%S"
                                    ).replace(day=dd,
                                              month=mm,
                                              year=yy)
            m = np.where(self.data["t"]<=end,m,False)
            
        if kwargs["particletype"] is None:
            yy = np.array([np.nanmean(self.data[f"bin{i}_dndlogdp"][m]) 
                           for i in range(self.bins)])
        else:
            try:
                pt = kwargs["particletype"]
                yy = np.array(
                    [np.nanmean(self.data[f"{pt}_bin{i}_dndlogdp"][m]) 
                     for i in range(self.bins)]
                    )
            except:
                msg = f"{kwargs['particletype']} is not a legal particletype. "
                msg += "Legal particle types are a, b, c, ab, ac, bc or abc. "
                msg += "If you want to plot the particle number size distribut"
                msg += "ion of all particles, leave the kwarg 'particletype' "
                msg += "blank."
                raise ValueError(msg)
     
        if kwargs["scatter"]:
            ax.scatter(xx,yy,color=kwargs["scatter_color"])
            if kwargs["scatter_line"]:
                ax.plot(xx,yy,
                        color=kwargs["scatter_color"],
                        linestyle="dashed")
        else:
            if isinstance(kwargs["bin_borders"],list):
                bb = kwargs["bin_borders"]
            else:
                try:
                    bb = self.bin_borders
                except AttributeError:
                    msg = "bin_borders attribute does not exist. The loaded"
                    msg += " .wibs file was probably created before the attri"
                    msg += "bute was introduced. Try passing 'bin_borders'"
                    msg += " manually in WIBS.dndlogdp() or consult docu."
                    raise AttributeError(msg)
            width = np.array([bb[i+1]-bb[i] for i in range(self.bins)])
            ax.bar(xx,yy,width*0.8,align="center")
        if kwargs["log"]:
            ax.set_xscale("log")
        ax.set_xlabel("D$_p$ in μm")
        ax.set_ylabel("dN/dlogD$_p$ in cm$^{-3}$")
        
        
    def save(self, path):
        """
        Saves the obj as a preprocessed .wibs file

        Parameters
        ----------
        path : str
            Determines the path and name, where the .wibs file should be saved.

        Returns
        -------
        None.

        """
        
        op = {
            "bins" : self.bins,
            "bin_means" : self.bin_means,
            "bin_borders" : self.bin_borders,
            "data" : self.data,
            "rawdata" : self.rawdata,
            "details" : self.details,
            "fl1_FTbg" : self.fl1_FTbg,
            "fl2_FTbg" : self.fl2_FTbg,
            "fl3_FTbg" : self.fl3_FTbg,
            "FT_sigma" : self.FT_sigma,
            "flow" : self.flow
            }
        
        if path[-5:] != ".wibs":
            path += ".wibs"
          
        with open(path,"wb") as dumppath:
            pickle.dump(op,dumppath,4)
            
            
    def returndata(self):
        """
        Returns a tuple containing all data in a standardized form. Important 
        for communication with `agg_dim.drone.DroneWrapper` or 
        `agg_dim.experiment.Wrapper` objs.

        Returns
        -------
        data : dict {str : np.array}
            This dict contains all data in the form of np.arrays indexed by 
            their name.
        details : dict {str : [str,str]}
            This dict contains a description and a unit for all the 
            exported data.
        """
        
        
        op_t = []
        for t in self.data["t"]:
            op_t.append(t.replace(microsecond=0))
        op_data = {"t":np.array(op_t)}
        for key in self.data.keys():
            if key == "t":
                continue
            op_data[key] = self.data[key]
        
        return op_data,self.details
    

    def append(self,wibs2):
        """
        Adds another `WIBS` obj to the current one.

        Parameters
        ----------
        wibs2 : WIBS
            Object whichs data is to be appended.

        Returns
        -------
        None
        """
        
        for key in self.data:
            self.data[key] = np.append(
                self.data[key],
                wibs2.data[key]
                )

    
    #housekeeping funcs
    
    def hk_kwargs(self,kwargs,key,default):
        """
        Housekeeping Func --> Should not be used outside the object
        
        Turns kwargs into attributes
        """

        op = kwargs[key] if key in kwargs else default
        setattr(self,key,op)
        
        
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
          
