# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 15:15:41 2024

@author: mrupp
"""

class IllegalValue(Exception):
    
    def __init__(self,illegalvar,funcname,keys):

        legalstrings = ", ".join(list(keys.keys()))
        self.message = "Illegal " + illegalvar + " was given for " + funcname + "\nLegal " + illegalvar + "s: " + legalstrings
        super().__init__(self.message)
        
        
class NotPlottable(Exception):
    
    def __init__(self,givenvar,funcname,legallist):
        
        
        legalstr = ", ".join(legallist)
        self.message = givenvar + " is not plottable in " + funcname + "\nLegal strings: " + legalstr
        super().__init__(self.message)