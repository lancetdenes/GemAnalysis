import os 
import numpy as np
from cellpose import io,models
from nd2reader import ND2Reader
import matplotlib.pyplot as plt 
from skimage.filters import threshold_isodata, median
from skimage.io import imread
def segment_nuc(nuc_file, model=None, modelpath=None, tif=False, channel=0):
    print('INITIALIZE: nucleus segmentation pipeline segment_nuc_v2.py on %s'%nuc_file)
    base_path, prefix = os.path.split(nuc_file)
    base_path,rawdata_path = os.path.split(base_path)
    print('Base path: %s'%base_path)
    if not tif:
        with ND2Reader(nuc_file) as frames:
            nuc_image = frames.get_frame(channel)
    else:
        nuc_image = imread(nuc_file)
        if len(nuc_image.shape) > 2:
            nuc_image = nuc_image[channel,:,:]
    if len(nuc_image.shape) != 2:
        print('wrong shape nucleus image')
        exit()

    if not model:
        if not modelpath:
            print('need to provide model path')
            exit()
        else:
            print('loading model from path')
            model = models.CellposeModel(pretrained_model=modelpath, gpu=True)
    if model:
        print('preloaded model provided')
    print('segmenting')
    masks, flows, styles = model.eval(nuc_image, diameter=120, progress=True)
    print('finished! found %s masks'%(np.amax(masks)))
    if not os.path.exists(os.path.join(base_path, 'npy_masks')):
        os.mkdir(os.path.join(base_path, 'npy_masks'))
    if not os.path.exists(os.path.join(base_path, 'png_masks')):
        os.mkdir(os.path.join(base_path, 'png_masks'))
    io.masks_flows_to_seg(nuc_image, masks, flows, 120, os.path.join(base_path, 'npy_masks', prefix), [0]) 
    io.save_to_png(nuc_image, masks, flows, os.path.join(base_path, 'png_masks', prefix))
    nuc_mask = np.where(masks>0, 1, 0)
    nuc_smooth = median(nuc_image, footprint=np.ones((10,10)))
    fig,(ax1,ax2,ax3)=plt.subplots(1,3)
    ax1.imshow(nuc_mask, cmap='Greys')
    ax2.imshow(nuc_smooth > threshold_isodata(nuc_smooth), cmap='Greys')
    ax3.imshow(nuc_image, cmap='Greys')
    ax3.set_title('original')
    ax1.set_title('cellpose')
    ax2.set_title('threshold')
    if not os.path.exists(os.path.join(base_path, 'compare_segs')):
        os.mkdir(os.path.join(base_path, 'compare_segs'))
    plt.savefig(os.path.join(base_path, 'compare_segs', prefix+'.png'))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--nuc_file', help='need to provide the path the nucleus file')
    parser.add_argument('--modelpath', default=None, type=str, help='provide a path to load a model in each script here')
    parser.add_argument('--tif', action='store_true', help='whether input file is nd2 or tiff, for read in purposes')
    args=parser.parse_args()
    if args.modelpath:
        model = models.CellposeModel(pretrained_model=args.modelpath, gpu=True)
        segment_nuc(nuc_file=args.nuc_file, model=model, tif=args.tif)
    else:
        print('need to provide model path!')
    