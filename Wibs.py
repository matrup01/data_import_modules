# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 08:26:00 2024

@author: mrupp
"""


from datetime import datetime
import h5py
import numpy as np


class Wibs:
    
    def __init__(self,file,timecorr):
        
        if type(file) == str:
            f = h5py.File(file,"r")
            f2 = f["NEO"]
            f3 = f2['ParticleData']
            f4 = f2["MonitoringData"]
            
            wibstime = list(f3["Seconds"])
            wibstime = [wibstime[i] - 3810797754 + 1727952954 - 212 for i in range(len(wibstime))] #correct weird WIBS dataformat
            wibstime = [wibstime[i] + 7200 - timecorr for i in range(len(wibstime))] #correct timezone and WIBS-computer time error
            self.wibstime = [datetime.utcfromtimestamp(wibstime[i]) for i in range(len(wibstime))] #convert to datetime
            
            self.data = {"size" : list(f3["Size_um"]),
                         "excited" : [bool(ex) for ex in list(f3["Flag_Excited"])]}
            
            self.data["ex_size"] = [s if x else np.NaN for s,x in zip(self.data["size"],self.data["excited"])]
            
                
            
    
    def debug(self):
        
        print(self.wibstime)