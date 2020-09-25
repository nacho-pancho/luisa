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
from console_progressbar import ProgressBar # pip3 install console-progressbar
from skimage import transform # pip3 install scikit-image

#---------------------------------------------------------------------------------------

def imread(fname):
    img = Image.open(fname)
    return 1-np.asarray(img,dtype=np.uint8)

#---------------------------------------------------------------------------------------

def achicar_DP(a,proporcion):
 (norigx,norigy) = np.shape(a) 
 nnuevox = norigx/proporcion
 nnuevoy = norigy/proporcion
 salida = np.zeros((math.ceil(nnuevox),math.ceil(nnuevoy)))
 stepx = norigx//nnuevox
 stepy = norigy//nnuevoy
 for yr,xr in enumerate(np.arange(0,norigx,stepx)):
  for yc,xc in enumerate(np.arange(0,norigy,stepy)):
   salida[yr,yc] = np.max(a[int(xr):int(xr+stepx),int(xc):int(xc+stepy)])
 return salida

#---------------------------------------------------------------------------------------

def achicar(a,proporcion):
 ares =  transform.rescale(a.astype(np.float),1/proporcion,order=1,mode='constant',cval=0,anti_aliasing=False)
 salida = (ares >= 0.45).astype(np.bool)
 #print("achicar a proporcion",proporcion,100*np.sum(salida)/np.prod(salida.shape))
 return salida

#---------------------------------------------------------------------------------------

def listaz(a,proporcion):
 salida = []
 salida.append(a)
 i = 1
 aa = np.copy(a)
 while i<proporcion:
  i = i*2
  aa = achicar(aa,2)
  salida.append(aa)
 return salida

#---------------------------------------------------------------------------------------

def detector_bitabit(img,seals):
 det = np.zeros(len(seals),dtype=np.float)
 tolerancia = 0.5
 isello = 0
 #armo la lista con la imagen en las distintas escalas
 limgz = listaz(img,256)
 limgz = limgz[::-1]
 for sello in seals:
  imaximo = 0
  jmaximo = 0
  resultados = []
  for angulo in range(-10,10):
   #se va a agrandar un poco la imagen, y rellena con 0 en los bordes, así que los bordes no generan error
   s = ndimage.rotate(sello,angulo, reshape=True)
   
   #armo la lista con el sello en las distintas escalas
   lsz = listaz(s,256)
   lsz = lsz[::-1]
   
   sz = lsz[0]
   imgz = limgz[0]
   (largos,anchos) = np.shape(sz)
   (largo,ancho) = np.shape(imgz)
   sumasello = np.sum(sz)
   validos = []
   if sumasello>0:
    for i in range(largo-largos):
     for j in range(ancho-anchos):
      corte = imgz[i:largos+i,j:anchos+j]
      sumacorte = np.sum(corte)
      if not sumacorte:
       continue
      suma = np.sum(np.logical_and(corte == 1, sz == 1))
      score = suma / (sumasello*sumacorte)
      if score >=tolerancia:
       validos.append((i,j,score))
   
   proporcion = 256
   ii = 1
   while proporcion>1 and len(validos)>0:
    proporcion = proporcion/2
    #print(f'sello {isello} angulo {angulo} : proporcion {proporcion} validar: {len(validos)}')
    sz = lsz[ii]
    imgz = limgz[ii]
    ii = ii+1
    sumasello = np.sum(sz)
    
    (largos,anchos) = np.shape(sz)
    (largo,ancho) = np.shape(imgz)
    vds = []
    for (i,j,margen) in validos:
     i = i*2
     j = j*2
     if (largos+i)<=largo and (anchos+j)<ancho:
      corte = imgz[i:largos+i,j:anchos+j]
      suma = np.sum(np.logical_and(corte == 1, sz == 1))
      if (suma/sumasello)>=tolerancia:
       vds.append((i,j,suma/sumasello))

      if (largos+i+1)<=largo:
       corte = imgz[(i+1):(largos+i+1),j:anchos+j]
       suma = np.sum(np.logical_and(corte == 1, sz == 1))
       if (suma/sumasello)>=tolerancia:
        vds.append((i+1,j,suma/sumasello))
      
      if (anchos+j+1)<=ancho:
       corte = imgz[i:largos+i,(j+1):anchos+j+1]
       suma = np.sum(np.logical_and(corte == 1, sz == 1))
       if (suma/sumasello)>=tolerancia:
        vds.append((i,j+1,suma/sumasello))
      
      if (anchos+j+1)<=ancho and (largos+i+1)<=largo:
       corte = imgz[i+1:largos+i+1,j+1:anchos+j+1]
       suma = np.sum(np.logical_and(corte == 1, sz == 1))
       if (suma/sumasello)>=tolerancia:
        vds.append((i+1,j+1,suma/sumasello))
    validos = vds
   maximo = 0
   imaximo = 0
   jmaximo = 0
   for (i,j,margen) in validos:
    if margen>maximo:
     imaximo = i
     jmaximo = j
     maximo = margen
   if(maximo>0):
    resultados.append((imaximo,jmaximo,maximo))
  #esta parte es solo para mostrar
  maximo = 0
  imaximo = 0
  jmaximo = 0
  for (i,j,margen) in resultados:
   if margen>maximo:
    imaximo = i
    jmaximo = j
    maximo = margen

  if maximo>0.5 :  
   copia = np.copy(img)
   for x in range(largos):
    for y in range(anchos):
     if copia[x+imaximo][y+jmaximo]==1:
      copia[x+imaximo][y+jmaximo] = 0
     else:
      copia[x+imaximo][y+jmaximo] = 1
   plt.imshow(copia, interpolation='nearest')
   plt.show()
  det[isello] = maximo
  isello = isello+1
 return det

#---------------------------------------------------------------------------------------

def detector_bitabitsinachicar(img,seals):
 plt.imshow(img, interpolation='nearest')
 plt.show()
 det = np.zeros(len(seals),dtype=np.float)
 i = 0
 (largo,ancho) = np.shape(img)
 print("largo ",largo)
 print("ancho ",ancho)
 det = np.zeros(len(seals),dtype=np.float)
 selloactual = 0
 for sello in seals:
  imaximo = 0
  jmaximo = 0
  hastaahora = 0
  mejorrotacion = 0
  for angulo in range(-10,10):
   #se va a agrandar un poco la imagen, y rellena con 0 en los bordes, así que los bordes no generan error
   s = ndimage.rotate(sello,angulo, reshape=True)
   #plt.imshow(s, interpolation='nearest')
   #plt.show()
   (largos,anchos) = np.shape(s)
   #print("******largos ",largos)
   #print("******anchos ",anchos)
   sumasello = np.sum(s)
   print(f'sumasello {sumasello}')
   pb = ProgressBar(total=100,prefix='', suffix='', decimals=3, length=50, fill='X', zfill='-')
   if sumasello>0:
    #print(s)
    #print(len(s.shape))
    max = 0
    iteracion = 0
    total = (largo-largos)*(ancho-anchos)
    for i in range(largo-largos):
     for j in range(ancho-anchos):
      
      suma = 0
      iteracion = iteracion+1
      corte = img[i:largos+i,j:anchos+j]
      (lrgo,acho) = np.shape(corte)    
      #print("******largo ",lrgo)
      #print("******ancho ",acho)
      suma = np.sum(np.logical_and(corte == 1, s == 1))

      actual = i*(ancho-anchos)+j
      pb.print_progress_bar((actual/total)*100)
      if (suma/sumasello)>det[selloactual]:
       hastaahora = suma/sumasello
       imaximo = i
       jmaximo = j
       mejorrotacion = angulo
       #print(f'iteracion {iteracion} de {total} mejor resultado: {hastaahora} rotacion {mejorrotacion}')
       det[selloactual]=suma/sumasello

   print(f'mejor resultado: {hastaahora} rotacion {angulo}')
  
  #esta parte es solo para mostrar
  copia = np.copy(img)
  for x in range(largos):
   for y in range(anchos):
    if copia[x+imaximo][y+jmaximo]==1:
     copia[x+imaximo][y+jmaximo] = 0
    else:
     copia[x+imaximo][y+jmaximo] = 1
  plt.imshow(copia, interpolation='nearest')
  plt.show()
 return det

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
    detectores.append(detector_bitabit)

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