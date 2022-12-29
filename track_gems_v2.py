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

def process_gem(gem_file, nuc=True, minmass=100., rate=100, pixel_size=0.1833333, spot_size=9, nd2=True):
    '''
    gem_file = path to the original ND2 file with gem movie
    minmass = intensity cutoff for patricle identification, 100 for 20ms images and 70 for 10 ms images
    rate = frame rate from acquisition, 50 fps for 20ms images and 100 for 10 ms images
    pixel_size = different pixel size dependent on the microscope
    '''
    print(gem_file)
    base_path,prefix = os.path.split(gem_file)
    prefix = prefix.split('.nd2')[0]
    if nd2:
        frames = ND2_Reader(gem_file)
        arr_list = []
        for item in frames:
            arr_list.append(item)
        frames = np.array(arr_list)
    else:
        frames = imread(gem_file)
    f = tp.batch(frames, spot_size, minmass=minmass, separation=3, processes=4)
    raw_tracks = tp.link(f, 5, memory=3)
    raw_tracks['compartment'] = 'cyto'
    if nuc:
        nuc_file = os.path.join(base_path,'png_masks', prefix+'_cp_masks.png')
        nuc_mask = imread(nuc_file)
        raw_tracks.loc[nuc_mask[raw_tracks['y'].astype(int), raw_tracks['x'].astype(int)] > 0, 'compartment'] = 'nuc'
    tracks = tp.filter_stubs(raw_tracks, 11)
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
    if not os.path.exists(os.path.join(base_path,'tracks')):
        os.mkdir(os.path.join(base_path,'tracks'))
    if not os.path.exists(os.path.join(base_path,'vals')):
        os.mkdir(os.path.join(base_path,'vals'))
    tracks.to_csv(os.path.join(base_path,'tracks',prefix+'_tracks.csv'))
    vals.to_csv(os.path.join(base_path,'vals',prefix+'_vals.csv'))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--gem_file')
    parser.add_argument('--nuc', default=True, type=bool, help='specify with true/false whether this dataset needs to be segmented with nuclei masks (generated separately)')
    parser.add_argument('--minmass', default=100., type=float, help='minmass parameter for trackpy')
    parser.add_argument('--rate', default=100, type=float, help='frame rate in frames per second')
    parser.add_argument('--pixel_size', default=0.1833333, type=float, help='pixel size in um per pixel from microscope, this default is for holt lab nikon new spinning disk ')
    parser.add_argument('--spot_size', default=9, type=int, help='spot size for trackpy')
    parser.add_argument('--nd2', default=True, type=bool, help='whether input file is nd2 or tiff, for read in purposes')
    args=parser.parse_args()
    process_gem(gem_file=args.gem_file, nuc=args.nuc, minmass=args.minmass, rate=args.rate, pixel_size=args.pixel_size, spot_size=args.spot_size, nd2=args.nd2)