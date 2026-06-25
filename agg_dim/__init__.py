"""
# AG Grothe Data Import Modules
Welcome to agg_dim!

This Module contains Data Analysis Classes for different instruments.

Full Docu is available under https://matrup01.github.io/data_import_modules

## How to use
Install over PyPi:
```
pip install -i https://test.pypi.org/simple/ agg-dim
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