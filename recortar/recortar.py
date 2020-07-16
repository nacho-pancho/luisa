#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 17:22:41 FIRST_CROP18

@author: nacho
"""
#import os.path
import sys
import numpy as np
from PIL import Image,ImageOps,ImageChops,ImageDraw
import scipy.ndimage as skimage
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
import scipy.signal as dsp
import time
import argparse
import math
import functools # functional programming tools

#---------------------------------------------------------------------------------------

ROW_ABS_THRES = 100   # row has 2.5% of its pixels black
ROW_REL_THRES = 4     # 4 more pixels than local baseline
COL_ABS_THRES = 1     # column has at least three pixels black
MIN_WORD_SEP = 10     # minimum separation between two words
BLOCK_ABS_THRES = 4   # minimum number of pixels in a valid block
TRAZO=1.0
COLOR=(0.0,0.2,0.4,0.1)
COLORMAP = plt.get_cmap('cool')
WIN_SIZE = 1024
MIN_BAND_HEIGHT = 20  # smallest letter I found was about 23

#---------------------------------------------------------------------------------------

def imwrite(fname,img):
    #img.save(fname,compression=COMP)
    img.save(fname)

#---------------------------------------------------------------------------------------

def imrot(img,angle):
    w,h = img.size
    return img.rotate(angle, resample=Image.NEAREST,expand=True,fillcolor=1)

#---------------------------------------------------------------------------------------

def imread(fname):
    img = Image.open(fname)
    return img

#---------------------------------------------------------------------------------------
    
def detect_bands(rmt):
    dif = np.int8(rmt[1:]) - np.int8(rmt[:-1])
    upidx = np.flatnonzero(dif > 0) + 1
    dnidx = np.flatnonzero(dif < 0) + 1 
    if len(upidx) < 2:
        return list()
    
    if len(dnidx) < 2:
        return list()
    
    if dnidx[0] < upidx[0]: # lo primero que ocurre es flanco de bajada
        dnidx = dnidx[1:]
    if len(upidx) > len(dnidx):
        upidx = upidx[:-1]
        
    bands = list(zip(upidx,dnidx))
    bands = list( filter( lambda x: x[1]-x[0] > MIN_BAND_HEIGHT, bands ) )
    return bands



#---------------------------------------------------------------------------------------
def cut_blocks(img,debugdir):

    radius  = 100
    row_sum = np.sum(I,axis=1)
    order   = int((radius*2+1)/3)
    domain  = np.arange(-radius,radius+1)
    row_sum_filtered    =  dsp.order_filter(row_sum,domain,order) 
    row_sum_thresholded = (row_sum > ROW_ABS_THRES) & ((row_sum - row_sum_filtered) > ROW_REL_THRES) #
    bands = detect_bands(row_sum_thresholded)
    band_heights = np.diff(bands)
    h,hc = np.unique(band_heights,return_counts=True)
    #
    # cada banda es luego cortada en bloques
    # para esto mide la intensidad promedio de cada columna en la banda
    # y se recorta en donde dicha intensidad está por debajo de cierto umbral
    # (cero en este caso) y tiene un ancho suficientemente grande (más de 2 pixeles)
    #
    # aqui se detectan los bloques en cada banda en base a las 
    # intensidades de las  columnas de pixeles
    #
    block_map = (1-np.copy(I)).astype(float)
    block_list    = list()
    band_idx  = 0
    #
    # altura de las bandas
    #
    for band in bands:
        y0 = band[0]
        y1 = band[1]
        band = I[y0:y1, :]
        col_sum = np.sum(band,axis=0)
        #
        col_sum_thresholded = col_sum >= COL_ABS_THRES
        #
        # filtro de mediana para evitar separaciones entre palabras
        #
        col_sum_thresholded = dsp.medfilt(col_sum_thresholded, kernel_size=2*MIN_WORD_SEP+1)
        col_blocks          = detect_bands(col_sum_thresholded)
        block_idx           = 0
        for block in col_blocks:
            x0 = block[ 0 ]
            x1 = block[ 1 ]
            block_info = (band_idx,block_idx,y0,x0,y1,x1)
            #
            # filtramos bloques demasiado vacios y demasiado lleno
            #
            Ib = I[y0:y1,x0:x1]
            bsum = np.sum(Ib)
            if  (bsum >= BLOCK_ABS_THRES) & (bsum < Ib.size - BLOCK_ABS_THRES):
                # mismo formato que modulo C : i0, j0, i1, j1, i0 orig, j0 orig, i1 orig, j0 orig, row idx, block idx
                block_list.append(block_info)
                block_map[y0:y1,x0:x1] = block_map[y0:y1,x0:x1] * 0.75
            block_idx = block_idx + 1
        band_idx = band_idx +1

    if debugdir is not None:
        plt.close('all')
        fig = plt.figure(figsize=(9,12))
        plt.subplot(221)
        plt.plot(row_sum,lw=0.5)
        plt.plot(row_sum_filtered,lw=0.5)
        plt.plot(100*row_sum_thresholded,lw=1)
        plt.legend(('sum','filt','thres'))

        fimgbands  = os.path.join(debugdir,fbase + '_bands.png')
        fimgblocks = os.path.join(debugdir,fbase + '_blocks.png')
        png_file = os.path.join(debugdir,"_debug.png")
        col_sum = np.sum(I,axis=0)
        col_sum_filtered =  dsp.order_filter(col_sum,domain,order) 
        col_sum_thresholded = (col_sum > ROW_ABS_THRES) & ((col_sum - col_sum_filtered) > ROW_REL_THRES) #
        plt.subplot(222)
        plt.plot(col_sum,lw=0.5)
        plt.plot(col_sum_filtered,lw=0.5)
        plt.plot(100*col_sum_thresholded,lw=0.5)
        plt.legend(('sum','filt','thres'))
        plt.subplot(223)
        plt.bar(h,hc)
        plt.subplot(224)
        plt.imshow(img,cmap=cm.gray)
        plt.savefig(png_file,dpi=300)
        plt.show()
        plt.close(fig)
        block_file = os.path.join(debugdir,"block_map.png")
        plt.imsave(block_file,(255*block_map).astype(np.uint8),cmap=cm.gray)
    #    
    # devolver resultado refinado
    #
    return block_list

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--prefix", type=str, default="../datos",
		    help="path prefix  where to find prealigned files")
    ap.add_argument("-o","--outdir", type=str, default="../results",
		    help="where to store results")
    ap.add_argument("-l","--list", type=str, default="../datos/r0566a.list",
		    help="text file where input pre-aligned files are specified")
    ap.add_argument("-f","--force", action="store_true",
		    help="Forces the output to be overwritten even if it exists.")
    #
    # INICIALIZACION
    #
    args      = vars(ap.parse_args())
    print(args)
    prefix    = args["prefix"]
    outdir    = args["outdir"]
    list_file = args["list"]
    #
    # crear estructuras de directorios
    #
    with open(list_file) as fl:
        #
        # inicializacion de memoria
        #
        errors = list()
        nimage = 0
        t0 = time.time()
        for relfname in fl:
            #
            # proxima imagen
            #
            nimage = nimage + 1        
            #
            # ENTRADA Y SALIDA
            #
            # nombres de archivos de entrada y salida
            #
            relfname     = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext   = os.path.splitext(fname)
            foutdir      = os.path.join(outdir,reldir)
            debugdir     = os.path.join(foutdir,fbase + "_debug")

            fcsvblocks = os.path.join(foutdir,fbase + '.blocks')
            
            print(f'#{nimage} relfname={relfname} outdir={outdir} fname={fname} fbase={fbase}')
            #
            # creamos carpeta de destino si no existe
            #
            fpath = fname[:(fname.find('/')+1)]
            if not os.path.exists(foutdir):
                os.makedirs(foutdir)

            if not args["force"] and os.path.exists(fcsvblocks):
                print('CACHED.')
                continue

            img = imread(os.path.join(prefix,relfname))
            I = 1 - np.array(img)
            if not os.path.exists(debugdir):
                os.makedirs(debugdir)
            #
            # deteccion de bloques
            #
            block_list = cut_blocks(img,debugdir)
            #
            # guardamos lista de bloques en archivo CSV
            #
            fblocks = open(fcsvblocks,'w')
            for block_info in block_list:
                print(functools.reduce(lambda a,b: str(a) + '\t' + str(b), block_info), file=fblocks)
            fblocks.close()
            #
            # fin loop principal
            #

        if nimage > 0:
            meandt = time.time() / nimage
            print(f'Average time per image: {meandt} seconds. ')

        nerr = len(errors)
        if nerr > 0:
            print(f'ERROR AL PROCESAR {nerr} ARCHIVOS:')
            for l in errors:
                print(l)
        #
        # fin main
        #
#---------------------------------------------------------------------------------------
