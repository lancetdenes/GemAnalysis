import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience
import pims_nd2
from pims_nd2 import ND2_Reader
import trackpy as tp
import os


def process_gem(infile, minmass_parameter, frame_rate, outfile):
    #minmass = 100 for 20ms images and 70 for 10 ms images
    #frame rate = 50 fps for 20ms images and 100 for 10 ms images
    frames = ND2_Reader(infile)
    f = tp.batch(frames, 9, minmass=float(minmass_parameter), separation=3, processes=8)
    t = tp.link(f, 5, memory=3)
    t1 = tp.filter_stubs(t, 10)
    t1.to_csv(outfile+'_tracks.csv')
    em = tp.emsd(t1, 0.1341799, float(frame_rate))
    result = tp.utils.fit_powerlaw(em.iloc[:10])
    deff = result['A']/4
    with open(outfile+'.txt', 'w') as f:
        f.write(infile +','+str(deff.values[0]))


#process_gem('/gpfs/scratch/denesl01/gem_images/20220506_msc_diff_cytogem/sparse_control_immediate/10ms_064.nd2', 70, 100, 'a.txt')
