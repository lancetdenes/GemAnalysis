import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience
import pims_nd2
from pims_nd2 import ND2_Reader
import trackpy as tp
import os
import skimage as sk
from cellpose import models,io
from skimage.io import imread
from scipy.stats import linregress

working_dir = '/gpfs/home/denesl01/scratch/20221107_GEM_osmo'
df = pd.read_csv(os.path.join(working_dir, 'file_list.csv'))
#nuc_model = '/gpfs/scratch/denesl01/libLTD/CP_20220513_192756'
print('loading model')
nuc_model = '/gpfs/scratch/denesl01/libLTD/CP_20221228_nuclei_60xNikonSD'
model = models.CellposeModel(pretrained_model=nuc_model, gpu=True) 
print(model.device)

for n,line in df.iterrows():
    nucfile = os.path.join(working_dir, line['nuc_file'])
    sample = line['sample']
    sample = f'{sample:03d}'
    prefix = '_'.join([line['time'],line['condition'],sample])
    nuc_image = ND2_Reader(nucfile).get_frame(0)
    #used this to save training data 
    #sk.io.imsave(os.path.join('/gpfs/home/denesl01/scratch/202221228_nuc_training', '_'.join([line['time'],line['condition'],sample])+'.tif'), nuc_image)
    print('segmenting')
    masks, flows, styles = model.eval(nuc_image, diameter=120, progress=True)
    print('finished!')
    if not os.path.exists(os.path.join(working_dir, 'npy_masks')):
        os.mkdir(os.path.join(working_dir, 'npy_masks'))
    if not os.path.exists(os.path.join(working_dir, 'png_masks')):
        os.mkdir(os.path.join(working_dir, 'png_masks'))
    io.masks_flows_to_seg(nuc_image, masks, flows, 120, os.path.join(working_dir, 'npy_masks', prefix), [0]) 
    io.save_to_png(nuc_image, masks, flows, os.path.join(working_dir, 'png_masks', prefix))
    nuc_mask = np.where(masks>0, 1, 0)
    nuc_smooth = sk.filters.median(nuc_image, footprint=np.ones((10,10)))
    fig,(ax1,ax2,ax3)=plt.subplots(1,3)
    ax1.imshow(nuc_mask, cmap='Greys')
    ax2.imshow(nuc_smooth > sk.filters.threshold_isodata(nuc_smooth), cmap='Greys')
    ax3.imshow(nuc_image, cmap='Greys')
    ax3.set_title('original')
    ax1.set_title('cellpose')
    ax2.set_title('threshold')
    if not os.path.exists(os.path.join(working_dir, 'compare_segs')):
        os.mkdir(os.path.join(working_dir, 'compare_segs'))
    plt.savefig(os.path.join(working_dir, 'compare_segs', prefix+'.png'))

