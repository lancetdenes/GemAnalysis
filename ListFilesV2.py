import os
import pandas as pd

import os
import pandas as pd

def list_files(path, ext='.nd2'):
    files = [f for f in os.listdir(os.path.join(path, 'rawdata')) if f.endswith(ext)]
    odd_files = [f for f in files if int(f.split('_')[-1].replace(ext, '')) % 2 == 1]
    paired_files = [(f, f.rsplit('_', 1)[0] + '_' + str(int(f.split('_')[-1].replace(ext, '')) + 1).zfill(3) + ext) for f in odd_files]
    return paired_files

def create_file_list(path):
    paired_files = list_files(path)
    data = []
    field_count = None
    for nuc_file, gem_file in paired_files:
        fields = nuc_file.split('_')
        if field_count is None:
            field_count = len(fields)
        elif field_count != len(fields):
            print(f"Warning: {nuc_file} has a different number of fields")
            continue
        data.append([nuc_file, gem_file] + fields[:-1] + [fields[-1].replace('.nd2', '')])
    columns = ['nuc_file', 'gem_file'] + [f'field_{i+1}/{field_count-1}' for i in range(field_count-1)] + ['sample']
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(os.path.join(path, 'file_list.csv'))

if __name__ == '__main__':

    exp_path = '/gpfs/scratch/denesl01/projects/MSC_GEMs/2024_GEM_clones/'
    exp_list = [f for f in os.listdir(exp_path) if os.path.isdir(os.path.join(exp_path, f))]
    for exp in exp_list:
        print('starting: ', exp)
        create_file_list(os.path.join(exp_path, exp))