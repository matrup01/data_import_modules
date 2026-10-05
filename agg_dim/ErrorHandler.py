# -*- coding: utf-8 -*-
"""
This submodule contains classes that are used to raise Exceptions inside the
module agg_dim. From outside the module there is no real usecase.
"""

class IllegalValue(Exception):
    
    def __init__(self,illegalvar,funcname,legallist):

        legalstrings = ", ".join(legallist)
        self.message = (f"Illegal {illegalvar} was given for {funcname}\n"
                        "Check for typos or if needed data is loaded\n"
                        f"Legal {illegalvar}s: {legalstrings}")
        super().__init__(self.message)
        
        
class NotPlottable(Exception):
    
    def __init__(self,givenvar,funcname,legallist):
        
        
        legalstr = ", ".join(legallist)
        self.message = (f"{givenvar} is not plottable in {funcname}\n"
                        f"Legal strings: {legalstr}")
        super().__init__(self.message)
        
        
class IllegalArgument(Exception):
    
    def __init__(self,arg,func,legallist=[]):
        
        if len(legallist) != 0:
            legalstr = ", ".join(legallist)
            self.message = (f"{arg} isn't a legal kwarg for {func}\n"
                            f"Legal arguments: {legalstr}")
        else:
            self.message = (f"{arg} isn't a legal kwarg for {func}\n"
                            "Check for typos or consult documentation.")
        super().__init__(self.message)
        
        
class IllegalFileFormat(Exception):
    
    def __init__(self,wrongfile,correctfile,argname):
        
        self.message = (f".{wrongfile}-files are not legal as {argname}. "
                        f"Expected file: .{correctfile}")
        super().__init__(self.message)
        
        
class SensorNotMounted(Exception):
    
    def __init__(self,illegalvar,instrument):
        
        self.message = (f"{illegalvar} can't be used here, since the "
                        "corresponding sensor is not mounted onto "
                        f"{instrument} in the given layout.")
        super().__init__(self.message)
        

class UnknownLayoutError(Exception):
    
    def __init__(self,illegal,legallist,instrument):
        
        legal = ", ".join(legallist)
        self.message = (f"{illegal} is no legal layout for {instrument} "
                        "You can use a custom layout or use one of the known"
                        f" layouts: {legal}")
        super().__init__(self.message)