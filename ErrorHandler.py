# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 15:15:41 2024

@author: mrupp
"""

class IllegalValue(Exception):
    
    def __init__(self,illegalvar,funcname,legallist):

        legalstrings = ", ".join(legallist)
        self.message = "Illegal " + illegalvar + " was given for " + funcname + "\nCheck for typos or if needed data is loaded\nLegal " + illegalvar + "s: " + legalstrings
        super().__init__(self.message)
        
        
class NotPlottable(Exception):
    
    def __init__(self,givenvar,funcname,legallist):
        
        
        legalstr = ", ".join(legallist)
        self.message = givenvar + " is not plottable in " + funcname + "\nLegal strings: " + legalstr
        super().__init__(self.message)
        
        
class IllegalArgument(Exception):
    
    def __init__(self,arg,func,legallist=[]):
        
        if len(legallist) != 0:
            legalstr = ", ".join(legallist)
            self.message = arg + " isn't a legal kwarg for " + func + "\nLegal arguments: " + legalstr
        else:
            self.message = arg + " isn't a legal kwarg for " + func + "\nCheck for typos or consult documentation: "
        super().__init__(self.message)
        
        
class IllegalFileFormat(Exception):
    
    def __init__(self,wrongfile,correctfile,argname):
        
        self.message = "." + wrongfile + "-files are not legal as " + argname + ". Expected file: ." + correctfile
        super().__init__(self.message)