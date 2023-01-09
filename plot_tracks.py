import pandas as pd
import matplotlib.pyplot as plt
import os, sys
from nd2reader import ND2Reader
import matplotlib as mpl
import numpy as np

mpl.use('agg')
scratch = os.environ['SCRATCH']
experiment = sys.argv[1]
epath = os.path.join(scratch, 'projects', 'MSC_GEMs', experiment)
df = pd.read_csv(os.path.join(epath, 'consolidated.csv'))

sample = df.iloc[0]

gem_movie = os.path.join(epath, 'rawdata', sample['gem_file'])
nucleus_image = os.path.join(epath, 'rawdata', sample['nuc_file'])

tracks = pd.read_csv(os.path.join(epath, 'tracks', sample['gem_file'].split('.nd2')[0]+'_tracks.csv'))

nuc_im = ND2Reader(nucleus_image)
arr_list = []
with ND2Reader(gem_movie) as frames:
    for item in frames:
        arr_list.append(item)
gem_mov = np.array(arr_list)

fig,ax=plt.subplots(figsize=(7,9))
ax.imshow(np.amax(gem_mov, axis=0), cmap='Greys', vmin=100, vmax=200)
for n,track in tracks.groupby('particle'):
    ax.plot(track['x'], track['y'], lw=0.3, alpha=0.5)
ax.set_aspect('equal')
ax.axis('off')
plt.savefig('test.pdf')

