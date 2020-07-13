#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

Código de referencia para usar en el desarrollo de una versión eficiente y efectiva
de detección de ORIENTACIÓN del documento. Con esto nos referimos a cómo debe orientarse
la imagen (en pasos de 90 grados) para que el texto quede normal (ni de costado,
ni boca arriba, etc.).

Como paso previo a la orientación es fundamentar la ALINEACIÓN (corrección de pequeñas
inclinaciones de la página escaneada). Por eso el siguiente ejemplo incluye código para eso.

Por suerte la alineación parece funcionar muy bien en general, por lo que se recomienda
no tocar esa parte y sí concentrarse en el tema de la orientación, cuyo código
se encuentra en la función orientation_score.

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
    #center = (int(w/2),int(h/2))
    return img.rotate(angle, resample=Image.NEAREST,expand=True,fillcolor=1)

#---------------------------------------------------------------------------------------

def imread(fname):
    '''
    simple wrapper for reading images    
    '''
    img = Image.open(fname)
    if not 274 in img.tag_v2:
        return img
    if img.tag_v2[274] == 8: # regression bug in PILLOW for TIFF images
        img = imrot(img,-90)
    return img


#---------------------------------------------------------------------------------------

def orientation_score(img, debug_prefix = None):
    ''' 
    score for deciding which orientation is most likely the best.
    this is the crucial part of this program.
    '''
    #
    # convert from PIL image to Numpy array 
    #
    w,h = img.size
    img = 1-np.asarray(img) # img is now a matrix!
    #
    # sum rows: this gives us a curve of vertical intensity
    # of the image. If the orientation is right, this will
    # result in a number of regularly-spaced 'pulses' corresponding
    # more or less like this: 
    #
    #     +---+  +---+  +---+  
    #     |   |  |   |  |   | 
    # ----+   +--+   +--+   +--
    #
    profile = np.sum(img,axis=1)
    #
    # as a technical step, the curve is 'normalized'
    # this means that the vector 'profile' will sum to 0
    # and have an Euclidean norm of 1 afterwards.
    # this helps in making the score invariant with respect
    # to irrelevant features such as the average intensity
    # of the image, for example.
    #
    profile = profile - np.mean(profile) 
    profile = profile / np.linalg.norm(profile)
    #
    # the idea now is to compute the so called "correlogram"
    # (https://en.wikipedia.org/wiki/Correlogram)
    # The correlogram is a vector which tells us how self-similar
    # is the profile with respect to shifted versions of itself.
    # The idea behind using this is that we should observed
    # a very high correlation when the shift corresponds to the number
    # of pixels between text lines. Below is an example (shift = 7)
    #
    #
    #  1   +---+  +---+  +---+  
    #  0   |   |  |   |  |   | 
    # -1  -+   +--+   +--+   +-
    #
    #  1          +---+  +---+  +---+  
    #  0          |   |  |   |  |   | 
    # -1  --------+   +--+   +--+   +-
    #
    # Later I found that it was even better to look for a sharp 
    # negative correlation (that is, that the shifted version looks like
    # an inverted version of itself) when the shift is equal to the height
    # of the text. This is an example:
    #
    #  1   +---+  +---+  +---+  
    #  0   |   |  |   |  |   | 
    # -1  -+   +--+   +--+   +-
    #
    #  1       +---+  +---+  +---+  
    #  0       |   |  |   |  |   | 
    # -1  -----+   +--+   +--+   +-
    #
    # So far, the best score I found was to measure
    # the difference between the first minimum below 0
    # and the following maximum.
    #
    corr = dsp.correlate(profile,profile)
    #
    # The correlogram is symmetric.
    # we discard the first half:
    # 
    offset = np.argmax(corr)        
    corr = corr[(offset+1):(offset+201)]
    #
    # first minimum of the correlogram below zero:
    # 
    # 1: dp is the 1st order difference of the correlogram.
    # dp[i] = corr[i+1] - corr[i]
    #
    dp = np.diff(corr)
    #
    # since the correlogram always starts as a decreasing function (dp < 0)
    # the first minimum occurs when dp > 0:
    #  
    gut = (dp > 0) * (corr[:-1] < 0)
    idx = np.flatnonzero(gut)
    if len(idx) > 0:
        xmin = idx[0]
    else:
        xmin = 199
    ymin = corr[xmin] # value at the minimum
    
    if xmin < 198:
        ymax = np.max(corr[(xmin+1):]) #value at the maximum
    else:
        ymax = 0
    score = ymax - ymin 
    #
    # if debug_prefix is provided, then a bunch of diagnostics, plots 
    # and intermediate results are saved to graphic files.
    #
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
    #
    # return the score
    #     
    return score
            
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

#---------------------------------------------------------------------------------------

def select_analysis_zone(orig_img,debug_prefix):
    '''
    Chooses a suitable, square region for performing the alignement and orientation
    analyses of the image. This is done for two purposes:
    
    - to speed up the search, since the whole image is 18MPix; here we choose a 1MP square
    - to avoid the influence of borders, marks, or other irrelevant features of the image;
    
    We seek for a square region, among 3 candidates (center top, center center and center bottom), 
    which is more 'interesting' by looking at the average intensity of the pixels. 
    
    A block with more text will have an average intensity close to 1/2. Parts which have no 
    text will usually be much
    closer to 0. Some strange parts may be all black and be too close to 1.
    '''
    w,h = orig_img.size
    d = min(w,h)
    MARGIN=600
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
        x0 = int(np.floor(w/2)) - R
        x1 = int(np.floor(w/2)) + R
        y0 = int(np.floor(i*h/4)) - R
        y1 = int(np.floor(i*h/4)) + R
        p = np.mean(orig_mat[y0:y1,x0:x1])
        box = (x0,y0,x1,y1)
        # the actual score is p * (1 - p)
        # this value is higher when p is close to 1/2 
        # and lower when p is close to 1 or 0
        #
        scores.append(p*(1-p)) 
        boxes.append(box)

    best_idx = np.argmax(scores)
    print("scores",scores)
    print("best zone ",best_idx,":",boxes[best_idx])
    #
    # Additional information.
    # If the top block is significantly darker than
    # the others, it is a good additional indication 
    # that the ORIENTATION of the document os PORTRAIT.
    # This is used as a hint on the orientation detection
    # algorithm.
    #
    if scores[0] > 3*max(scores[1],scores[2]):
        hint = True
    else:
        hint = False
    return (boxes[best_idx], hint)

#---------------------------------------------------------------------------------------

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
    box, hint = select_analysis_zone(orig_img,debug_prefix)
    img = orig_img.crop(box)
    imwrite(debug_prefix + "_cropped.tif",img)
    #
    # search the best alignement angle between -5 and 5 degrees,
    # assuming a portrait orientation.
    #
    delta_angle = 1
    best_portrait_angle, best_portrait_score   = local_angle_search(img, -5,5, delta_angle, debug_prefix+"_portrait")
    aligned_portrait  = imrot(img,best_portrait_angle)
    #
    # if we have a strong hint that the image is in portrait orientation,
    # we do not perform an orientation detection and declare the image
    # to be PORTRAIT 
    #
    if hint:
        print("orientation PORTRAIT (via HINT) correction ",best_portrait_angle)
        return imrot(orig_img,best_portrait_angle)

    #
    # there is no hint, so we see what happens if we rotate the image 90
    # degrees (LANDSCAPE)
    #
    img90 = imrot(img,-90)
    best_landscape_angle, best_landscape_score = local_angle_search(img90,-5,5, delta_angle, debug_prefix+"_landscape")
    best_landscape_angle = best_landscape_angle - 90
    aligned_landscape = imrot(img,best_landscape_angle)
    #
    # in this case we compare both orientations (PORTRAIT and LANDSCAPE)
    # with a specially designed score (which is completely different to the one used for alignement!)
    #
    portrait_score    = orientation_score(aligned_portrait, debug_prefix+"_portrait")
    landscape_score   = orientation_score(aligned_landscape, debug_prefix+"_landscape")
    #
    # decide if the image is landscape or portrait based on the orientation score
    #
    print("portrait score",portrait_score)
    print("landscape score",landscape_score)
    if  landscape_score > portrait_score:
        best_angle = best_landscape_angle
        print("orientation LANDSCAPE correction ",best_landscape_angle + 90)
    else:
        best_angle = best_portrait_angle
        print("orientation PORTRAIT  correction ",best_portrait_angle)
    #
    # that's it
    #
    return imrot(orig_img,best_angle)
    
#---------------------------------------------------------------------------------------

if __name__ == '__main__':

    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--prefix", type=str, default="../datos/orig",
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
                os.system(f'mkdir -p \'{foutdir}\'')
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
                os.system(f'mkdir -p \'{debugdir}\'')
            copy_name = os.path.join(debugdir, 'orig' + EXT)
            imwrite(copy_name,Iorig)
            #
            # perform actual processing (alignement)
            #
            Ialign = align_image(Iorig,os.path.join(debugdir,"alinear"))
            #
            # write result
            #
            imwrite(aligned_name,Ialign)
            #
            # end of main loop over images
            #
        #
        # print some performance stats
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
        # end of main function
        #
#---------------------------------------------------------------------------------------
