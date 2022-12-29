#!/gpfs/home/denesl01/.conda/envs/cp-tp-v2env/bin/python
import os
import sys
import Mysbatch_
import track_gems_v2
import pandas as pd

scratch = os.environ['SCRATCH']
data_dir = sys.argv[1]
file_list = os.path.join(scratch,data_dir,'file_list.csv')
if not os.path.exists(file_list):
    print('ERROR: file list not there!')
    exit()

file_list = pd.read_csv(file_list,index_col=0)
print('loaded file list!')

for n,line in file_list.iterrows():
    gem_file = os.path.join(scratch,data_dir,line['gem_file'])
    cmd = 'python track_gems_v2.py --gem_file %s'%gem_file
    scriptOptions = {'jobname':'track_nuc_gems','time':'12:00:00','partition':'cpu_short','mem-per-cpu':'2gb', 'cpus-per-task':'4', 'gres':'0'}
    Mysbatch_.launchJob(cmd,scriptOptions,verbose=True)