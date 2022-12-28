import matplotlib as mpl
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
nuc_model = '/gpfs/scratch/denesl01/libLTD/CP_20220513_192756'
nucfile = os.path.join(working_dir, df.iloc[0]['nuc_file'])
print(nucfile)
nuc_image = ND2_Reader(nucfile).get_frame(0)
print('loading model')
model = models.CellposeModel(pretrained_model=nuc_model, gpu=True) 
print(model.device)
print('segmenting')
masks, flows, styles = model.eval(nuc_image, diameter=120, progress=True)
print('finished!')
#io.masks_flows_to_seg(nuc_image, masks, flows, 120, maskout, [0]) 
#io.save_to_png(nuc_image, masks, flows, maskout)
nuc_mask = np.where(masks>0, 1, 0)


fig,(ax1,ax2)=plt.subplots(1,2)
ax1.imshow(nuc_mask)
ax2.imshow(nuc_image > sk.filters.threshold_otsu(nuc_image))
plt.savefig('test.png')
