import pandas as pd
import os
import sys 
from nd2reader import ND2Reader
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('agg')
scratch = os.environ['SCRATCH']
experiment = sys.argv[1]
datapath = os.path.join(scratch,'projects', 'MSC_GEMs', experiment, 'rawdata')
print(datapath)
#initial pass through directory to screen for file name architecture
fdict = {}

flistnd2 = [f for f in os.listdir(datapath) if f.endswith('.nd2')]
flisttif = [f for f in os.listdir(datapath) if f.endswith('.tif')]
if len(flistnd2) > 1 and len(flisttif) == 0:
    naming_conv = {}
    excepted_files = []
    flist = []
    for f in flistnd2:
        if 'zstack' in f or 'ZSTACK' in f or 'weird' in f or 'WEIRD' in f or 'mitosis' in f:
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
    if n == 0:
        flist1 = item
    if n == 1:
        flist2 = item

print('\nentering file list, parsing metadata: ')
def generate_flist(flist, fieldlen):
    cy5 = False
    sampledict = {}
    columns_list = []
    scratch = os.environ['SCRATCH']
    experiment = sys.argv[1]
    datapath = os.path.join(scratch,'projects', 'MSC_GEMs', experiment, 'rawdata')

    for i,f in enumerate(flist):
        #print('file #%s'%i)
        prefix = f.split('.nd2')[0]
        fields = prefix.split('_')
        if len(fields[-1]) == 3:
            sample = int(fields[-1])
            gem_image = True
            with ND2Reader(os.path.join(datapath, f)) as frames:
                for n,chan in enumerate(frames.metadata['channels']):
                    #print(chan)
                    if 'DAPI' in chan or 'dapi' in chan:
                        if n != 0:
                            print('nucleus not channel index 0, generate nucleus channel flag for filelist and update scripts or generate new files')
                            exit()
                        else:
                            gem_image = False
                    if 'CY5' in chan:
                        gem_image=False
                        cy5 = True
            if not gem_image:
                #print('nucleus image')
                if sample%2 == 0:
                    sample_num_gem = f'{sample-1:03d}'
                else:
                    sample_num_gem = f'{sample+1:03d}'
                
                gem_path = '_'.join(fields[:-1])+'_'+sample_num_gem+'.nd2'
                if os.path.exists(os.path.join(datapath, gem_path)):
                    sampledict[f] = []
                    sampledict[f].append(f)
                    sampledict[f].append(gem_path)
                    for n,item in enumerate(fields):
                        sampledict[f].append(item)
                else:
                    print('gem image corresponding to nucleus is not present', f)
                    continue

                if sys.argv[2] == 'plot':
                    #print('entering plotting functionality, might take a while')
                    qc_dir = os.path.join(scratch,'projects', 'MSC_GEMs', experiment,'paired_images')
                    if not os.path.exists(qc_dir):
                        os.mkdir(qc_dir)
                    fig,(ax1,ax2) = plt.subplots(1,2)
                    with ND2Reader(os.path.join(datapath, f)) as frames:
                        if cy5:
                            ax1.imshow(frames[1], cmap='Greys')
                        else:
                            ax1.imshow(frames[0], cmap='Greys')
                        ax1.set_title('nucleus')
                    with ND2Reader(os.path.join(datapath, gem_path)) as frames:
                        ax2.imshow(frames[0], cmap='Greys', vmax=200)
                        ax2.set_title('gems')
                    fig.savefig(os.path.join(qc_dir,prefix+'paired.png'))
                    plt.close()
    
    columns_list = ['nuc_file', 'gem_file']
    for n,item in enumerate(fields):
        print(n,item)
        if len(item) == 3 and item.isdigit():
            columns_list.append('sample')
        elif item.startswith('t') or item.startswith('T') or 'hr' in item:
            columns_list.append('time')
        elif 'glass' in item or 'kPa' in item or 'kpa' in item or item.endswith('um'):
            columns_list.append('substrate')
        elif 'power' in item:
            columns_list.append('laserpower')
        elif 'ms' in item:
            columns_list.append('exposure')
        else:
            columns_list.append('field_%s/%s'%(n+1,fieldlen))
    df = pd.DataFrame(sampledict).T
    print(df)
    df.columns = columns_list
    return(df)

if len(naming_conv) != 1:
    print('\nmultiple conventions, figure out whats going on!\n')

df_list = []
for key in fdict:
    print(key)
    print('processing %s fields files'%key)
    dft = generate_flist(fdict[key], key)
    df_list.append(dft)

df = pd.concat(df_list)
print(df)
df.to_csv(os.path.join(scratch, 'projects', 'MSC_GEMs', experiment, 'file_list.csv'))




#df.to_csv(os.path.join(scratch, 'projects', 'MSC_GEMs', experiment, 'file_list.csv')