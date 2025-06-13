# `simulations`
This repository contains template files for `jwave` simulations. 
Different simulations can be run by simply changing some user-defined parameters in the Jupyter notebooks. 

## `jwave` installation
See [these notes](https://liminalinsights.atlassian.net/wiki/x/egAGQ). 
Notebooks are configured to run on CPU by default. 
This can be changed to GPU, but be aware of memory usage. 

## Miscellaneous
Also included is a Python script `CreateAnimation.py` to render an animation (optionally an mp4 movie) from the simulation dump file. 
FOr how to use it, run the following: 
```bash
$ python -u ./CreateAnimation.py --help
```




