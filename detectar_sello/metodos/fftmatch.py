#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Plantilla de archivo para trabajar en los distintos proyectos de LUISA
Esta plantilla no hace mas que abrir una lista de archivos, leerlos uno
por uno y guardar una copia en un directorio especificado.

Los requisitos mínimos para correr este script es tener instalados
los siguientes paquetes de Python 3.
Se recomienda utilizar el manejador de paquetes de Python3, pip3:

numpy
pillow 
matplotlib

Se recomienda también el siguiente paquete:

scipy

@author: nacho
"""
#
# # paquetes base de Python3 (ya vienen con Python)
#
# import os
import os.path
import sys
import time
import argparse
import math
import csv
import scipy.signal as dsp

#
# bibliotecas adicionales necesarias
#
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from scipy import ndimage, misc
#from console_progressbar import ProgressBar # pip3 install console-progressbar
from skimage import transform # pip3 install scikit-image

verbose = False

#---------------------------------------------------------------------------------------

def imread(fname):
    img = Image.open(fname)
    return 1-np.asarray(img,dtype=np.uint8)

#---------------------------------------------------------------------------------------

def imsave(fname,img):
    aux = img.copy()
    aux -= np.min(aux)
    aux = np.uint8(255*aux/max(1e-10,np.max(aux)))
    Image.fromarray(aux).save(fname)

#---------------------------------------------------------------------------------------

def reducir(a,razon):
    ares =  transform.rescale(a.astype(np.float),razon,order=1,mode='constant',cval=0,anti_aliasing=True)
    return ares

#---------------------------------------------------------------------------------------

def ampliar(a,shape):
    return  transform.resize(a,shape,mode='constant',cval=0,anti_aliasing=True)

#---------------------------------------------------------------------------------------

def show_image(img):
    plt.figure(figsize=(10,10))
    plt.imshow(img)
    plt.colorbar()

#---------------------------------------------------------------------------------------

def show_match(I,S,i,j):
    img  = I.copy()
    seal = S.copy()
    ms,ns =  seal.shape
    m,n  = img.shape
    i0 = int(i)-ms//2
    i1 = i0 + ms
    j0 = int(j)-ns//2
    j1 = j0 + ns
    if i0 < 0:
        seal = seal[-i0:,:]
        i0 = 0
    if j0 < 0:
        seal = seal[:,-j0:]
        j0 = 0
    if i1 > m:
        seal = seal[:m-i1,:]
        i1 = m
    if j1 > n:
        seal = seal[:,:n-j1]
        j1 = n
    img[i0:i1,j0:j1] += 2*seal
    show_image(img)

def correlate(img,sello):
    return dsp.correlate( img, sello, method="fft",mode='same' ) 

#---------------------------------------------------------------------------------------

def detector_fft_un_sello(image_scales,seal_scales):
    #
    # factores de normalizacion
    #
    best_score = 0
    base_scale = np.max(list(seal_scales.keys()))
    base_image,_ = image_scales[base_scale]
    base_shape = base_image.shape
    nscales = len(seal_scales.keys())
    Gtotal    =  np.zeros((*base_shape,nscales))
    nscale = 0
    for s in seal_scales.keys():
        Is,Isn  = image_scales[s]
        m,n = Is.shape
        seal_rotations = seal_scales[s]
        best_score = 0
        best_angle = 0
        best_i = 0
        best_j = 0
        best_G = 0
        for a in seal_rotations.keys():
            ssr = seal_rotations[a]
            G = correlate( Is, ssr ) / Isn 
            limax = np.argmax( G )
            imax  = limax // n
            jmax  = limax - imax*n
            gmax = G[imax,jmax]
            if best_score < gmax:
                best_score = gmax
                best_angle = a
                best_i     = int(imax*base_scale/s)
                best_j     = int(jmax*base_scale/s)
                best_G     = G.copy()
        if verbose:
            print(f"\tscale {s:7.5f} angle {best_angle:5.2f} maximum {best_score:5.3f} at ({best_i:5d},{best_j:5d})")
        Gtotal[:,:,nscale] = ampliar(best_G,base_shape)
        nscale += 1
    Gtotal = np.median(Gtotal,axis=2)
    limax = np.argmax( Gtotal )
    imax  = limax // base_shape[1]
    jmax  = limax - imax*base_shape[1]
    best_score = Gtotal[imax,jmax]
    return best_score
    
#---------------------------------------------------------------------------------------

def detector_fft(I,seals,args):
    cachedir = args["cachedir"]
    imgname  = args["name"]
    score_cache = os.path.join(cachedir,f"{imgname}-scores.npy")
    if os.path.exists(score_cache):
        scores = np.load(score_cache)
        return scores

    if not os.path.exists(cachedir):
        os.makedirs(cachedir)
    maxw = 0 
    maxh = 0
    scales = list()
    scales.append(0.25)
    angles = np.arange(-3,3.5,0.5)
    #print("Precomputing scales and rotations")
    #
    # tamaño comun para todos los sellos
    #
    for i in range(len(seals)):
        if seals[i].shape[0] > maxh:
            maxh = seals[i].shape[0]
        if seals[i].shape[1] > maxw:
            maxw = seals[i].shape[1]
    #jp
    # precalcular imagenes escaladas y normalizadas
    #
    # usamos una convolucion para estimar la norma 2 de cada patch de la imagen
    # es la raiz de la suma del cuadrado de los pixeles en cada patch
    image_scales = dict()
    for s in scales:
        maxhs = int(np.ceil(1.1*maxh*s))
        maxws = int(np.ceil(1.1*maxw*s))
        plantilla1 = np.ones((maxhs,maxws))
        fcache = os.path.join(cachedir,f"{imgname}-scale{s:5.3f}.npy")
        if not os.path.exists(fcache):
            Is =  reducir( I, s )
            Isn  = correlate( Is**2, plantilla1 )
            Isn = np.sqrt(np.maximum(Isn,1e-16))
            np.save(fcache,Is)            
            fcache = os.path.join(cachedir,f"{imgname}-scale{s:5.3f}.jpg")
            imsave(fcache,Is)
            fcache = os.path.join(cachedir,f"{imgname}-scale{s:5.3f}-norm.npy")
            np.save(fcache,Isn)            
            fcache = os.path.join(cachedir,f"{imgname}-scale{s:5.3f}-norm.jpg")
            imsave(fcache,Isn)
            image_scales[s] = (Is, Isn)            
        else:
            Is = np.load(fcache)
            fcache = os.path.join(cachedir,f"{imgname}-scale{s:5.3f}-norm.npy")
            Isn = np.load(fcache)
            image_scales[s] = (Is, Isn)            
    #
    # precalcular sellos escalados, rotados y normalizados
    #
    nseals = len(seals)
    scores = list()
    for i in range( nseals ):
        #print(f"seal {i} of {nseals}")
        seal = seals[ i ]
        seal_scales = dict()
        for s in scales:
            #print(f"\tscale {s}")
            seal_scales[s] = dict()
            maxhs = int(np.ceil(1.1*maxh*s))
            maxws = int(np.ceil(1.1*maxw*s))
            for a in angles:
                aa = abs(a)
                if a < 0:
                    sgn = '-'
                else:
                    sgn = '+'
                fcache = os.path.join(cachedir,f"sello{i:02d}-scale{s:5.3f}-angle{sgn}{aa:06.3f}.npy")
                if os.path.exists(fcache):
                    seal_scales[s][a] = np.load(fcache)
                else:    
                    ssr = reducir( ndimage.rotate( seal, a ), s ) 
                    sh,sw = ssr.shape
                    sn    = 1.0 / np.linalg.norm( ssr.ravel() )                
                    aux = np.zeros((maxhs,maxws))
                    ioff  = ( maxhs - sh ) // 2
                    joff  = ( maxws - sw ) // 2
                    #print(maxhs,ioff,sh,maxws,joff,sw)
                    aux[ ioff:ioff+sh, joff:joff+sw ] = ssr*sn
                    seal_scales[s][a] = aux
                    np.save(fcache,aux)
                    fcache = os.path.join(cachedir,f"sello{i:02d}-scale{s:5.3f}-angle{sgn}{aa:6.3f}.png")
                    imsave(fcache,aux)
        score = detector_fft_un_sello( image_scales, seal_scales )
        if verbose:
            print( f"sello {i:3d} score {score:5.3f}" )
        scores.append(score)
    np.save(score_cache,scores)
    return scores
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="../datos",
      help="path prefix  where to find files")
    ap.add_argument("-c", "--cachedir", type=str, default="../cache",
      help="path prefix  where to find cache files")
    ap.add_argument("-o","--outdir", type=str, default="../results",
      help="where to store results")
    ap.add_argument("-l","--list", type=str, default="../datos/r0566.list",
      help="text file where input files are specified")
    ap.add_argument("-s","--seals", type=str, default="../datos/sellos.list",
      help="text file with the list of input seal image files")
    ap.add_argument("-t","--truth", type=str, default="../datos/sellos_gt.csv",
      help="ground truth file.")
    args = vars(ap.parse_args())
    #
    # INICIALIZACION
    #
    prefix = args["datadir"]
    outdir = args["outdir"]
    cachedir = args["cachedir"]
    #
    # cargamos sellos
    #
    seals_file = args["seals"]
    sellos = list()
 #
 # grond truth
 #
    ground_truth = dict()
    gtfname = args['truth']
    with open(gtfname,'r') as gtfile:
     csvreader = csv.reader(gtfile, delimiter=' ')
     for row in csvreader:
      key = row[0]
      ground_truth[key] = [ int(r) for r in row[1:-1]] # ultimo es espacio 
 
    with open(seals_file) as fl:
        nimage = 0
        for relfname in fl:
            nimage = nimage+1
            relfname = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext = os.path.splitext(fname)
            input_fname = os.path.join(prefix,relfname)
            #print(f'cargando sello #{nimage} fname={input_fname}')
            sello = imread(input_fname)
            sellos.append(sello)
    #
    # armamos lista de detectores a evaluar
    #
    detectores = list()
    detectores.append(detector_fft)

    #
    # abrimos lista de archivos
    # la lista es un archivo de texto con un nombre de archivo
    # en cada linea
    #
    list_file  = args["list"]
    all_scores = list()
    all_gt     = list()
    with open(list_file) as fl:
        t0 = time.time()
        nimage = 0
        #
        # repetimos una cierta operación para cada archivo en la lista
        #
        for relfname in fl:
            relfname = relfname.split('.')[0]+".tif"
            #
            # proxima imagen
            #
            nimage = nimage + 1        
            #
            # nombres de archivos y directorios de entrada y salida
            #
            relfname = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext = os.path.splitext(fname)
            foutdir = os.path.join(outdir,reldir)
            debugdir = os.path.join(foutdir,fbase + "_debug")            
            print(f'#{nimage} image={fbase}:')
            #
            # creamos carpetas de destino si no existen
            #
            if not os.path.exists(foutdir):
                os.makedirs(foutdir)


            output_fname = os.path.join(foutdir,fname)
            input_fname = os.path.join(prefix,relfname)
            #
            # leemos imagen
            #
            img = imread(input_fname)
            #---------------------------------------------------
            # hacer algo en el medio
            #---------------------------------------------------
            #
            gt = ground_truth[fbase] 
            args["reldir"] = reldir
            args["name"]   = fbase
            scores = detector_fft(img,sellos,args)
            print("\ttruth:",gt)
            print("\tscore:",[np.round(d,2) for d in scores])
            all_scores.append(scores)
            all_gt.append(gt)
            #---------------------------------------------------
        #
        # fin para cada archivo en la lista
        #

    #
    # fin main
    #
#---------------------------------------------------------------------------------------
