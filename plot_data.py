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

if x:   
    for n, field in enumerate(fields):
        fig,ax = plt.subplots(figsize=(10,5))
        sns.swarmplot(data=df[df['compartment']=='nuc'], y='Deff', x=x, hue=field, dodge=True, s=3)#, hue_order=['c0','c1','c2','c3','c4','c5','c6','c7'],ax=ax, s=3,dodge=True)#err_style="bars",order=['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9'], ax=ax)
        ax.legend(fontsize=6, frameon=False)
        if '/' in field:
            field = '.'.join(field.split('/'))
        plt.savefig('%s_%s.png'%(experiment, field))
else:
    print(df)

