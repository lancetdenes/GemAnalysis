import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience
from nd2reader import ND2Reader
import trackpy as tp
import os
from cellpose import models,io
from skimage.io import imread
from scipy.stats import linregress

def track_gem(gem_file, nuc_file=None, minmass=100., rate=100, pixel_size=0.1833333, spot_size=9, tif=False):
    '''
    gem_file = path to the original ND2 file with gem movie
    minmass = intensity cutoff for patricle identification, 100 for 20ms images and 70 for 10 ms images
    rate = frame rate from acquisition, 50 fps for 20ms images and 100 for 10 ms images
    pixel_size = different pixel size dependent on the microscope
    '''
    print('INITIALIZE: gem tracking pipline track_gems_v2 on %s'%gem_file)
    cytoflag=False
    base_path,prefix = os.path.split(gem_file)
    base_path = os.path.split(base_path)[0]
    print(base_path)    
    if not tif:
        prefix = prefix.split('.nd2')[0]
        arr_list = []
        with ND2Reader(gem_file) as frames:
            for item in frames:
                arr_list.append(item)
        frames = np.array(arr_list)
    else:
        prefix = prefix.split('.tif')[0]
        frames = imread(gem_file)
    f = tp.batch(frames, spot_size, minmass=minmass, separation=3, processes=4)
    raw_tracks = tp.link(f, 5, memory=3)
    raw_tracks['compartment'] = 'cyto'
    if nuc_file:
        trash,nuc_prefix = os.path.split(nuc_file)
        nuc_prefix = nuc_prefix.split('.nd2')[0]
        try:
            nuc_file = os.path.join(base_path,'png_masks', nuc_prefix+'_cp_masks.png')
            print(nuc_file)
            nuc_mask = imread(nuc_file)
            raw_tracks.loc[nuc_mask[raw_tracks['y'].astype(int), raw_tracks['x'].astype(int)] > 0, 'compartment'] = 'nuc'
        except:
            print('\n\n\n______\nno nuc masks! cyto only for this sample: ', prefix,'\n_______\n\n\n')
            cytoflag = True
    else:
        cytoflag = True
    tracks = tp.filter_stubs(raw_tracks, 11)

    #comput the imsd for each track and combine them into a single dataframe from which a summary statsistic can be derived and tracks can be labeled
    imsd = tp.motion.imsd(tracks, pixel_size, rate).iloc[:10,:]
    print(imsd)
    a=[]
    fit_lag = 10
    for column in imsd.columns:
        #print(imsd[column][:fit_lag]) excessive print statements
        t = tp.utils.fit_powerlaw(imsd[column][:fit_lag], plot=False)
        t['lin_Deff'] = linregress(imsd[column].index[:fit_lag], imsd[column].iloc[:fit_lag]).slope/4
        a.append(t)
    a = pd.concat(a)

    #initialize a property for every track that will then be filled with values derived from imsd, add these properties to to tracks dataframe 
    tracks['alpha'] = 0.
    tracks['D'] = 0.
    df_list = []
    grouped = tracks.groupby('particle')
    for (z,(n,dft)) in zip(a.index, grouped):
        dft['alpha'] = a.loc[z]['n']
        dft['Deff'] = a.loc[z]['A']/4
        dft['lin_Deff'] = a.loc[z]['lin_Deff']
        dft['track_length'] = len(dft)
        dft['avg_mas'] = dft['mass'].mean()
        df_list.append(dft)
    tracks = pd.concat(df_list)

    #calculate ensemble values for each compartment
    em_cyto = tp.emsd(tracks[tracks['compartment'] == 'cyto'], pixel_size, rate)
    cyto_vals = tp.utils.fit_powerlaw(em_cyto.iloc[:10], plot=False)
    cyto_deff = linregress(em_cyto.index[:fit_lag], em_cyto.iloc[:fit_lag]).slope/4
    cyto_vals['lin_Deff'] = cyto_deff
    cyto_vals['compartment'] = 'cyto'
    if not cytoflag:
        em_nuc = tp.emsd(tracks[tracks['compartment'] == 'nuc'], pixel_size, rate)
        nuc_vals = tp.utils.fit_powerlaw(em_nuc.iloc[:10], plot=False)
        nuc_deff = linregress(em_nuc.index[:fit_lag], em_nuc.iloc[:fit_lag]).slope/4
        nuc_vals['lin_Deff'] = nuc_deff
        nuc_vals['compartment'] = 'nuc'
        vals = pd.concat([nuc_vals, cyto_vals])
    else: 
        vals = cyto_vals
    print(vals.columns)
    vals.columns = ['alpha', 'Deff', 'lin_Deff', 'compartment']
    vals = vals.reset_index(drop=True)
    vals['Deff'] = vals['Deff']/4
    print(vals)

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
    parser.add_argument('--nuc_file', default=None, help='add nucfile or not')
    parser.add_argument('--minmass', default=100., type=float, help='minmass parameter for trackpy')
    parser.add_argument('--rate', default=100, type=float, help='frame rate in frames per second')
    parser.add_argument('--pixel_size', default=0.1833333, type=float, help='pixel size in um per pixel from microscope, this default is for holt lab nikon new spinning disk ')
    parser.add_argument('--spot_size', default=9, type=int, help='spot size for trackpy')
    parser.add_argument('--tif', action='store_true', help='whether input file is nd2 or tiff, for read in purposes')
    args=parser.parse_args()
    track_gem(gem_file=args.gem_file, nuc_file=args.nuc_file, minmass=args.minmass, rate=args.rate, pixel_size=args.pixel_size, spot_size=args.spot_size, tif=args.tif)