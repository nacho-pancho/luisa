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
import os
import config
import scipy.signal as dsp
import time
import argparse
import math

#---------------------------------------------------------------------------------------

ROW_ABS_THRES = 100    # row has 2.5% of its pixels black
ROW_REL_THRES = 4     # 4 more pixels than local baseline
COL_ABS_THRES = 1     # column has at least three pixels black
MIN_WORD_SEP = 3      # minimum separation between two words
BLOCK_ABS_THRES = 4   # minimum number of pixels in a valid block
TRAZO=1.0
COLOR=(0.0,0.2,0.4,0.1)
COLORMAP = plt.get_cmap('cool')
WIN_SIZE = 1024

#---------------------------------------------------------------------------------------

def imwrite(fname,img):
    img.save(fname,compression=config.COMP)

#---------------------------------------------------------------------------------------

def imrot(img,angle):
    w,h = img.size
    #center = (int(w/2),int(h/2))
    return img.rotate(angle, resample=Image.NEAREST,expand=True,fillcolor=1)

#---------------------------------------------------------------------------------------

def imread(fname):
    img = Image.open(fname)
    if not 274 in img.tag_v2:
        return img
    if img.tag_v2[274] == 8: # regression bug in PILLOW for TIFF images
        img = imrot(img,-90)
    return img


#---------------------------------------------------------------------------------------

def orientation_score(img, debug_prefix = None):
        w,h = img.size
        d = WIN_SIZE
        box = (int((w-d)/2), int((h-d)/2), int((w+d)/2), int((h+d)/2)) #x0,y0,x1,y1
        rot = img
        #rot = imrot(img,angle).crop(box)
        Mrot = 1-np.asarray(rot.crop(box))
        profile = np.sum(Mrot,axis=1)
        # 
        # correlogram
        #
        # normalize
        profile = profile - np.mean(profile)
        profile = profile / np.linalg.norm(profile)
        # compute correlation
        corr = dsp.correlate(profile,profile)
        # find first local minimum below 0
        offset = np.argmax(corr)        
        corr = corr[(offset+1):(offset+201)]
        #
        # primer intento minimo global: no anda siempre bien
        # xmin = np.argmin(corr)
        #
        # segundo intento: primer minimo bajo 0
        #
        dp = np.diff(corr)
        gut = (dp > 0) * (corr[:-1] < 0)
        idx = np.flatnonzero(gut)
        if len(idx) > 0:
            xmin = idx[0]
        else:
            xmin = 199
        ymin = corr[xmin]
        if xmin < 198:
            ymax = np.max(corr[(xmin+1):])
        else:
            ymax = 0
        score = ymax - ymin
        # cuarto intento: excursion entre primer minimo y primer maximo
        #
        #  tercer variacion total del correlograma
        #
        #score = np.sum(np.abs(dp))
        if debug_prefix is not None:
            plt.close('all')
            plt.figure(figsize=(10,10))
            plt.plot(profile)
            plt.grid(True)
            plt.savefig(f'{debug_prefix}_profile.svg')
            plt.close('all')
            plt.figure(figsize=(10,10))
            plt.plot(corr)
            plt.axis((0,200,-1,1))
            plt.plot(xmin,ymin,'*')
            plt.grid(True)
            plt.title(f"correlogram min = ( {xmin}, {ymin:5.3f} ) score = {score} ")
            plt.savefig(f'{debug_prefix}_cgram.svg')
            imwrite(f'{debug_prefix}.tif',img)
        
        return score
            
#---------------------------------------------------------------------------------------

def alignment_score(img, angle, debug_prefix = None):
    # 
    # luego de rotar, recortamos una zona que sabemos siempre
    # va a estar bien definida. 
    #
    w,h = img.size
    margin = int(min(w,h)*0.1)
    dw = w - 2*margin
    dh = h - 2*margin
    x0 = int((w-dw)/2)
    x1 = int((w+dw)/2)
    y0 = int((h-dh)/2)
    y1 = int((h+dh)/2)
    box = (x0, y0, x1, y1)
    rot = imrot(img,angle).crop(box)
    Mrot = 1-np.asarray(rot)
    profile = np.sum(Mrot,axis=1)
    # get rid of solid lines
    trim = int(0.8*dw)
    trom = 0
    trimmed_profile = np.copy(profile)
    trimmed_profile[profile > trim] = trim # borrar lineas solidas
    variation = np.abs(np.diff(trimmed_profile))
    trimmed_variation = variation
    #trimmed_variation[variation < trom] = 0.0 # borrar ruidito
    l2 = np.linalg.norm(trimmed_variation)
    l1 = np.sum(trimmed_variation)
    score = l2/l1

    if debug_prefix is not None:
        plt.close('all')
        plt.figure(10)
        plt.plot(profile)
        plt.plot(trimmed_profile)
        plt.plot(variation)
        plt.plot(trimmed_variation)
        plt.axis((0,dw,0,1000))
        plt.grid(True)
        plt.legend(('profile','trimmed profile','variation','trimmed variation'))
        plt.title(f'angle={angle:6.2f} l2={l2:8.2f} l1={l1:8.2f} l2/l1={score:7.5f}')
        if angle < 0:
            sgn = "-"
            aangle = -angle
        else:
            sgn = "+"
            aangle = angle
        #imwrite(f'{debug_prefix}_a{sgn}{aangle:4.2f}.tif',rot)
        #plt.savefig(f'{debug_prefix}_a{sgn}{aangle:4.2f}.svg')
    
    return score
    
#---------------------------------------------------------------------------------------

def local_angle_search(work_img, min_angle, max_angle, delta_angle, debug_prefix = None):
    best_angle = min_angle
    best_score = alignment_score(work_img,best_angle)

    angles = np.arange(min_angle,max_angle+delta_angle,delta_angle)
    scores = np.zeros(len(angles))
    for i in range(len(angles)):
        scores[i] = alignment_score(work_img,angles[i], debug_prefix)
    best_i = np.argmax(scores)
    best_score = scores[best_i]
    if best_score == 0.0:
        best_angle = (max_angle + min_angle)/2
    else:
        best_angle = angles[best_i]
    print(f'delta {delta_angle:5.2f} best {best_angle:5.2f} score {best_score:7.5f}')

    delta_angle = delta_angle / 2
    if delta_angle >= 0.25:
        if best_i == 0: # best at the border!
            max_angle = angles[1]
            min_angle = max_angle-delta_angle*2 
        elif best_i == len(angles)-1: # best at the border
            min_angle = angles[-2]
            max_angle = min_angle + delta_angle*2
        else: # best in the middle
            min_angle = angles[best_i-1]
            max_angle = angles[best_i+1]                
        return local_angle_search(work_img, min_angle, max_angle, delta_angle, debug_prefix)
    else:
        return best_angle,best_score

#---------------------------------------------------------------------------------------

def seleccionar_zona(orig_img,debug_prefix):
    '''
    elige un area cuadrada que tenga bastante negro y blanco
    para hacer la alineacion 
    '''
    w,h = orig_img.size
    d = min(w,h)
    MARGIN=600
    #return (MARGIN,MARGIN,d-MARGIN,d-MARGIN)
    if w < h:
        R = int(np.floor(w/4))      # size of outer rectangle
    else:
        R = int(np.floor(h/4))      # size of outer rectangle
    orig_mat = np.asarray(orig_img)
    scores = list()
    boxes  = list()
    #
    # probamos qué cuadrado de WIN_SIZExWIN_SIZE
    # es el mas adecuado para analizar la alineacion
    #
    for i in (1,2,3):
        js = list()
        js.append(2)
        for j in js:
            x0 = int(np.floor(j*w/4)) - R
            x1 = int(np.floor(j*w/4)) + R
            y0 = int(np.floor(i*h/4)) - R
            y1 = int(np.floor(i*h/4)) + R
            p = np.mean(orig_mat[y0:y1,x0:x1])
            box = (x0,y0,x1,y1)
            scores.append(p*(1-p))
            boxes.append(box)

    best_idx = np.argmax(scores)
    print("scores",scores)
    print("mejor zona ",best_idx,":",boxes[best_idx])
    #
    # como dato adicional, si el bloque de más arriba es
    # significativamente más oscuro que los otros,
    # entonces es muy probable que el documento sea
    # un retrato.
    #
    if scores[0] > 3*max(scores[1],scores[2]):
        hint = True
    else:
        hint = False
    return (boxes[best_idx], hint)

def alinear_imagen(orig_img, debug_prefix):
    w,h = orig_img.size
    #
    # elegimos una zona cuadrada que tenga suficiente informacion
    #
    box, hint = seleccionar_zona(orig_img,debug_prefix)
    img = orig_img.crop(box)
    imwrite(debug_prefix + "_cropped.tif",img)
    #
    # busqueda por biparticion de mejores angulos tanto en retrato como apaisado
    #
    delta_angle = 1
    best_portrait_angle, best_portrait_score   = local_angle_search(img, -5,5, delta_angle, debug_prefix+"_portrait")
    aligned_portrait  = imrot(img,best_portrait_angle)
    #
    # si tenemos un indicio fuerte (hint = True) de que la imagen es retrato,
    # ya damos ese caso por cierto
    #
    if hint:
        print("orientation PORTRAIT (via HINT) correction ",best_portrait_angle)
        return imrot(orig_img,best_portrait_angle)

    #
    # repetimos el proceso para la imagen apaisada
    #
    img90 = imrot(img,-90)
    best_landscape_angle, best_landscape_score = local_angle_search(img90,-5,5, delta_angle, debug_prefix+"_landscape")
    best_landscape_angle = best_landscape_angle - 90
    #
    # la orientacion se define con otro criterio mas robusto
    # que el de la alineacion
    #
    aligned_landscape = imrot(img,best_landscape_angle)
    portrait_score    = orientation_score(aligned_portrait, debug_prefix+"_portrait")
    landscape_score   = orientation_score(aligned_landscape, debug_prefix+"_landscape")
    print("portrait score",portrait_score)
    print("landscape score",landscape_score)
    if  landscape_score > portrait_score:
        best_angle = best_landscape_angle
        print("orientation LANDSCAPE correction ",best_landscape_angle + 90)
    else:
        best_angle = best_portrait_angle
        print("orientation PORTRAIT  correction ",best_portrait_angle)

    return imrot(orig_img,best_angle)
    
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
    bands = list( filter( lambda x: x[1]-x[0] > 4, bands ) )
    return bands

#---------------------------------------------------------------------------------------

def plot_stats(I,MR,MC,row_sum,row_sum_filtered,row_sum_thresholded):
    #plt.figure(FIRST_CROP0,dpi=160,figsize=(FIRST_CROP,15))
    plt.clf()
    plt.subplot(221)
    plt.title('Intensidades de fila')
    plt.plot(row_sum, lw=TRAZO)
    plt.plot(row_sum_filtered, lw=TRAZO)
    plt.plot(ROW_ABS_THRES*row_sum_thresholded, lw=TRAZO)
    plt.legend(('mean','filt','thres'))
    plt.grid(True)
    plt.subplot(222)
    plt.imshow(I)
    plt.subplot(223)
    plt.imshow(MR)
    plt.subplot(224)
    plt.imshow(MC)
    plt.show()

#---------------------------------------------------------------------------------------

if __name__ == '__main__':

    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--prefix", type=str, default="../data/orig",
		    help="path prefix  where to find files")
    ap.add_argument("-o","--outdir", type=str, default="../results",
		    help="where to store results")
    ap.add_argument("-l","--list", type=str, default="../data/test.list",
		    help="text file where input files are specified")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    print(args)
    prefix = args["prefix"]
    outdir = args["outdir"]
    list_file = args["list"]

    #
    # crear estructuras de directorios
    #
    with open(list_file) as fl:
        # #
        # # inicializacion de memoria
        # #
        errors = list()
        radius = 40
        nimage = 0
        # kernel = dsp.gaussian(radius*2+1,radius/2)
        # kernel = kernel*(ROW_REL_THRES/np.sum(kernel))
        #
        # bucle principal: analiza cada hoja
        #
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
            relfname = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext = os.path.splitext(fname)
            foutdir = os.path.join(outdir,reldir)
            debugdir = os.path.join(foutdir,fbase + "_debug")
            
            fimgbands  = os.path.join(foutdir,fbase + '_bands' + config.EXT)
            fimgblocks = os.path.join(foutdir,fbase + '_blocks' + config.EXT)
            fcsvblocks = os.path.join(foutdir,fbase + '.blocks')
            
            print(f'#{nimage} relfname={relfname} outdir={outdir} fname={fname} fbase={fbase}')
            #
            # creamos carpeta de destino si no existe
            #
            fpath = fname[:(fname.find('/')+1)]
            if not os.path.exists(foutdir):
                os.system(f'mkdir -p \'{foutdir}\'')
            #
            # alignment
            #
            aligned_name = os.path.join(foutdir,fname)
            if not os.path.exists(aligned_name):
                Iorig = imread(os.path.join(prefix,relfname))
                if not os.path.exists(debugdir):
                    os.system(f'mkdir -p \'{debugdir}\'')
                copy_name = os.path.join(debugdir, 'orig' + config.EXT)
                imwrite(copy_name,Iorig)

                Ialign = alinear_imagen(Iorig,os.path.join(debugdir,"alinear"))

                imwrite(aligned_name,Ialign)
                I = 1-np.asarray(Ialign)
            else:
                I = 1-np.asarray(imread(aligned_name))
            #
            # detectamos bandas horizontales
            #
            row_sum = np.sum(I,axis=1)
            order = int((radius*2+1)/3) # 30%
            domain = np.arange(-radius,radius+1)
            row_sum_filtered =  dsp.order_filter(row_sum,domain,order) 
            #row_sum_filtered[:] = dsp.fftconvolve(row_sum,kernel,mode='same')
            row_sum_thresholded = (row_sum > ROW_ABS_THRES) & ((row_sum - row_sum_filtered) > ROW_REL_THRES) #
            plt.close('all')
            plt.figure(1)
            plt.plot(row_sum,lw=0.5)
            plt.plot(row_sum_filtered,lw=0.5)
            plt.plot(100*row_sum_thresholded,lw=0.5)
            plt.legend(('sum','filt','thres'))
            if debugdir is not None:
                png_file = os.path.join(debugdir,"profile_h.png")
                plt.savefig(png_file,dpi=300)
                col_sum = np.sum(I,axis=0)
                col_sum_filtered =  dsp.order_filter(col_sum,domain,order) 
                col_sum_thresholded = (col_sum > ROW_ABS_THRES) & ((col_sum - col_sum_filtered) > ROW_REL_THRES) #
                plt.close('all')
                plt.figure(1)
                plt.plot(col_sum,lw=0.5)
                plt.plot(col_sum_filtered,lw=0.5)
                plt.plot(100*col_sum_thresholded,lw=0.5)
                plt.legend(('sum','filt','thres'))
                png_file = os.path.join(debugdir,"profile_v.png")
                plt.savefig(png_file,dpi=300)

            bands = detect_bands(row_sum_thresholded)
            #
            # cada banda es luego cortada en bloques
            # para esto mide la intensidad promedio de cada columna en la banda
            # y se recorta en donde dicha intensidad está por debajo de cierto umbral
            # (cero en este caso) y tiene un ancho suficientemente grande (más de 2 pixeles)
            #
            #
            # aqui se detectan los bloques en cada banda en base a las 
            # intensidades de las  columnas de pixeles
            #
            block_map = Image.fromarray(128*(1-I.astype(np.uint8)),mode='L')
            canvas = ImageDraw.Draw(block_map)
            fhblocks = open(fcsvblocks,'w')
            blocks = list()
            band_idx = 0
            for b in bands:
                w = b[1]-b[0]
                band = I[b[0]:b[1], :]
                col_sum = np.sum(band,axis=0)
                #
                col_sum_thresholded = col_sum >= COL_ABS_THRES
                #
                # filtro de mediana para evitar separaciones entre palabras
                #
                col_sum_thresholded = dsp.medfilt(col_sum_thresholded, kernel_size=2*MIN_WORD_SEP+1)
                col_blocks = detect_bands(col_sum_thresholded)
                #print('band ',b,'blocks:',col_blocks)
                block_idx = 0
                for block in col_blocks:
                    box = (band_idx,block_idx,b[0],block[0],b[1],block[1])
                    #
                    # filtramos bloques demasiado vacios y demasiado lleno
                    #
                    Ib = I[b[0]:b[1],block[0]:block[1]]
                    bsum = np.sum(Ib)
                    if  (bsum >= BLOCK_ABS_THRES) & (bsum < Ib.size - BLOCK_ABS_THRES):
                        # mismo formato que modulo C : i0, j0, i1, j1, i0 orig, j0 orig, i1 orig, j0 orig, row idx, block idx
                        print(b[0], block[0], b[1], block[1], 4*b[0], 4*block[0], 4*b[1], 4*block[1], band_idx, block_idx, file=fhblocks)
                        blocks.append(box)
                        canvas.rectangle((block[0],b[0],block[1],b[1]),fill=(200))
                    block_idx = block_idx + 1
                band_idx = band_idx +1
            
            fhblocks.close()
            block_file = os.path.join(debugdir,"block_map.png")
            block_map.save(block_file)
            #print('(OK)')
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
