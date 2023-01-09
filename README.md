# GemAnalysis
pipelines for tracking and analyzing gem movies

will continue to update this with adapted scripts for both local machines and bigpurple compute cluster 

big_purple_optimization_notebook.ipynb is being used currently to generate file lists containing sample information and paired nucleus/gem files 

gem_tracking.py is the original script without nucleus segmentation that uses trackpy for GEM analysis 

process_nuc_gem.py is the nucleus segmentation version of the script that uses cellpose to segment nuclei 

use the tp-cp-v2env for running these scripts 


all scripts renamed and synchronized with Github 

pipeline: 

make sure file structure is consistent: 

experiment_directory 
    rawdata 
        sequence of nucleus and gem movies 

all output directories will be generated into this experiment directory automatically 

run ListFiles to generate file list from directory, may need fine tuning depending on naming convention, KEEP NAMING CONSISTENT FOR BEST RESULTS 

run JobLauncher with filelist and experiment directory path to automatically process 

plotting scripts need fine tuning on a per experiment basis depending on various parameters 

need to make napari launcher script once environment is set up appropriately 

