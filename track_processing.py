import pandas as pd
from nd2reader import ND2Reader
import numpy as np
import matplotlib.pyplot as plt
import skimage as sk
import colorcet as cc
from matplotlib.collections import LineCollection
from skimage.measure import label
from skimage.morphology import dilation, erosion, disk
import os
import sys
import matplotlib.patheffects as PathEffects
import Mysbatch_


def read_nd2(file_path):
    with ND2Reader(file_path) as images:
        return np.array(images)

def plot_images(gem, nuc, nucim, tracks, fname, outdir):

    #make output directories for plots and tracks
    if not os.path.exists(os.path.join(outdir, 'track_plots')):
        os.makedirs(os.path.join(outdir, 'track_plots'))
    if not os.path.exists(os.path.join(outdir, 'per_nuc_tracks')):
        os.makedirs(os.path.join(outdir, 'per_nuc_tracks'))
    if not os.path.exists(os.path.join(outdir, 'gemspa_tracks')):
        os.makedirs(os.path.join(outdir, 'gemspa_tracks'))
    if not os.path.exists(os.path.join(outdir, 'cyto_tracks')):
        os.makedirs(os.path.join(outdir, 'cyto_tracks'))

    #initiate glasbey colormap for tracks
    cmap = cc.cm['glasbey_hv']

    #separate nuclear tracks and filter out short tracks below 9, also save cytoplasmic tracks
    tracks_nuc = tracks[tracks['compartment'] == 'nuc']
    tracks_cyto = tracks[tracks['compartment'] == 'cyto']
    tracks_cyto = tracks_cyto.groupby('particle').filter(lambda x: len(x) > 9)
    tracks_cyto.to_csv(os.path.join(outdir, 'cyto_tracks', fname + '_tracks.csv'))
    cyto_gemspa = tracks_cyto[['particle', 'frame', 'x', 'y']]
    cyto_gemspa.columns = ['Trajectory', 'Frame', 'x', 'y']
    cyto_gemspa.to_csv(os.path.join(outdir, 'per_nuc_tracks', 'cytoGemSpa_fname'+'_tracks.csv'))
    tracks_nuc = tracks_nuc.groupby('particle').filter(lambda x: len(x) > 9)
    
    #get the unique nucleus labels
    labelmax = nuc.max()

    #make the color dictionary for each nucleus from the glasbey cmap
    color_dict = {i: cmap(i) for i in range(1, 1+labelmax)}    #get the region properties of the nuclei for later use to plot centroids 
    nuc_props=sk.measure.regionprops(nuc)
    
    #make nucleus boundaries for plots
    boundaries = sk.segmentation.find_boundaries(nuc)
    boundaries_rgba = np.zeros((boundaries.shape[0], boundaries.shape[1], 4))  # Initialize with zeros
    boundaries_rgba[boundaries] = [0, 0, 0, 1]

    #initiate figure 
    fig,ax = plt.subplots(1,3, figsize= (20, 10))
    
    #plot nucleus boundaries with transparent background
    ax[0].imshow(boundaries_rgba)

    #filter the gem image with a gaussian filter for smoothing and plot the max projection in time
    gem = sk.img_as_uint(sk.filters.gaussian(gem, 1))
    ax[1].imshow(np.amax(gem, axis=0,), cmap='Greys', interpolation='none', vmin=100, vmax=160)

    #plot the nuclear boundaries again overtop of the gem image
    ax[1].imshow(boundaries_rgba, interpolation='none')
    #plot the first frame of the nuclear image
    ax[2].imshow(nucim[0,:,:], cmap='Greys', interpolation='none')
    
    #now loop through the different nuclei in each dataframe and begin to plot the tracks
    for nuc in nuc_props:
        label = nuc.label
        group = tracks_nuc[tracks_nuc['nucleus'] == label]

        #make sub data frames grouped by nucleus to be saved as individual files for downstream processing 
        labeled_df = group[['particle', 'frame', 'x', 'y']]
        labeled_df.columns = ['Trajectory', 'Frame', 'x', 'y']
        group.to_csv(os.path.join(outdir, 'per_nuc_tracks', '_'.join([fname, 'nucleus', str(label), 'tracks.csv']))) 
        labeled_df.to_csv(os.path.join(outdir, 'gemspa_tracks', '_'.join([fname, 'nucleus', str(label), 'tracks.csv'])))

        #generate a list of the number of unique tracks in each nucleus to be plotted on top of each nucleus 
        num_tracks = group['particle'].nunique()
        
        #plot this number on top of the nuclei 
        
        ax[2].text(nuc_props[label-1].centroid[1], nuc_props[label-1].centroid[0], 'nucleus %s\n%s tracks'%(label, num_tracks), color=color_dict[label], fontsize=8, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none'))
        
        #plot the tracks for each nucleus, colored by the colordict generated above 
        for track, group in group.groupby('particle'):
            ax[0].plot(group['x'], group['y'], color=color_dict[label], lw=0.5)
    
    #finish the plot and save
    fig.tight_layout()
    plt.savefig(os.path.join(outdir, 'track_plots', fname + '_tracks.png'), dpi=300)
    plt.close()

def process_directory(exp_dir):
    exp_list = [f for f in os.listdir(exp_dir) if '.' not in f]
    for d in exp_list:
        flist = os.path.join(exp_dir, d, 'file_list.csv')
        df = pd.read_csv(flist, index_col=0).reset_index(drop=True)
        for i, row in df.iterrows():
            gempath = os.path.join(exp_dir, d, 'rawdata', row['gem_file'])
            nucimpath = os.path.join(exp_dir, d, 'rawdata', row['nuc_file'])
            nucpath = os.path.join(exp_dir, d, 'png_masks', row['nuc_file'].split('.')[0] + '_cp_masks.png')
            trackspath = os.path.join(exp_dir, d, 'tracks', row['gem_file'].split('.')[0] + '_tracks.csv')
            print('opening images for', row['gem_file'] + '...')
            gem = read_nd2(gempath)
            nucim = read_nd2(nucimpath) 
            nuc = sk.io.imread(nucpath)
            print('loading tracks for', row['gem_file'] + '...')
            tracks = pd.read_csv(trackspath)
            fname = row['gem_file'].split('.nd2')[0]
            plot_images(gem, nuc, nucim, tracks, fname, os.path.join(exp_dir, d))



# input the experiment directory here 
# here is one as a sample:
# '/gpfs/home/denesl01/scratch/projects/MSC_GEMs/20240206_GEM_plating_collagen_cell_density' 
#should have subdirs with all the formatted categories
if __name__ == '__main__':
    process_directory(sys.argv[1])

    