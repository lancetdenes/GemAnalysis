import pandas as pd
import numpy as np
import os 
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def plot_tracks(df, cmap_name='viridis', save_path='fasttracks.png'):
    grouped = df.groupby('particle')
    print('Number of tracks: ', len(grouped))

    fig, ax = plt.subplots()

    # Create a colormap
    cmap = cm.get_cmap(cmap_name)

    # Normalize the values of your variable to the range [0, 1]
    variable_values = [group['Deff'].values[0] for n, group in grouped]
    norm = plt.Normalize(min(variable_values), max(variable_values))

    track_len_list = []
    diff_list = []

    for n, group in grouped:
        track_len_list.append(len(group))
        deff = group['Deff'].values[0]
        diff_list.append(deff)
        variable_value = group['Deff'].values[0]
        ax.plot(group['x'], group['y'], color=cmap(norm(variable_value)))

    # Add a colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, label='Deff')

    plt.savefig(save_path)
    plt.close()

    return track_len_list, diff_list


path = '/gpfs/scratch/denesl01/projects/MSC_GEMs/20240206_GEM_plating_collagen_cell_density/'
exp_list = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
full_exp = []
for exp in exp_list:
    print('starting: ', exp)
    flist = [f for f in os.listdir(os.path.join(path, exp, 'per_nuc_tracks')) if f.endswith('.csv')]
    consol = []
    for f in flist:
        df = pd.read_csv(os.path.join(path, exp, 'per_nuc_tracks', f))
        basename = f.split('_nucleus_')
        cell = basename[0][-3:] + '_' + basename[1].split('_tracks.csv')[0]
        grouped = df.groupby('particle')
        for n, group in grouped:
            track_len = len(group)
            deff = group['Deff'].values[0]
            consol.append([basename[0][:-4], cell, int(track_len), deff, int(n)])
    df = pd.DataFrame(consol)
    df.columns =  ['condition', 'cell', 'track_len', 'Deff', 'particle']
    df_grouped = df.groupby(['cell', 'condition'])
    temp = []
    for n, group in df_grouped:
        med = group['Deff'].median()
        n_tracks = len(group)
        name = n[0] + '_' + n[1]
        temp.append([n[0], n[1], med, n_tracks])
    df = pd.DataFrame(temp, columns=['cell', 'condition', 'Deff', 'n_tracks'])
    full_exp.append(df)

full_exp = pd.concat(full_exp)
full_exp.to_csv('full_exp.csv')
full_exp = full_exp[full_exp['n_tracks'] > 10]
import seaborn as sns
fig,ax=plt.subplots()
sns.scatterplot(data=full_exp, y='Deff', x='condition', ax=ax)
plt.xticks(rotation=45)
fig.tight_layout()
plt.savefig('swarm.png')