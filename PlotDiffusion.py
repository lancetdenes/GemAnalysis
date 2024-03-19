import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os 
import sys
mpl.use('agg')

scratch = os.environ['SCRATCH']
experiment = sys.argv[1]
epath = os.path.join(scratch, 'projects', 'MSC_GEMs', experiment)
df = pd.read_csv(os.path.join(epath, 'consolidated.csv'))

'''timedict = {'T0':0, 'T1': 5, 'T2':10, 'T3':20, 'T4':40, 'T5': 80, 'T6': 160, 'T7': 320, 'T8': 640, 'T9': 1280}
for f in timedict:
    timedict[f] = timedict[f]/60.
df['time'] = df['time'].apply(lambda x: timedict[x])
df['time'] = df['time'].apply(lambda x: int(x[1:]))
'''
print(df)
#df['combo']=df['field_1']+'_'+df['field_2']
#df['time'] = np.log2(df['time'])
#df['Deff'] = np.log2(df['Deff'])
x = False
#parse fields
fields = []
y='Deff'
for col in df.columns:
    if 'time' in col:
        x = 'time'
    if 'field' in col:
        fields.append(col)

if experiment == 'differentiation_22.12.15_3day_timecourse':
    fig,ax = plt.subplots(figsize=(10,5))
    plotdf = df[df['compartment'] == 'nuc']
    plotdf = df[df['field_2'] == 'D']
    plotdf['log2time'] = np.log2(plotdf['field_0'])
    #sns.lineplot(data=plotdf, y='Deff', x='log2time', hue='field_1', hue_order=['C', 'A', 'AA', 'O', 'OM'])
    sns.swarmplot(data=plotdf, y='Deff', x='field_0', hue='field_1', hue_order=['C', 'A', 'AA', 'O', 'OM'], s=3, dodge=True)
    ax.set_ylim(bottom=0)
    ax.set_xlabel('hours')
    plt.savefig(os.path.join(epath, 'swarm_%s_condition.pdf'%(experiment)))

if experiment == 'osmotic_stress_22.11.07_long_timecourse':
    fig,ax = plt.subplots(figsize=(10,5))
    plotdf = df[df['compartment'] == 'nuc']
    sns.swarmplot(data=plotdf, y='Deff', x='time', hue='field_2/3', dodge=True, s=3, ax=ax, order=['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9'], hue_order=['c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    ax.set_ylim(bottom=0)
    ax.legend(loc='lower left', fontsize=6)
    plt.savefig(os.path.join(epath, '%s_condition.pdf'%(experiment)))

if experiment == 'osmotic_stress_22.12.11_short_timecourse':
    fig,ax = plt.subplots(figsize=(3,2))
    plotdf = df[df['compartment'] == 'nuc']
    field = 'field_2/3'
    plotdf = plotdf[(plotdf[field] == '100mM') | ( plotdf[field] == '75mM')]
    sns.swarmplot(data=plotdf, y='Deff', x=x, hue=field, dodge=True, s=3, order=['t0', 't1', 't5', 't15', 't30', 't60'], ax=ax)#hue_order=['wnk0mM', '75mM', 'wnk75mM', '100mM', '200mM'], ax=ax)
    ax.legend(fontsize=6,frameon=False)
    ax.set_ylim([0,0.9])

    fig.tight_layout()
    plt.savefig(os.path.join(epath, '%s_condition.pdf'%(experiment)))


if experiment == 'substrates_22.12.06_gels':
    fig,ax = plt.subplots(figsize=(10,5))
    comp = 'cyto'
    plotdf = df[df['compartment'] == comp]
    plotdf = plotdf[(plotdf['substrate'] == 'glass') | (plotdf['substrate'] == '30um')]
    field = 'substrate'
    sns.swarmplot(data=plotdf, y='Deff', x=x, hue=field, dodge=True, s=3)
    ax.legend(fontsize=6, frameon=False)
    ax.set_ylim([0,0.9])
    plt.savefig(os.path.join(scratch, '%s_%s.png'%(experiment, comp)))