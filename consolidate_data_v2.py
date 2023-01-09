import pandas as pd
import os
import sys

scratch = os.environ['SCRATCH']
experiment = sys.argv[1]
epath = os.path.join(scratch, 'projects', 'MSC_GEMs', experiment)
valsdir = os.path.join(epath, 'vals')
df = pd.read_csv(os.path.join(epath, 'file_list.csv'), index_col=0)
dflist = []
for n,sample in df.iterrows():
    valsf = sample['gem_file'].split('.nd2')[0]+'_vals.csv'
    try:
        dft = pd.read_csv(os.path.join(valsdir, valsf), index_col=0)
    except:
        print('data not found for: ', sample)
        continue
    for col in sample.index:
        dft[col] = sample[col]
    dflist.append(dft)
df = pd.concat(dflist)
df.to_csv(os.path.join(epath, 'consolidated.csv'))
