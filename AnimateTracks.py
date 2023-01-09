import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import os 
import sys
import matplotlib as mpl
from nd2reader import ND2Reader
#mpl.use('agg')
print(mpl.animation.writers.list())
scratch = os.environ['SCRATCH']
experiment = sys.argv[1]
epath = os.path.join(scratch, 'projects', 'MSC_GEMs', experiment)
df = pd.read_csv(os.path.join(epath, 'consolidated.csv'))
animpath = os.path.join(epath, 'animate')
if not os.path.exists(animpath):
    os.mkdir(animpath)
gem_file = df.iloc[0]['gem_file']
prefix = gem_file.split('.nd2')[0]
tracks = pd.read_csv(os.path.join(epath, 'tracks', prefix+'_tracks.csv'))

arr_list = []
with ND2Reader(os.path.join(epath, 'rawdata', gem_file)) as frames:
    for item in frames:
        arr_list.append(item)
gem_mov = np.array(arr_list)

from matplotlib.animation import FuncAnimation
from matplotlib import animation, rcParams


FFwriter = animation.FFMpegWriter(bitrate=1600, fps=10)
img = gem_mov
fig,ax=plt.subplots()

im = ax.imshow(img[0,:,:], cmap='Greys', vmax=150, vmin=100)
line, = ax.plot([],[], c='r')#, s=2, c='r', facecolors='none', edgecolors='r')
def animate(i):
    im.set_data(img[i,:,:])
    frame = tracks[tracks['frame']==i]
    particles = frame.groupby('particle')
    for n, particle in particles:
        print(particle)
        line.set_data(particle['x'], particle['y'])

    return im,line


anim = FuncAnimation(fig, animate, frames=range(img.shape[0]), interval=1, blit=False)
anim.save('test.mp4', writer=FFwriter)
