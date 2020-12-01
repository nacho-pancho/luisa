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

def achicar(a,proporcion):
    ares =  transform.rescale(a.astype(np.float),1/proporcion,order=1,mode='constant',cval=0,anti_aliasing=True)
    salida = (ares >= 0.45).astype(np.bool)
    print("achicar a proporcion",proporcion,100*np.sum(salida)/np.prod(salida.shape))
    return salida

#---------------------------------------------------------------------------------------

def achicar_sgn(a,proporcion):
    ares =  transform.rescale(a.astype(np.float),1/proporcion,order=1,mode='constant',cval=0,anti_aliasing=True)
    ares[ares >   0.45 ]=  1 
    ares[ares <= -0.45 ]= -1
    #print("achicar a proporcion",proporcion,100*np.sum(ares > 0)/np.prod(ares.shape))
    return ares


#---------------------------------------------------------------------------------------

def detector_fft_un_sello(I,S):
    #
    # reducimos imagen y sello a 1/4 de resolucion
    #
    Is = achicar_sgn(I,4)
    m,n = Is.shape
    angles  = np.arange(-5,5.5,step=0.5)
    matches = np.zeros((len(angles),4),dtype=np.int)
    for i in range(len(angles)): 
        ang = angles[i]
        Sr  = ndimage.rotate(S,ang)
        Srs = achicar_sgn(Sr,4)
        N = np.prod(Srs.shape)
        G = dsp.fftconvolve(Is,Srs,mode='same')
        limax = np.argmax(G)
        imax = limax // n
        jmax = limax - imax*n
        matches[i,0] = ang
        matches[i,1] = imax
        matches[i,2] = jmax
        matches[i,3] = int(10000 * G[imax,jmax] / N)
    #
    # tomamos salida de mayor correlacion
    #
    best_angle_idx = np.argmax(matches[:,-1])
    matches = matches[best_angle_idx,:]
    return matches 
    
#---------------------------------------------------------------------------------------

def detector_fft(img,seals):
    for i in range(len(seals)):
        matches = detector_fft_un_sello(img,seals[i])
        print(f"sello {i} score {matches[3]}")
    #return [detector_fft_un_sello(img,s) for s in seals]
        
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
      ground_truth[key] = row[1:-1] # ultimo es espacio 
 
    with open(seals_file) as fl:
        nimage = 0
        for relfname in fl:
            nimage = nimage+1
            relfname = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext = os.path.splitext(fname)
            input_fname = os.path.join(prefix,relfname)
            print(f'cargando sello #{nimage} fname={input_fname}')
            sellos.append(imread(input_fname))
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
            print("\tDP:",detecciones)
            #---------------------------------------------------
        #
        # fin para cada archivo en la lista
        #
    #
    # fin main
    #
#---------------------------------------------------------------------------------------
