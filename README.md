fMRI Preprocessing
----------------------------------------------

The new and improved resting-state fMRI preprocessing pipeline

> Alex Bartnik 06/2019

Due to the free-for-all nature of processing in a notebook leading to inconsistencies
and the generation of huge images that were never used in the final analyses,
the fMRI preprocessing pipeline has been reworked into one monolithic program
to make everyone's lives easier.

**This has 3  main advantages**:
    - Speed: This program has been designed so that the user may specifiy 
	     how many instances of the preprocessing pipeline may be run
	     in parellel (10 is recommended)
    - Easier to understand: 
    - Easier to QC


### Usage
In order for processing to successfully run, you'll need to make sure you have all of the
required python packages (numpy, nilearn, sklearn, pandas).
The easiest way to do this is to source the python venv in /.../connectome/venv/bin/activate.
This is done anytime the user runs `./activate` in this directory, like:
$ ./activate 
To leave the venv and carry on with your normal life, simply enter 'deactivate' in your terminal.

The three necessary arguments are as follows:
 - 1) Subject list - self explanatory, just a file containing the subjects you want to process
 - 2) Number of threads - how many instances to run (usually 10, but can use from 1-64 on donut)
 - 3) Stage - which stage of preprocessing to run; options are "Premelodic," "Melodic," "Postmelodic," and "All"


To run premelodic steps (brain extraction, slicetime correction, motion outlier detection, etc.) on 10 threads:

`python main.py subject_list.csv 10 premelodic`


