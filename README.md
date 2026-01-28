# Welcome to the data analysis modules of AG Grothe

## Contents

This repo contains modules with python importable classes that can be used for data analysis of different instruments. Further documentation is available in /docu/docu.md

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
```
pip install -i https://test.pypi.org/simple/ agg-dim
```
For upgrading add the `--upgrade` flag before `-i`

### Manual installation

Download the .whl-file from the release folder and enter the following in your console:
```
pip install yourlocalpath/yourlocalfilename.whl
```

## How to contribute

If you are from AG Grothe you are welcome to add/improve on modules and commit into this repo. Please just keep the following things in mind:

- Please add documentation of your changes in both docu.md and change.log in a consistent way, to make it easier for others to make use of your improvements!
- This repo only contains general purpose import classes for different instruments. Please dont add code for data analysis of a specific project!
- Please add your changes to dev or create a new branch. Changes will be merged into main for new releases.
