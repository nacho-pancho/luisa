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

ROW_ABS_THRES = 20    # 
ROW_REL_THRES = 4     # 4 more pixels than local baseline
COL_ABS_THRES = 1     # column has at least three pixels black
MIN_WORD_SEP = 20     # minimum separation between two words
BLOCK_ABS_THRES = 4   # minimum number of pixels in a valid block
TRAZO=1.0
COLOR=(0.0,0.2,0.4,0.1)
COLORMAP = plt.get_cmap('cool')
WIN_SIZE = 1024
MIN_ROW_HEIGHT = 20  # smallest letter I found was about 23

#---------------------------------------------------------------------------------------

def imwrite(fname,img):
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
    
def detect_bands(rmt, min_size):
    '''
    given a sequence of values, detects contiguous segments or 'bands' which are significantly
    darker than their neighborhood.
    '''
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
    #bands = list( filter( lambda x: x[1]-x[0] > min_size, bands ) )
    return bands



#---------------------------------------------------------------------------------------

def detect_rows(img,debugfile):
    # parameters of order filter
    radius  = 100
    domain  = np.arange(-radius,radius+1)
    order   = int((radius*2+1)/3)

    row_sum = np.sum(I,axis=1)
    row_sum_filtered    =  dsp.order_filter(row_sum,domain,order) 
    row_sum_thresholded = (row_sum > ROW_ABS_THRES) & ((row_sum - row_sum_filtered) > ROW_REL_THRES) #
    row_list = detect_bands(row_sum_thresholded, MIN_ROW_HEIGHT)
    band_heights = np.diff(row_list)
    h,hc = np.unique(band_heights,return_counts=True)
    if debugfile is not None:
        plt.close('all')
        fig = plt.figure(figsize=(16,10))
        plt.subplot(211)
        plt.plot(row_sum,lw=0.5)
        plt.plot(row_sum_filtered,lw=0.5)
        plt.plot(100*row_sum_thresholded,lw=1)
        plt.legend(('sum','filt','thres'))
        for b in row_list:
            plt.plot(b,(300,300),lw=1,color='black')
        plt.grid(True)
        plt.subplot(212)
        plt.bar(h,hc)
        plt.savefig(debugfile,dpi=300)
    return row_list

#---------------------------------------------------------------------------------------

def detect_blocks(img,band_list,debugfile):
    # parameters of order filter
    radius  = 100
    domain  = np.arange(-radius,radius+1)
    order   = int((radius*2+1)/3)
    #
    # cada banda es luego cortada en bloques
    # para esto mide la intensidad promedio de cada columna en la banda
    # y se recorta en donde dicha intensidad está por debajo de cierto umbral
    # (cero en este caso) y tiene un ancho suficientemente grande (más de 2 pixeles)
    #
    # aqui se detectan los bloques en cada banda en base a las 
    # intensidades de las  columnas de pixeles
    #
    block_list = list()
    band_idx   = 0
    #
    # altura de las bandas
    #
    for band in band_list:
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
        col_blocks          = detect_bands(col_sum_thresholded, MIN_WORD_SEP)
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
            block_idx = block_idx + 1
        band_idx = band_idx +1
    #    
    # devolver resultado refinado
    #
    return block_list

#---------------------------------------------------------------------------------------


def label_block(img,block_info):
    y0,x0,y1,x1 = block_info[2:]
    w = x1 - x0
    h = y1 - y0
    aspect = w / h
    block_img = img[y0:y1,x0:x1]
    #
    # trim block
    #
    ver_profile = np.sum(block_img,axis=1)
    nz = np.flatnonzero(ver_profile)
    top, bottom = nz[0], nz[-1]

    hor_profile = np.sum(block_img,axis=0)
    nz = np.flatnonzero(hor_profile)
    left, right = nz[0], nz[-1]
    trimmed_block = block_img[top:bottom,left:right] 
    tw, th  = (right-left), (bottom-top)
    tsize   = tw * th
    taspect = tw / th
    if th < h/4: # relative height w.r.t. non trimmed block
        return 'flat'
    if th < 20: # absolute height in pixels (smallest letter height ~ 20 pixels) 
        return 'flat'
    if tsize < 400: # 20x20 pixels is really small 
        return 'small'
    #
    # aspect ratio too large: this could be due to a long underlined sentence
    #
    if taspect > 25: # too long for a single word
        return 'long'
    if np.sum(trimmed_block) > 0.9*tsize: # too dark
        return 'dark'
    return 'good'

#---------------------------------------------------------------------------------------

def refine_blocks(img,block_list,debugdir):
    '''
    El método primario  de recortar bloques es muy sencillo y rápido,
    pero no es capaz de discernir si cada bloque es en sí relevante.
    
    Además puede haber bloques mal segmentados.
    
    Finalmente, se realizan estadísticas para detectar, por ejemplo
    si la página debe ser girada -- si todos los bloques tienen más o menos
    el mismo tamaño, eso es un fuerte indicador de que el documento está girado 90
    grados.

    Esta función devuelve dos listas: una con las coordenadas ajustadas y otra con etiquetas indicando
    si los bloques deben borrarse, están mal segmentados, o sin dobles.
    
    Además devuelve un valor booleano indicando si la imagen debe ser girada

    '''
    #
    # 1. marcamos bloques inútiles: vacíos, basura, o sólo con puntuación 
    #
    block_labels = [label_block(img,bi) for bi in block_list]
    lab,freq = np.unique(block_labels,return_counts=True)
    for i in range(len(lab)):
        print(lab[i],freq[i])

    return block_list,block_labels # for now, only this

#---------------------------------------------------------------------------------------

def create_block_map(img,block_list,block_labels):

    block_map = np.ones((img.shape[0],img.shape[1],3))
    block_map[:, :, 0 ] = (1-img).astype(float)
    block_map[:, :, 1 ] = block_map[:,:,0 ]
    block_map[:, :, 2 ] = block_map[:,:,0 ]

    for i in range(len(block_list)):
        info = block_list[i]
        label = block_labels[i]
        y0,x0,y1,x1 = info[2:]
        w,h = (x1-x0),(y1-y0)
        # for use with colormap 'RdYlGn' (red - yellow - green)
        cmap = cm.get_cmap('hsv')
        if label == 'good':
            c = cmap(0.50)
        elif label == 'long':
            c = cmap(0.40) 
        elif label == 'flat':
            c = cmap(0.20) 
        elif label == 'small':
            c = cmap(0.10)
        elif label == 'dark':
            c = cmap(0)
        else:
            print('Unkown label',label)
        block = block_map[y0:y1,x0:x1]
        bred   = block[:,:,0]
        bgreen = block[:,:,1]
        bblue  = block[:,:,2]
        bred[bred == 1] = c[0] 
        bgreen[bgreen == 1] = c[1] 
        bblue[bblue == 1] = c[2] 
        block_map[y0:y1,x0:x1,0] = bred
        block_map[y0:y1,x0:x1,1] = bgreen
        block_map[y0:y1,x0:x1,2] = bblue

    return block_map

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
    ap.add_argument("-m","--margin", type=int, default=100,
		    help="Cut this number of pixels from each side of image before analysis.")
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
            debugdir     = foutdir # os.path.join(foutdir,fbase + "_debug")

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
            margin = args["margin"]
            I = I[margin:-margin,margin:-margin]

            if not os.path.exists(debugdir):
                os.makedirs(debugdir)
            #
            # deteccion de bandas (renglones)
            #
            debugfile = os.path.join(foutdir,fbase + '_debug_rows.png')
            row_list = detect_rows(img,debugfile)
            #  
            # deteccion de bloques primaria
            #
            fdebug = os.path.join(foutdir,fbase + '_debug_blocks.png')
            block_list = detect_blocks(I,row_list,fdebug)
            #
            # refinamiento (se ve más de cerca cada bloque)
            #
            block_list, block_labels = refine_blocks(I,block_list,debugdir)
            #
            # guardamos lista de bloques en archivo CSV
            #
            fblocks = open(fcsvblocks,'w')
            for block_info in block_list:
                print(functools.reduce(lambda a,b: str(a) + '\t' + str(b), block_info), file=fblocks)
            fblocks.close()
            #
            # generamos imagen de analisis
            #
            block_map = create_block_map(I,block_list,block_labels)
            block_file = os.path.join(debugdir,fbase + "_blocks.png")
            plt.imsave(block_file,block_map)
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
