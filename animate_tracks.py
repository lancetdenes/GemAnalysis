import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import os 
import sys
import matplotlib as mpl
#mpl.use('agg')
print(mpl.animation.writers.list())
scratch = os.environ['SCRATCH']
experiment = sys.argv[1]
epath = os.path.join(scratch, 'projects', 'MSC_GEMs', experiment)
df = pd.read_csv(os.path.join(epath, 'consolidated.csv'))
animpath = os.path.join(epath, 'animate')
if not os.path.exists(animpath):
    os.mkdir(animpath)


prefix = df.iloc[0]['gem_file'].split('.nd2')[0]
tracksdir = os.path.join(epath, 'tracks')

data = pd.read_csv(os.path.join(tracksdir, prefix+'_tracks.csv'))

print(df)

import matplotlib.animation as animation

# assume data is a pandas DataFrame with columns 'x', 'y', 'id', and 'frame'

# create a figure and axis
fig, ax = plt.subplots()

# create empty lists for the lines and points
lines = []
points = []

# function to update the plot for each frame
def update(num):
    # clear the previous frame
    for line in lines:
        line.set_data([], [])
    #for point in points:
    #    point.set_data([], [])
    lines.clear()
    #points.clear()
    
    # get the data for the current frame
    frame_data = data[data['frame'] == num]
    
    # plot the lines and points for each trajectory
    for _, row in frame_data.iterrows():
        while(_) < 100:
            x = row['x']
            y = row['y']
            id = row['particle']
            line, = ax.plot(x, y, '-', c=f'C{id % 10}')
            #point, = ax.plot(x, y, 'o', c=f'C{id % 10}')
            lines.append(line)
            #points.append(point)

# create the animation using the update function and the number of frames
ani = animation.FuncAnimation(fig, update, frames=data['frame'].max()+1, blit=False)

# show the plot
Writer = animation.writers['ffmpeg']
Writer = Writer(fps=10, metadata=dict(artist="Me"), bitrate=-1)

print('rendering animation')
ani.save('test.mp4', writer=Writer)


'''def plot_gems(tracks, image):   
    fig, ax = plt.subplots()
    ax.imshow(image)
    for n,track in tracks.groupby('particle'):
        line, = ax.plot(track['x'], track['y'])

def animate(i):
    line.set_ydata(i)  # update the data.
    return line,

ani = animation.FuncAnimation(fig, animate, interval=20, blit=True, save_count=50)

# To save the animation, use e.g.
#
ani.save("movie.mp4")
#
# or
#
writer = animation.FFMpegWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)
ani.save("movie.mp4", writer=writer)

plt.show()
'''