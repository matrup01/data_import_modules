"""
# AG Grothe Data Import Modules
Welcome to agg_dim!

This Module contains Data Analysis Classes for different instruments.


## Installation
Install over PyPi:
```
pip install -i https://test.pypi.org/simple/ agg-dim
```

--> Alternatively you can also get the .whl from [github](https://github.com/matrup01/data_import_modules)
```
pip install ~/your/local/path/downloadedfile.whl
```

## How to use
This module provides objects, which the data of the different instruments 
should be read into. All further analysis can be done using this obj.
Example from the Grimm 11-D:
```python
from agg_dim import OPC
import matplotlib.pyplot as plt

opc = OPC("file-C.dat")

_,ax = plt.subplots()
opc.plot(ax,"totalpartconc")
plt.show()
```

## How to contribute
See https://github.com/matrup01/data_import_modules
"""

from .drone import Dronedata, DroneWrapper
from .fluoreszenz import FData, NewFData
from .lowcostsensors import CCS811, SEN55, FlyingFlo_USB
from .particle_counters import Pops, OPC
from .wibs import WIBS
from .weather import WeatherData
from .experiment import Wrapper, save_experiment, load_experiment