#!/gpfs/home/denesl01/.conda/envs/cp-tp-v2env/bin/python
import os
import sys
import Mysbatch_
import pandas as pd


def launch_gem_job(nuc_file, model_path, gem_file):
    cmd = 'python SegmentNuc.py --nuc_file %s --modelpath %s\npython TrackGEMs.py --gem_file %s --nuc_file %s'%(nuc_file, model_path, gem_file, nuc_file)
    scriptOptions = {'jobname':'track_nuc_gems','time':'12:00:00','partition':'cpu_short','mem-per-cpu':'2gb', 'cpus-per-task':'4', 'gres':'0'}
    Mysbatch_.launchJob(cmd,scriptOptions)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', '-t', action='store_true', help='testing run with file names provided directly using -g and -n flags')
    parser.add_argument('--gem_file','-g', default=None, help='gem file to be processed')
    parser.add_argument('--nuc_file', '-n', default=None, help='nuc file to be processed')
    parser.add_argument('--modelpath', '-m', default='/gpfs/scratch/denesl01/libLTD/CP_20221228_nuclei_60xNikonSD', help='path to cellpose model, default model is CP_20221228_nuclei_60xNikonSD')
    parser.add_argument('--experiment', '-e', default=None, help='use this to run on a whole directory using a premade file list with gem_file and nuc_file columns')
    args=parser.parse_args()

    if args.test:
        print('runnning test mode')
        if args.nuc_file and args.modelpath and args.gem_file:
            launch_gem_job(args.nuc_file, args.modelpath, args.gem_file)
        else:
            print('no files provided, provide files, use --help for info')
    else:
        scratch = os.environ['SCRATCH']
        experiment = args.experiment
        file_list = os.path.join(scratch,'projects','MSC_GEMs',experiment,'file_list.csv')
        if not os.path.exists(file_list):
            print('ERROR: file list not there!')
            exit()
        file_list = pd.read_csv(file_list,index_col=0)
        print('loaded file list!')
        model_path = args.modelpath
        print('model used is: %s'%model_path)
        rawdata_path = os.path.join(scratch, 'projects', 'MSC_GEMs', experiment, 'rawdata')
        for n,line in file_list.iterrows():
            launch_gem_job(os.path.join(rawdata_path, line['nuc_file']), model_path, os.path.join(rawdata_path, line['gem_file']))