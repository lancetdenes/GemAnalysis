import pandas as pd
import os
import sys 
from nd2reader import ND2Reader
import matplotlib.pyplot as plt

scratch = os.environ['SCRATCH']
experiment = sys.argv[1]
datapath = os.path.join(scratch,'projects', 'MSC_GEMs', experiment, 'rawdata')
sampledict = {}
columns_list = []
#initial pass through directory to screen for file name architecture
skip_images = sys.argv[2]
fdict = {}

flistnd2 = [f for f in os.listdir(datapath) if f.endswith('.nd2')]
flisttif = [f for f in os.listdir(datapath) if f.endswith('.tif')]
if len(flistnd2) > 1 and len(flisttif) == 0:
    naming_conv = {}
    excepted_files = []
    flist = []
    for f in flistnd2:
        if 'zstack' in f or 'ZSTACK' in f or 'weird' in f or 'WEIRD' in f:
            print('strange file encountered, (%s) left out of file list'%f)
            excepted_files.append(f)
        else:
            prefix = f.split('.nd2')[0]
            parsed = prefix.split('_')
            n_descriptors = len(parsed)
            if len(parsed[-1]) == 3 and parsed[-1].isdigit():
                if n_descriptors not in naming_conv:
                    naming_conv[n_descriptors] = [0, 'example: %s'%prefix]
                    fdict[n_descriptors] = []
                fdict[n_descriptors].append(f)
                naming_conv[n_descriptors][0] += 1
            else:
                nm = str(n_descriptors)+'_unconventional'
                if nm not in naming_conv:
                    naming_conv[nm] = [0, 'example: %s'%prefix]
                    fdict[nm] = []
                naming_conv[nm][0] += 1
                fdict[nm].append(f)
else:
    print('multiple image file types in raw data directory:\n', flistnd2, '\n', flisttif)
    exit()

import itertools
flist = list(itertools.chain(*fdict.values()))
print('\nfound %s type of filenames from %s files\n'%(len(fdict), len(flist)))
print('\ndictionary of naming conventions: ', naming_conv)

for n,item in enumerate(fdict.values()):
    flist = item
print('using flist %s'%n)

if len(naming_conv) == 1:
    print('\nentering file list, parsing metadata: ')
    for i,f in enumerate(flist):
        print('file #%s'%i)
        prefix = f.split('.nd2')[0]
        fields = prefix.split('_')
        if len(fields[-1]) == 3:
            sample = int(fields[-1])
            gem_image = True
            with ND2Reader(os.path.join(datapath, f)) as frames:
                for n,chan in enumerate(frames.metadata['channels']):
                    if 'DAPI' in chan:
                        if n != 0:
                            print('nucleus not channel index 0, generate nucleus channel flag for filelist and update scripts or generate new files')
                            exit()
                        else:
                            gem_image = False

            if not gem_image:
                if sample%2 == 0:
                    sample_num_gem = f'{sample-1:03d}'
                    gem_path = '_'.join(fields[:-1])+'_'+sample_num_gem+'.nd2'
                    if os.path.exists(os.path.join(datapath, gem_path)):
                        sampledict[f] = []
                        sampledict[f].append(f)
                        sampledict[f].append(gem_path)
                        for n,item in enumerate(fields):
                            sampledict[f].append(item)
                    else:
                        print('gem image corresponding to nucleus is not present')
                        exit()

                    if not skip_images:
                        print('entering plotting functionality, might take a while')
                        qc_dir = os.path.join(scratch,'projects', 'MSC_GEMs', experiment,'paired_images')
                        if not os.path.exists(qc_dir):
                            os.mkdir(qc_dir)
                        fig,(ax1,ax2) = plt.subplots(1,2)
                        with ND2Reader(os.path.join(datapath, f)) as frames:
                            ax1.imshow(frames[0], cmap='Greys')
                            ax1.set_title('nucleus')
                        with ND2Reader(os.path.join(datapath, gem_path)) as frames:
                            ax2.imshow(frames[0], cmap='Greys', vmax=200)
                            ax2.set_title('gems')
                        fig.savefig(os.path.join(qc_dir,prefix+'paired.png'))
                        plt.close()
                        
                            
else:
    print('\nmultiple conventions, figure out whats going on!\n')
    exit()


columns_list = ['nuc_file', 'gem_file']
for n,item in enumerate(fields):
    columns_list.append('field_%s'%n)
df = pd.DataFrame(sampledict).T
df.columns = columns_list
df.to_csv(os.path.join(scratch, 'projects', 'MSC_GEMs', experiment, 'file_list.csv'))