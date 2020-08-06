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
import scipy.signal as dsp

#
# bibliotecas adicionales necesarias
#
import numpy as np
from PIL import Image,ImageOps,ImageChops,ImageDraw
import matplotlib.pyplot as plt

#---------------------------------------------------------------------------------------
def evaluar_detectores(img,seals,methods):
    return [ m(img,seals) for m in methods]

#---------------------------------------------------------------------------------------

def detector_nulo(img,seals):
    det = np.zeros(len(seals),dtype=np.float)
    return det

#---------------------------------------------------------------------------------------

def detector_bobo(img,seals):
    det = np.zeros(len(seals),dtype=np.float)
    flipped_seals = [ np.fliplr(np.flipud(s)) for s in seals ]
    norm_factors = [ 1.0/np.sum(s) for s in flipped_seals ]
    correlations = [ np.max(dsp.correlate2d(img,s,mode="same")) for s in flipped_seals ]    
    return np.round(correlations,2) 

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
    with open(seals_file) as fl:
        nimage = 0
        for relfname in fl:
            relfname = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext = os.path.splitext(fname)
            input_fname = os.path.join(prefix,relfname)
            print(f'cargando sello #{nimage} fname={input_fname}')
            img = Image.open(input_fname)
            sellos.append(np.asarray(img,dtype=np.float))
    #
    # armamos lista de detectores a evaluar
    #
    detectores = (detector_nulo,detector_bobo)

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
            print(f'#{nimage} image={fbase} seals=',end='')
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
            img = Image.open(input_fname)
            #---------------------------------------------------
            # hacer algo en el medio
            #---------------------------------------------------
            truth = np.zeros(len(sellos),dtype=np.float)
            detecciones = evaluar_detectores(np.asarray(img,dtype=np.float), sellos, detectores)
            print(detecciones)
            #---------------------------------------------------
        #
        # fin para cada archivo en la lista
        #
    #
    # fin main
    #
    
#---------------------------------------------------------------------------------------
