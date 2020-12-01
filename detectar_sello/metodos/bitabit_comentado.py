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
from functools import partial
#
# bibliotecas adicionales necesarias
#
import numpy as np
from PIL import Image, ImageOps, ImageChops, ImageDraw
import matplotlib.pyplot as plt
from scipy import ndimage, misc
from skimage import transform
import cv2
import multiprocessing

# ---------------------------------------------------------------------------------------

def imrot(_img, _angle):
    w, h = _img.size
    return _img.rotate(_angle, resample=Image.NEAREST, expand=True, fillcolor=1)

# ---------------------------------------------------------------------------------------

def imread(_fname):
    """
    Lectura de imagen TIFF binaria, con corrección por rotaciones
    para contrarrestar bug de Pillow
    :param fname: imagen de entrada
    :return: instancia de Pillow.Image
    """
    _img = Image.open(_fname)
    if _fname.endswith('tif') and _img.tag_v2[274] == 8:  # regression bug in PILLOW for TIFF images
        _img = imrot(_img, -90)
    return 1 - np.asarray(_img, dtype=np.uint8)

# ---------------------------------------------------------------------------------------

def achicar(_img, proporcion):
    """
    reduce imagen de modo que su tamaño original es 1/proporcion del original
    :param _img: imagen de entrada
    :param proporcion: tamaño de salida / tamaño de entrada
    :return: imagen reescalada y umbralizada
    """
    ares = transform.rescale(_img.astype(np.float), 1 / proporcion, order=1, mode='constant', cval=0, anti_aliasing=False)
    salida = (ares > 0).astype(np.bool)
    return salida

# ---------------------------------------------------------------------------------------

def calcularEscalas(a, proporcion):
    """
    Dada una imagen de entrada, devuelve una lista de imágenes a distintas
    proporciones, de 1/2 hasta 1/proporción, en pasos de 1/2.
    :param a: imagen de entrada
    :param proporcion: proporción de la imagen más pequeña resp. a la img de entrada
    :return: lista de imágenes (la primera es la entrada)
    """
    salida = list()
    salida.append(a)
    i = 1
    aa = np.copy(a)
    while i < proporcion:
        i = i * 2
        aa = achicar(aa, 2)
        salida.append(aa)
    return salida

# ---------------------------------------------------------------------------------------

def sacarBarras(_img):
    """
    Quita regiones sólidas negras ("barras") de la imagen, con el objetivo
    de evitar falsos positivos.
    :param _img: imagen de entrada
    :return:  imagen sin barras
    """
    # s1 <- cantidad de negro en la img
    s1 = np.sum(_img)
    # detección de contornos en la imagen
    contours, hierarchy = cv2.findContours(_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # para cada contorno
    for cnt in contours:
        # se determina el área encerrada por el contorno
        area = cv2.contourArea(cnt)
        # si supera cirto umbral (absoluto) de tamaño
        if area > 50000: # :todo: mejor usar tamano relativo en el futuro
            # :todo: por qué generar N copias de la imagen original?
            img2 = _img.copy()
            # se rellena el area con blanco (se borra la barra)
            img2 = cv2.fillPoly(img2, pts=[cnt], color=(0))
            # se calcula la suma de la imagen modificada
            # :todo: esto es redundante, se sabe del area!
            s2 = np.sum(img2)
            # si la imagen modificada tiene al menos 10% menos pixeles negros
            # :todo: esto tambien es redundante, y acá si es proporcional
            promedio = ((s1 - s2) / area)
            if promedio > 0.9:
                _img = img2
                si = s2
    return _img

# ---------------------------------------------------------------------------------------

def bitabit(angulo, sello_, img_multiescala):
    """
    Detector de Damián Pintos
    Esta función busca un sello particular, en un ángulo particular, sobre
    una imagen particular en todas sus escalas (previamente calculadas)
    :param angulo: angulo en que se busca el sello
    :param sello_: imagen de sello de referencia
    :param img_multiescala: imagen a distintas escalas
    :return:
    """
    ESCALAS = 256
    tolerancia = 0.4

    # se va a agrandar un poco la imagen, y rellena con 0 en los bordes, así que los bordes no generan error
    s = ndimage.rotate(sello_, angulo, reshape=True)

    # armo la lista con el sello en las distintas escalas
    sello_multiescala = calcularEscalas(s, ESCALAS)
    sello_multiescala = sello_multiescala[::-1] # no entiendo por qué esta linea...

    #
    # primer escala (original)
    #
    sello_escala     = sello_multiescala[0]
    img_escala       = img_multiescala[0]
    (largo_sello, ancho_sello) = np.shape(sello_escala)
    (largo_img, ancho_img)   = np.shape(img_escala)
    sumasello        = np.sum(sello_escala)
    validos = list() # lista de posiciones en donde puede encontrarse un sello
    if sumasello > 0: # solo tiene sentido si el sello no está vacío
        #
        # se recorre toda la imagen en busca de detecciones
        #
        for i in range(largo_img - largo_sello):
            for j in range(ancho_img - ancho_sello):
                #
                # ventana de la imagen correspondiente a la esquina sup. (i,j)
                # con el mismo tam. que el sello
                corte = img_escala[i:largo_sello + i, j:ancho_sello + j]
                #
                # se declara una detección si la proporción de pixeles del
                # sello que también están "encendidos" en la imagen es mayor
                # a una tolerancia predeterminada.
                #
                # :todo: cuidado con esto; da falsos positivos si la imagen es muy negra
                #        ver si no se puede usar otra forma de correlación que no tenga
                #        este problema, por ejemplo dividiendo también sobre la cant. de pixeles
                #        negros en el 'corte'
                suma = np.sum(np.logical_and(corte == 1, sello_escala == 1))
                if (suma / sumasello) >= tolerancia:
                    validos.append((i, j, suma / sumasello))

    proporcion = ESCALAS
    ii = 1
    while proporcion > 1 and len(validos) > 0:
        proporcion = proporcion / 2
        # print(f'sello {isello} angulo {angulo} : proporcion {proporcion} validar: {len(validos)}')
        sello_escala = sello_multiescala[ii]
        img_escala = img_multiescala[ii]
        ii = ii + 1
        sumasello = np.sum(sello_escala)
        # plt.imshow(sello_escala, interpolation='nearest')
        # plt.show()
        # plt.imshow(img_escala, interpolation='nearest')
        # plt.show()
        (largo_sello, ancho_sello) = np.shape(sello_escala)
        (largo_img, ancho_img) = np.shape(img_escala)
        vds = []
        for (i, j, margen) in validos:
            i = i * 2
            j = j * 2

            if (largo_sello + i) <= largo_img and (ancho_sello + j) <= ancho_img:
                corte = img_escala[i:largo_sello + i, j:ancho_sello + j]
                suma = np.sum(np.logical_and(corte == 1, sello_escala == 1))

                if (suma / sumasello) >= tolerancia:
                    vds.append((i, j, suma / sumasello))

                if (largo_sello + i + 1) <= largo_img:
                    corte = img_escala[(i + 1):(largo_sello + i + 1), j:ancho_sello + j]
                    suma = np.sum(np.logical_and(corte == 1, sello_escala == 1))
                    if (suma / sumasello) >= tolerancia:
                        vds.append((i + 1, j, suma / sumasello))

                if (ancho_sello + j + 1) <= ancho_img:
                    corte = img_escala[i:largo_sello + i, (j + 1):ancho_sello + j + 1]
                    suma = np.sum(np.logical_and(corte == 1, sello_escala == 1))
                    if (suma / sumasello) >= tolerancia:
                        vds.append((i, j + 1, suma / sumasello))

                if (ancho_sello + j + 1) <= ancho_img and (largo_sello + i + 1) <= largo_img:
                    corte = img_escala[i + 1:largo_sello + i + 1, j + 1:ancho_sello + j + 1]
                    suma = np.sum(np.logical_and(corte == 1, sello_escala == 1))
                    if (suma / sumasello) >= tolerancia:
                        vds.append((i + 1, j + 1, suma / sumasello))

        validos = vds
    maximo = 0
    imaximo = 0
    jmaximo = 0
    # print(f' rotacion {angulo}')
    # print(validos)
    for (i, j, margen) in validos:
        if margen > maximo:
            imaximo = i
            jmaximo = j
            maximo = margen
    # print("sale ",imaximo,jmaximo,maximo)
    return (imaximo, jmaximo, maximo)

# ---------------------------------------------------------------------------------------

def detector_bitabit_pool(img, seals):
    """
    Versión multicore de detector_bitabit
    :param img: imagen en donde buscar los sellos
    :param seals: lista de sellos a buscar
    :return: lista binaria en donde se indica si cada sello en la lista de entrada está o no presente en la imagen
    """
    ESCALAS = 256
    img = sacarBarras(img)
    det = np.zeros(len(seals), dtype=np.float)
    isello = 0
    # armo la lista con la imagen en las distintas escalas
    limgz = calcularEscalas(img, ESCALAS)
    limgz = limgz[::-1]
    for sello in seals:
        # plt.imshow(img, interpolation='nearest')
        # plt.show()
        # plt.imshow(sello, interpolation='nearest')
        # plt.show()
        imaximo = 0
        jmaximo = 0
        resultados = []

        p = multiprocessing.Pool()
        resultados = p.map(partial(bitabit, sello_=sello, limgz_=limgz), range(-10, 10))
        p.close()
        p.join()
        # print(resultados)
        maximo = 0
        imaximo = 0
        jmaximo = 0
        for (i, j, margen) in resultados:
            if margen > maximo:
                imaximo = i
                jmaximo = j
                maximo = margen

        # esta parte es solo para mostrar
        mostrar = 0
        if mostrar == 1:
            # if maximo>tolerancia :
            # print(f'maximo {maximo}')
            (largos, anchos) = np.shape(sello)
            copia = np.copy(img)
            for x in range(largos):
                for y in range(anchos):
                    if copia[x + imaximo][y + jmaximo] == 1:
                        copia[x + imaximo][y + jmaximo] = 0
                    else:
                        copia[x + imaximo][y + jmaximo] = 1
        # print(f'maximo: {maximo}')
        # plt.imshow(sello, interpolation='nearest')
        # plt.show()
        # plt.imshow(copia, interpolation='nearest')
        # plt.show()
        det[isello] = maximo
        isello = isello + 1
    return det

# ---------------------------------------------------------------------------------------

def detector_bitabit(img, seals):
    """
    Busca cada uno de los sellos en una imagen particular
    :param img: imagen en donde buscar los sellos
    :param seals: lista de sellos a buscar
    :return: lista binaria indicando la presencia o ausencia de cada sello en la lista.
    """
    img = sacarBarras(img)
    ESCALAS = 256
    det = np.zeros(len(seals), dtype=np.float)
    tolerancia = 0.4
    isello = 0
    # armo la lista con la imagen en las distintas escalas
    limgz = calcularEscalas(img, ESCALAS)
    limgz = limgz[::-1]
    for sello in seals:
        # plt.imshow(img, interpolation='nearest')
        # plt.show()
        # plt.imshow(sello, interpolation='nearest')
        # plt.show()
        imaximo = 0
        jmaximo = 0
        resultados = []
        for angulo in range(-10, 10):
            # se va a agrandar un poco la imagen, y rellena con 0 en los bordes, así que los bordes no generan error
            s = ndimage.rotate(sello, angulo, reshape=True)

            # armo la lista con el sello en las distintas escalas
            lsz = calcularEscalas(s, ESCALAS)
            lsz = lsz[::-1]

            sz = lsz[0]
            imgz = limgz[0]
            (largos, anchos) = np.shape(sz)
            (largo, ancho) = np.shape(imgz)
            sumasello = np.sum(sz)
            validos = []
            if sumasello > 0:
                for i in range(largo - largos):
                    for j in range(ancho - anchos):
                        corte = imgz[i:largos + i, j:anchos + j]
                        suma = np.sum(np.logical_and(corte == 1, sz == 1))
                        # sumacorte = np.sum(corte)
                        # if sumacorte!=0 and ((suma*suma)/(sumasello*sumacorte))>=tolerancia:
                        if (suma / sumasello) >= tolerancia:
                            validos.append((i, j, suma / sumasello))

            proporcion = ESCALAS
            ii = 1
            while proporcion > 1 and len(validos) > 0:
                proporcion = proporcion / 2
                # print(f'sello {isello} angulo {angulo} : proporcion {proporcion} validar: {len(validos)}')
                sz = lsz[ii]
                imgz = limgz[ii]
                ii = ii + 1
                sumasello = np.sum(sz)
                # plt.imshow(sz, interpolation='nearest')
                # plt.show()
                # plt.imshow(imgz, interpolation='nearest')
                # plt.show()
                (largos, anchos) = np.shape(sz)
                (largo, ancho) = np.shape(imgz)
                vds = []
                for (i, j, margen) in validos:
                    i = i * 2
                    j = j * 2

                    if (largos + i) <= largo and (anchos + j) <= ancho:
                        corte = imgz[i:largos + i, j:anchos + j]
                        suma = np.sum(np.logical_and(corte == 1, sz == 1))

                        if (suma / sumasello) >= tolerancia:
                            vds.append((i, j, suma / sumasello))

                        if (largos + i + 1) <= largo:
                            corte = imgz[(i + 1):(largos + i + 1), j:anchos + j]
                            suma = np.sum(np.logical_and(corte == 1, sz == 1))
                            if (suma / sumasello) >= tolerancia:
                                vds.append((i + 1, j, suma / sumasello))

                        if (anchos + j + 1) <= ancho:
                            corte = imgz[i:largos + i, (j + 1):anchos + j + 1]
                            suma = np.sum(np.logical_and(corte == 1, sz == 1))
                            if (suma / sumasello) >= tolerancia:
                                vds.append((i, j + 1, suma / sumasello))

                        if (anchos + j + 1) <= ancho and (largos + i + 1) <= largo:
                            corte = imgz[i + 1:largos + i + 1, j + 1:anchos + j + 1]
                            suma = np.sum(np.logical_and(corte == 1, sz == 1))
                            if (suma / sumasello) >= tolerancia:
                                vds.append((i + 1, j + 1, suma / sumasello))

                validos = vds
            maximo = 0
            imaximo = 0
            jmaximo = 0
            # print(f' rotacion {angulo}')
            # print(validos)
            for (i, j, margen) in validos:
                if margen > maximo:
                    imaximo = i
                    jmaximo = j
                    maximo = margen
            if (maximo > 0):
                resultados.append((imaximo, jmaximo, maximo))

        maximo = 0
        imaximo = 0
        jmaximo = 0
        for (i, j, margen) in resultados:
            if margen > maximo:
                imaximo = i
                jmaximo = j
                maximo = margen

        # esta parte es solo para mostrar
        mostrar = 1
        if mostrar == 1:
            # if maximo>tolerancia :
            # print(f'maximo {maximo}')
            (largos, anchos) = np.shape(sello)
            copia = np.copy(img)
            for x in range(largos):
                for y in range(anchos):
                    if copia[x + imaximo][y + jmaximo] == 1:
                        copia[x + imaximo][y + jmaximo] = 0
                    else:
                        copia[x + imaximo][y + jmaximo] = 1
        # print(f'maximo: {maximo}')
        # plt.imshow(sello, interpolation='nearest')
        # plt.show()
        # plt.imshow(copia, interpolation='nearest')
        # plt.show()
        det[isello] = maximo
        isello = isello + 1
    return det

# ---------------------------------------------------------------------------------------

def evaluar_detectores(img, seals, methods):
    return [m(img, seals) for m in methods]

# ---------------------------------------------------------------------------------------
def detector_nulo(img, seals):
    det = np.zeros(len(seals), dtype=np.float)
    return det


if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="../datos",
                    help="path prefix  where to find files")
    ap.add_argument("-o", "--outdir", type=str, default="../results",
                    help="where to store results")
    ap.add_argument("-l", "--list", type=str, default="../datos/r0566.list",
                    help="text file where input files are specified")
    ap.add_argument("-s", "--seals", type=str, default="../datos/sellos.list",
                    help="text file with the list of input seal image files")
    ap.add_argument("-t", "--truth", type=str, default="../datos/sellos_gt.csv",
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
            nimage = nimage + 1
            relfname = relfname.rstrip('\n')
            reldir, fname = os.path.split(relfname)
            fbase, fext = os.path.splitext(fname)
            input_fname = os.path.join(prefix, relfname)
            print(f'cargando sello #{nimage} fname={input_fname}')
            sellos.append(imread(input_fname))
    #
    # armamos lista de detectores a evaluar
    #
    detectores = (detector_bitabit_pool, detector_nulo)

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
            relfname = relfname.split('.')[0] + ".tif"
            #
            # proxima imagen
            #
            nimage = nimage + 1
            #
            # nombres de archivos y directorios de entrada y salida
            #
            relfname = relfname.rstrip('\n')
            reldir, fname = os.path.split(relfname)
            fbase, fext = os.path.splitext(fname)
            foutdir = os.path.join(outdir, reldir)
            debugdir = os.path.join(foutdir, fbase + "_debug")
            print(f'#{nimage} image={fbase}', flush=True)
            #
            # creamos carpetas de destino si no existen
            #
            if not os.path.exists(foutdir):
                os.makedirs(foutdir)

            output_fname = os.path.join(foutdir, fname)
            input_fname = os.path.join(prefix, relfname)
            #
            # leemos imagen
            #
            img = imread(input_fname)
            # ---------------------------------------------------
            # hacer algo en el medio
            # ---------------------------------------------------
            truth = np.zeros(len(sellos), dtype=np.float)
            detecciones = evaluar_detectores(img, sellos, detectores)
            print(detecciones, flush=True)
            # ---------------------------------------------------
        #
        # fin para cada archivo en la lista
        #
    #
    # fin main
    #

# ---------------------------------------------------------------------------------------
