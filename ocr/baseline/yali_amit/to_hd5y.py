import os
import numpy as np
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
import h5py


def create_template_image(oibx,text):


    img = Image.new('L', (200,40), 0)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Arial.ttf", 16)
    draw.text((0, 0), text,255,font=font)
    ibx=img.getbbox()
    ibx_in=(ibx[0],ibx[1],ibx[2]+1,ibx[3]+1)
    img=img.crop(ibx_in)
    img=img.resize(oibx[2:4],resample=Image.BICUBIC)
    ibx=img.getbbox()
    img = ImageOps.invert(img)
    new_im=Image.new('L', standard_size,255)
    new_im.paste(img,(0,0))
    nnew_im=np.array(new_im.getdata(),np.uint8).reshape(new_im.size[1], new_im.size[0])
    return nnew_im

def create_image(old_img):

    old_im=Image.new('L',standard_size,255)
    oim=old_img.convert('L')
    oim=ImageOps.scale(oim,.5,resample=Image.BICUBIC)
    oim=ImageOps.invert(oim)
    oibx=oim.getbbox()
    oim=oim.crop(oibx)
    oim=ImageOps.invert(oim)
    old_im.paste(oim,(0,0))
    nold_im=np.array(old_im.getdata(),np.uint8).reshape(old_im.size[1], old_im.size[0])
    IM=nold_im
    return IM, oibx[2:4]


if ('darwin' in sys.platform):
    path=os.path.expanduser("~/Desktop/luisa-blocks-real")
else:
    path="/ga/amit/Desktop/luisa-blocks-real"

print("path")

# Check that text is only regular letters
def all_alfa(text):

    alfa='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    lent=len(text)
    c=0
    for t in text:
        if (t in alfa):
            c+=1
    alf=c==lent
    return alf

# Read in image and test and save in global lists
def produce_image(r):
    with open (r, "r") as f:
        data=f.readlines()
        if (len(data)>0):
            if (all_alfa(data[0])):
                oldr = r[0:r.find('txt')] + 'tif'
                oldimg=Image.open(oldr)
                ra = r.split('/')[-1]
                if (len(data[0])<max_length):
                    text=data[0]+' '*(max_length-len(data[0]))
                else:
                    text=data[0][0:max_length]
                IM, ibx=create_image(oldimg)
                global Images, IBX, TEXT
                Images+=[IM]
                IBX+=[ibx]
                TEXT+=[text]

# Save as hdf5 file
def make_hpy():
    with h5py.File('pairs.hdf5', 'w') as f:
        dset1 = f.create_dataset("PAIRS", data=np.array(Images))
    with open('texts.txt','w') as f:
        for tx in TEXT:
            f.write('%s\n' % tx)


def im_proc(path,rr):
    for r in rr:
        if 'txt' in r:
            produce_image(path+'/'+r)
            if (len(TEXT)>=num_images):
                print("Hello", len(Images))
                make_hpy()
                exit()

# Recursively check if folder has images or has only subfolders.
def check_if_has_images(path):
    rr=os.listdir(path)
    rr.sort()
    print(len(rr), len(TEXT))
    if 'tif' in rr[0] or 'txt' in rr[0]:
        im_proc(path,rr)
    else:
        for r in rr:
            if not r.startswith('.'):
                check_if_has_images(path+'/'+r)


Images=[]
IBX=[]
TEXT=[]

# Number of images to read, max-length of string to use.
num_images=np.int32(sys.argv[1])
max_length=np.int32(sys.argv[2])
# Standard size of image for text of that length 120x35
sandard_size=(120,35)
if (len(sys.argv)>3):
    standard_size=(np.int32(sys.argv[3]),np.int32(sys.argv[4]))
# Loop over subfolders and process images.
check_if_has_images(path)
make_hpy()





