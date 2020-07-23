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
import luisadbsqlite as db
import hashes 

#---------------------------------------------------------------------------------------

ROW_ABS_THRES = 20    # 
ROW_REL_THRES = 4     # 4 more pixels than local baseline
COL_ABS_THRES = 1     # column has at least three pixels black
COL_REL_THRES = 0.1   # the intensity of the column is less than 20% of the maximum
MIN_WORD_SEP = 20     # minimum separation between two words
MAX_LETTER_SEP = 18
BLOCK_ABS_THRES = 4   # minimum number of pixels in a valid block
TRAZO=1.0
COLOR=(0.0,0.2,0.4,0.1)
COLORMAP = plt.get_cmap('cool')
WIN_SIZE = 1024
MIN_ROW_HEIGHT = 20  # smallest letter I found was about 23


#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--imgdir", type=str, default="../../datos",
		    help="path prefix  where to find prealigned files")
    ap.add_argument("-b", "--blockdir", type=str, default="../../datos/blocks",
		    help="path prefix  where to find prealigned files")
    ap.add_argument("-o","--outfile", type=str, default="luisa.db",
		    help="where to store sqlite3 database")
    ap.add_argument("-l","--list", type=str, default="../../datos/r0566a.list",
		    help="text file where input pre-aligned files are specified")
    ap.add_argument("-f","--force", action="store_true",
		    help="Forces the output to be overwritten even if it exists.")
    #
    # INICIALIZACION
    #
    args      = vars(ap.parse_args())
    print(args)
    blockdir    = args["blockdir"]
    imgdir      = args["imgdir"]
    outfile     = args["outfile"]
    list_fname  = args["list"]
    #
    # abrir db
    #
    nimage = 0
    errors = list()
    prev_rollo = ""
    with open(list_fname) as list_file:
        cursor = db.getConnection(outfile)
        for img_fname in list_file:
            nimage = nimage + 1        
            #
            # ENTRADA Y SALIDA
            #
            # nombres de archivos de entrada y salida
            #
            relfname     = img_fname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext   = os.path.splitext(fname)
            rollo = fbase[1:5]
            #
            # agregamos rollo a DB si no existe
            #
            if rollo != prev_rollo:
                db.query(f"INSERT INTO rollo (numero,path,anio) VALUES ({rollo},'{reldir}',0)")
            prev_rollo = rollo
            # 
            # agregamos hoja a DB
            #
            hoja  = fbase[6:]
            cursor = db.query(f"SELECT id FROM rollo WHERE numero={rollo}")
            row = cursor.fetchone()
            idrollo = row[0]
            img_path = os.path.join(imgdir,relfname)
            img_hash = hashes.hash_image_file(img_path)
            img = Image.open(img_path)
            img_mat = np.array(img).astype(np.uint8)
            db.query(f"INSERT INTO hoja (idrollo,numero,path,hash) VALUES ({rollo},{hoja},'{fbase}','{img_hash}')")
            cursor = db.query(f"SELECT id FROM hoja WHERE idrollo={rollo} AND numero={hoja}")
            row = cursor.fetchone()
            idhoja = row[0]
            #
            # agregamos los bloques de la hoja
            #
            blocks_fname = os.path.join(blockdir,reldir,fbase+".blocks")
            with open(blocks_fname) as blocks_file:
                for block_info in blocks_file:
                    block_info = block_info.strip()
                    fields = block_info.split('\t')
                    fila,indice,i0,j0,i1,j1 = fields
                    block_mat = img_mat[int(i0):int(i1),int(j0):int(j1)]
                    block_hash = hashes.hash_block(block_mat)
                    print(rollo,hoja,block_info)
                    db.query(f"INSERT INTO bloque (idhoja,fila,indice,i0,j0,i1,j1,hash) \
                        VALUES ({idhoja},{fila},{indice},{i0},{j0},{i1},{j1},'{block_hash}') ")
            db.commit()
        nerr = len(errors)
        if nerr > 0:
            print(f'ERROR AL PROCESAR {nerr} ARCHIVOS:')
            for l in errors:
                print(l)
        #
        # fin main
        #
#---------------------------------------------------------------------------------------
