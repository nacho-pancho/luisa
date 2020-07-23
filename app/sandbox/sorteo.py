# -*- coding: utf-8 -*-
#
# solo usamos funciones basicas de Python 
# para minimizar dependencias
#
import math
import random
import time 
import numpy as np

random.seed(time.time())
#
#
#
def setSemilla(s):
    random.seed(s)


def probPagina(frec_pag, score_ocr=None):
    '''
    dada la frecuencia de ocurrencia de cada página
    y el score obtenido por el OCR para esa página,
    se define una probabilidad de que salga una página
    de modo que:
     
    1) las páginas menos visitadas sean priorizadas
    2) las páginas con score de OCR entre 0.10 y 0.70
       sean priorizadas.
    '''
    k = 3.0/(np.max(frec_pag)+0.001)
    a = [math.exp(-k*x) for x in frec_pag]
    C = math.fsum(a)
    return [x/C for x in a]


def sortearPagina(id_pag, cantbloque_pag, frec_pag, score_ocr=None):
    '''
    sortea una página para mostrar en LUISA.
    @see probPagina
    '''
    ### Si P es vacío, entonces no hay más páginas para rellenar.
    if len(frec_pag) == 0:
        return -1  # no hay más páginas... TERMINAMOS !!!!!

    P = probPagina(frec_pag, score_ocr)
    print("prob pagina",P)
    print("DEBUG: prob de paginas: min=",min(P)," max=",max(P))
    dado = random.random()
    F = 0
    for i in range(len(P)):
        F = F + P[i]
        if F >= dado:
         #   return id_pag[i] # cambiado para poder usar mejor el resultado
            return i


def sortearBloque(frec_bloque,score_bloque=None):
    return random.randrange(0,len(frec_bloque))
    
