import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience
import pims_nd2
from pims_nd2 import ND2_Reader
import trackpy as tp
import os
from cellpose import models,io
from skimage.io import imread
from scipy.stats import linregress

def process_gem(nucfile, nucmodel, maskout, gemfile, minmass, rate, outprefix):
    '''
    nucfile = path to the image of the nucleus that matches the gem movie 
    model = path to the cellpose model being used for nucleus segmentation, '/gpfs/scratch/denesl01/libLTD/CP_20220513_192756' is working right now  
    maskout = path to the directory for cellpose output
    gemfile = path to the original ND2 file with gem movie
    minmass = intensity cutoff for patricle identification, 100 for 20ms images and 70 for 10 ms images
    rate = frame rate from acquisition, 50 fps for 20ms images and 100 for 10 ms images
    outprefix = filename to append tracks/stats for outfiles 
    '''
    
    nuc_image = ND2_Reader(nucfile).get_frame(0)
    #nuc_image = imread(nucfile)
    model = models.CellposeModel(pretrained_model=nucmodel) 
    masks, flows, styles = model.eval(nuc_image, diameter=120)
    io.masks_flows_to_seg(nuc_image, masks, flows, 120, maskout, [0]) 
    io.save_to_png(nuc_image, masks, flows, maskout)
    nuc_mask = np.where(masks>0, 1, 0)

    frames = ND2_Reader(gemfile)
    #frames = imread(gemfile)
    arr_list = []
    for item in frames:
        arr_list.append(item)
    frames = np.array(arr_list)
    f = tp.batch(frames, 9, minmass=float(minmass), separation=3, processes=4)
    raw_tracks = tp.link(f, 5, memory=3)
    raw_tracks['compartment'] = 'cyto'
    raw_tracks.loc[nuc_mask[raw_tracks['y'].astype(int), raw_tracks['x'].astype(int)] > 0, 'compartment'] = 'nuc'
    tracks = tp.filter_stubs(raw_tracks, 11)
    pixel_size = 0.1341799
    imsd = tp.motion.imsd(tracks, pixel_size, rate).iloc[:10,:]
    print(imsd)
    a=[]
    fit_lag = 10
    for column in imsd.columns:
        print(imsd[column][:fit_lag])
        t = tp.utils.fit_powerlaw(imsd[column][:fit_lag], plot=False)
        t['d_eff'] = linregress(imsd[column].index[:fit_lag], imsd[column].iloc[:fit_lag]).slope/4
        a.append(t)
    a = pd.concat(a)
    tracks['alpha'] = 0.
    tracks['D'] = 0.
    df_list = []
    grouped = tracks.groupby('particle')
    for (z,(n,dft)) in zip(a.index, grouped):
        dft['alpha'] = a.loc[z]['n']
        dft['D'] = a.loc[z]['A']/4
        dft['d_eff'] = a.loc[z]['d_eff']
        dft['track_length'] = len(dft)
        dft['avg_mas'] = dft['mass'].mean()
        df_list.append(dft)
    tracks = pd.concat(df_list)
    em_nuc = tp.emsd(tracks[tracks['compartment'] == 'nuc'], pixel_size, rate)
    em_cyto = tp.emsd(tracks[tracks['compartment'] == 'cyto'], pixel_size, rate)
    nuc_vals = tp.utils.fit_powerlaw(em_nuc.iloc[:10], plot=False)
    cyto_vals = tp.utils.fit_powerlaw(em_cyto.iloc[:10], plot=False)
    cyto_deff = linregress(em_cyto.index[:fit_lag], em_cyto.iloc[:fit_lag]).slope/4
    nuc_deff = linregress(em_nuc.index[:fit_lag], em_nuc.iloc[:fit_lag]).slope/4
    nuc_vals['A']=nuc_vals['A']/4
    cyto_vals['A']=cyto_vals['A']/4
    nuc_vals['d_eff'] = nuc_deff
    cyto_vals['d_eff'] = cyto_deff
    nuc_vals['compartment'] = 'nuc'
    cyto_vals['compartment'] = 'cyto'
    vals = pd.concat([nuc_vals, cyto_vals])
    vals.columns = ['alpha', 'd', 'compartment', 'd_eff']
    vals.index = [1, 2]
    tracks.to_csv(outprefix+'_tracks.csv')
    vals.to_csv(outprefix+'_vals.csv')



'''
base_dir = '/gpfs/scratch/denesl01/20220521_nucgem/'
nuc_f_list = [f for f in os.listdir(base_dir) if f.endswith('_nuc.nd2')]
nuc_model = '/gpfs/scratch/denesl01/libLTD/CP_20220513_192756'

nuc_fname = nuc_f_list[1]

nuc_f_path = os.path.join(base_dir, nuc_fname)
cpout_path = os.path.join(base_dir, 'cellpose_output', nuc_fname.split('_nuc.nd2')[0])
gem_f = os.path.join(base_dir, nuc_fname.split('_nuc.nd2')[0]+'.nd2')
outpre = os.path.join(base_dir, 'track_output', nuc_fname.split('_nuc.nd2')[0])

process_gem(nuc_f_path, 
            nuc_model, 
            cpout_path,
            gem_f,
            120, 
            50, 
            outpre)
'''
