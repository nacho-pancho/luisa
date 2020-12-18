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
from PIL import Image,ImageOps,ImageChops,ImageDraw
import matplotlib.pyplot as plt
from scipy import ndimage, misc
#from console_progressbar import ProgressBar # pip3 install console-progressbar
from skimage import transform # pip3 install scikit-image

#---------------------------------------------------------------------------------------

def imread(fname):
    img = Image.open(fname)
    return 1-np.asarray(img,dtype=np.uint8)

#---------------------------------------------------------------------------------------

#def achicar(a,proporcion):
#    ares =  transform.rescale(a.astype(np.float),1/proporcion,order=1,mode='constant',cval=0,anti_aliasing=True)
#    salida = (ares >= 0.45).astype(np.bool)
#    print("achicar a proporcion",proporcion,100*np.sum(salida)/np.prod(salida.shape))
#    return salida

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

#---------------------------------------------------------------------------------------

def detector_fft_un_sello(image_scales,seal_scales):
    #
    # factores de normalizacion
    #
    scores = dict()
    Gtotal = np.zeros(image_scales[0.5].shape)
    best_score = 0
    base_scale = np.max(list(seal_scales.keys()))
    base_shape = image_scales[base_scale].shape
    Gtotal    =  np.zeros(base_shape)
    for s in seal_scales.keys():
        Is  = image_scales[s]
        m,n = Is.shape
        seal_rotations = seal_scales[s]
        best_score = 0
        best_angle = 0
        best_i = 0
        best_j = 0
        best_G = 0
        for a in seal_rotations.keys():
            ssr = seal_rotations[a]
            G = dsp.fftconvolve( Is, np.flipud(ssr), mode='same' ) 
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
        print(f"\tscale {s:7.5f} angle {best_angle:5.2f} maximum {best_score:5.3f} at ({best_i:5d},{best_j:5d})")
        Gtotal += ampliar(best_G,base_shape)
        #
        # tomamos salida de mayor correlacion
        #
        #show_match(Is,seal_scales[s][best_angle],best_i,best_j)
    #plt.figure(figsize=(10,10))
    #plt.imshow(Gtotal)
    #plt.title("G total")
    #plt.show()
    limax = np.argmax( Gtotal )
    imax  = limax // base_shape[1]
    jmax  = limax - imax*base_shape[1]
    best_score = Gtotal[imax,jmax]
    #print(f"global score {gmax} at ({imax},{jmax})")
    return best_score 
    
#---------------------------------------------------------------------------------------

def detector_fft(I,seals):
    maxw = 0
    maxh = 0
    scales = (0.5,0.25,0.125)
    scales = (0.7,0.6,0.5,0.4)
    angles = np.arange(-3,3.25,0.25)
    #print("Precomputing scales and rotations")
    #
    # tamaño comun para todos los sellos
    #
    for i in range(len(seals)):
        if seals[i].shape[0] > maxh:
            maxh = seals[i].shape[0]
        if seals[i].shape[1] > maxw:
            maxw = seals[i].shape[1]
    plantilla0 = np.zeros((maxh,maxw))
    plantilla1 = np.ones ((maxh,maxw))
    #
    # precalcular imagenes escaladas y normalizadas
    #
    # usamos una convolucion para estimar la norma 2 de cada patch de la imagen
    # es la raiz de la suma del cuadrado de los pixeles en cada patch
    image_scales = dict()
    for s in scales:
        image_scales[s] =  reducir( I, s )
        In  = dsp.fftconvolve( image_scales[s]**2, plantilla1, mode='same' )
        image_scales[s] /= np.sqrt(np.maximum(In,1)) 
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
            for a in angles:
                #print(f"\t\tangle {a}")
                ssr = reducir( ndimage.rotate( seal, a ), s ) 
                sh,sw = ssr.shape
                sn    = 1.0 / np.linalg.norm( ssr.ravel() )
                aux   = plantilla0.copy()
                ioff  = ( maxh - sh ) // 2
                joff  = ( maxw - sw ) // 2
                aux[ ioff:ioff+sh, joff:joff+sw ] = ssr*sn
                seal_scales[s][a] = aux
        score = detector_fft_un_sello( image_scales, seal_scales )
        print( f"sello {i:3d} score {score:5.3f}" )
        scores.append(score)
    return scores
#---------------------------------------------------------------------------------------

def evaluar_detectores(img,seals,methods):
    return [ m(img,seals) for m in methods]

#---------------------------------------------------------------------------------------

def detector_nulo(img,seals):
    det = np.zeros(len(seals),dtype=np.float)
    return det

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="../datos",
      help="path prefix  where to find files")
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
    list_file = args["list"]
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
            print("\ttruth:",gt)
            detecciones = evaluar_detectores(img, sellos, detectores)
            print("\tscore:",[np.round(d,2) for d in detecciones])
            #---------------------------------------------------
        #
        # fin para cada archivo en la lista
        #
    #
    # fin main
    #
#---------------------------------------------------------------------------------------
