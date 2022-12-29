# gem-analysis
pipelines for tracking and analyzing gem movies

will continue to update this with adapted scripts for both local machines and bigpurple compute cluster 

big_purple_optimization_notebook.ipynb is being used currently to generate file lists containing sample information and paired nucleus/gem files 

gem_tracking.py is the original script without nucleus segmentation that uses trackpy for GEM analysis 

process_nuc_gem.py is the nucleus segmentation version of the script that uses cellpose to segment nuclei 

use the tp-cp-v2env for running these scripts 