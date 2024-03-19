import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import os
scratch = os.environ['SCRATCH']
experiment = 'differentiation_22.12.15_3day_timecourse'
epath = os.path.join(scratch, 'projects', 'MSC_GEMs', experiment)
df = pd.read_csv(os.path.join(epath, 'consolidated.csv'))
df = df[df['compartment'] == 'nuc']
control_sparse = df[(df['field_1'] == 'C') & (df['field_2'] == 'S')]
osteo_sparse = df[(df['field_1'] == 'O') & (df['field_2'] == 'S')]
control_dense = df[(df['field_1'] == 'C') & (df['field_2'] == 'D')]
osteo_dense = df[(df['field_1'] == 'O') & (df['field_2'] == 'D')]

fig,ax = plt.subplots(figsize=(2,1))
times = [float(f) for f in osteo_dense['field_0']]
diffusions = [float(f) for f in osteo_dense['Deff']]

print(times, diffusions)

'''plt.scatter(times, diffusions)

plt.show()'''