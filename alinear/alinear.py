#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

Código de referencia para usar en el desarrollo de una versión eficiente y efectiva
de detección de ALINEAMIENTO del documento. Con esto nos referimos a cómo debe orientarse
la imagen (en pasos de 90 grados) para que el texto quede normal (ni de costado,
ni boca arriba, etc.).

La idea de este código es que sirva de referencia para una reimplementación eficiente
de la función. Lo ideal sería llegar a 10 imágenes por segundo.

Nota: Por convención propia, el código y los comentarios del código están en inglés. 
Esto es previendo que en algún momento se abra la colaboración al ámbito internacional,
y por costumbre mía :)

@author: Ignacio Ramírez Paulino <nacho@fing.edu.uy>
"""

#
# standard Python packages
#
import os
import sys
import time
import argparse
import math
#
# additional packages (need installation using apt, pip3, etc.)
#
import numpy as np
from PIL import Image,ImageOps,ImageChops,ImageDraw
import scipy.ndimage as skimage
import matplotlib.pyplot as plt
import scipy.signal as dsp

#---------------------------------------------------------------------------------------
#
# these are important parameters of the system
#
ROW_ABS_THRES = 100    # row has 2.5% of its pixels black
ROW_REL_THRES = 4     # 4 more pixels than local baseline
COL_ABS_THRES = 1     # column has at least three pixels black
MIN_WORD_SEP = 3      # minimum separation between two words
BLOCK_ABS_THRES = 4   # minimum number of pixels in a valid block
#
# input / output
#
EXT = '.pbm'  # the images in this project are PBM files (http://netpbm.sourceforge.net/)
COMP='group4' # this only makes sense when compressing to TIFF; ignore it
#
# these are just some aesthetic choices when plotting stuff
#
LWIDTH=1.0            # for plotting
COLOR=(0.0,0.2,0.4,0.1) # for plotting
COLORMAP = plt.get_cmap('cool') # for plotting
WIN_SIZE = 1024

#---------------------------------------------------------------------------------------

def imwrite(fname,img):
    '''
    simple wrapper for writing images, in case I change the I/O package
    '''
    img.save(fname,compression=COMP)

#---------------------------------------------------------------------------------------

def imrot(img,angle):
    '''
    simple wrapper for rotating images, in case I switch Image processing libraries
    '''
    w,h = img.size
    return img.rotate(angle, resample=Image.NEAREST,expand=True,fillcolor=1)

#---------------------------------------------------------------------------------------

def imread(fname):
    '''
    simple wrapper for reading images    
    '''
    return Image.open(fname)

#---------------------------------------------------------------------------------------


def alignment_score(img, angle, debug_prefix = None):
    '''
    Computes a score which will be higher for images whose
    text lines are more horizontal.
    The function takes an unrotated image, a rotation angle,
    and computes the score.
    ''' 
    #
    # rotate the image by the angle given in the arguments
    # crop a little border so that there are no udefined pixels.
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
    #
    # convert image to matrix
    #
    Mrot = 1-np.asarray(rot)
    #
    # sum rows: this gives us a curve of vertical intensity
    # of the image. 
    #
    profile = np.sum(Mrot,axis=1)
    #
    # If the text lines are perfectly horizontal, then the profile
    # will have a very high value on the image rows where there is text,
    # and a very low value when the image rows fall between the lines of text.
    # For perfect alignement, the profile looks more or less like this:
    #
    #     +---+  +---+  +---+  
    #     |   |  |   |  |   | 
    # ----+   +--+   +--+   +--
    #
    # If the alignement is not good, every row of the image will be a mix of
    # text line and interspace between likes, thus making the transition look more
    # fuzzy:
    # 
    #      --     --     --
    #     /  \   /  \   /  \    
    # --./    \_/    \-/    \-
    #
    # When the transitions are sharp, the difference (functio np.diff) will  
    # produce high peaks at the transitions. We actually don't care about
    # the sign of the transition, so we use the absolute value: 
    # 
    #     +   +  +   +  +   +
    #     |   |  |   |  |   | 
    #     |   |  |   |  |   | 
    #     |   |  |   |  |   | 
    # ---- --- -- --- -- --- --
    # 
    # Conversely, for a fuzzy profile,
    # the absolute differences will be small:
    #
    #   ++  ++ ++  ++ ++  ++   
    # --  --  -  --  -  --
    #
    #  As it turns out (a simple result from Geometry), vectors which are 'peaky'
    #  exhibit a larger difference between their L1 norm (sum of their absolute values)
    # and their L2 norm (Euclidean norm). 
    #
    # Thus, the score is simply the ratio between the L1 norm and the L2 norm of the profile.
    #
    # There are a few techincalities to take into account. For example, it is common to find
    # very strong lines which correspond to vertical  (or horizontal) borders or shadows of the
    # page in the original microfilm. These produce very high peaks which do not correspond to 
    # text. That is why we 'trim' (cut) those rows in the profile which are just too strong.
    #
    trim = int(0.8*dw)
    trom = 0
    trimmed_profile = np.copy(profile)
    trimmed_profile[profile > trim] = trim # erase solid lines
    variation = np.abs(np.diff(trimmed_profile)) # compute difference (variation)
    trimmed_variation = variation
    l2 = np.linalg.norm(trimmed_variation) # L2 (Euclidean) norm
    l1 = np.sum(trimmed_variation)         # L1 norm
    #
    # as said, the score is the ratio between the L2 and L1 norms.
    # The L2 norm is large for 'peaky' vectors and smaller for 'fuzzy' vectors.
    # The L1 norm is large for 'fuzzy' or 'dense' vectors.
    #
    score = l2/l1
    #
    # if debug_prefix is provided, then a bunch of diagnostics, plots 
    # and intermediate results are saved to graphic files.
    #
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
    #
    # oh, the cow! (Les Luthiers)
    #     
    return score
    
#---------------------------------------------------------------------------------------

def local_angle_search(work_img, min_angle, max_angle, delta_angle, debug_prefix = None):
    '''
    Does a classical search by bipartition for finding the best alignement angle
    within a range of angles [min_angle,max_angle].
    '''
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


def align_image(orig_img, debug_prefix):
    '''
    Main alignement (and orientation) function.
    It takes the original scanned image and returns the angle (including orientation)
    that produces a straight image, with text lines perfectly horizontal 
    (if everything works as expected).
    '''
    w,h = orig_img.size
    #
    # choose a good zone for further analysis
    #
    box = (700,700,w-700,h-700)
    img = orig_img.crop(box)
    imwrite(debug_prefix + "_cropped.tif",img)
    #
    # search the best alignement angle between -5 and 5 degrees,
    # assuming a portrait orientation.
    #
    delta_angle = 1
    best_angle, best_score   = local_angle_search(img, -5,5, delta_angle, debug_prefix+"_alignement")
    #
    # that's it
    #
    return imrot(orig_img,best_angle),best_angle
    
#---------------------------------------------------------------------------------------

if __name__ == '__main__':

    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--prefix", type=str, default="../datos",
		    help="path prefix  where to find files")
    ap.add_argument("-o","--outdir", type=str, default="../results",
		    help="where to store results")
    ap.add_argument("-l","--list", type=str, default="../datos/test.list",
		    help="text file where input files are specified")
    #
    # initialization
    #
    args = vars(ap.parse_args())
    print(args)
    prefix = args["prefix"]
    outdir = args["outdir"]
    list_file = args["list"]
    with open(list_file) as fl:
        errors = list()
        nimage = 0
        t0 = time.time()
        angles_fname = os.path.join(outdir,'angles.csv')
        angles_file = open(angles_fname,mode="w")
        for relfname in fl:
            #
            # next image
            #
            nimage = nimage + 1        
            #
            # set up names of input and output files
            #
            relfname = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext = os.path.splitext(fname)
            foutdir = os.path.join(outdir,reldir)
            debugdir = os.path.join(foutdir,fbase + "_debug")            
            fimgbands  = os.path.join(foutdir,fbase + '_bands' + EXT)
            
            print(f'#{nimage} relfname={relfname} outdir={outdir} fname={fname} fbase={fbase}')
            #
            # create destination folders if necessary
            #
            fpath = fname[:(fname.find('/')+1)]
            if not os.path.exists(foutdir):
                os.makedirs(foutdir)
            #
            # aligned image name
            #
            aligned_name = os.path.join(foutdir,fname)
            #
            # if destination exists, we skip the alignement
            # process for this image. 
            #
            if os.path.exists(aligned_name):
                print("(cached).")
                continue            
            #
            # read image
            #
            Iorig = imread(os.path.join(prefix,relfname))
            #
            # create output directory for debugging, if required
            #            
            if not os.path.exists(debugdir):
                os.makedirs(debugdir)
            copy_name = os.path.join(debugdir, 'orig' + EXT)
            imwrite(copy_name,Iorig)
            #
            # perform actual processing (alignement)
            #
            Ialign, angle = align_image(Iorig,os.path.join(debugdir,"alinear"))
            print(f'{relfname},{angle}', file=angles_file)
            #
            # write result
            #
            imwrite(aligned_name,Ialign)
            #
            # end of main loop over images
            #
        angles_file.close()
        #
        # print some performance stats
        #
        if nimage > 0:
            meandt = (time.time()-t0) / nimage
            print(f'Average time per image: {meandt} seconds. ')
        nerr = len(errors)
        if nerr > 0:
            print(f'ERROR AL PROCESAR {nerr} ARCHIVOS:')
            for l in errors:
                print(l)
        #
        # end of main function
        #
#---------------------------------------------------------------------------------------
