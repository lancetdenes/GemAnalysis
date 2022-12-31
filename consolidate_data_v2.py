import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
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
    dft = pd.read_csv(os.path.join(valsdir, valsf), index_col=0)
    dflist.append(dft)
df = pd.concat(dflist)
print(df)