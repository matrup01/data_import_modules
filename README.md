# Welcome to the data analysis modules of AG Grothe

## Contents

This repo contains modules with python importable classes that can be used for data analysis of different instruments. Further documentation is available under https://matrup01.github.io/data_import_modules

Supported instruments:
- POPS
- FlyingFlo
- WIBS
- SEN55
- CCS811
- Weatherstation

## How to use

### Automatic installation

Enter the following command in your console:
```sh
pip install -i https://test.pypi.org/simple/ agg-dim
```
For upgrading add the `--upgrade` flag before `-i`

### Manual installation

Download the .whl-file from the release folder and enter the following in your console:
```sh
pip install yourlocalpath/yourlocalfilename.whl
```

## How to contribute

If you are from AG Grothe you are welcome to add/improve on modules and commit into this repo. Please just keep the following things in mind:

- Please add docstrings in numpydoc format (see https://numpydoc.readthedocs.io/en/latest/format.html), that can be automatically added to the docu. Also make add a block to change.log, to make it clear what has been changed.
- This repo only contains general purpose import classes for different instruments. Please dont add code for data analysis of a specific project!
- Please add your changes to dev or create a new branch. Changes will be merged into main for new releases.
