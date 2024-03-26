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

plotting_notebook was made to work on per nucleus functionality 

3/25/24

exported plotting_notebook to "track_processing.py" 
    
    feed this script a directory that contains subdirectories for each image set (can modify this to accept a single subdirectory)
    The script will make all subsequent data directories on its own 
    It will take the output tracks files from previous scripts and open original images and masks to make plots of images + tracks 
    it will then split up the tracks on a per nucleus basis and save a file for each

    Now, need to use a consolidation script to process each tracks file 



Run the bash script to make the directories and run the python scripts to generate file list and start the jobs 
