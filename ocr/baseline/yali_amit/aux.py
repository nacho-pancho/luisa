import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import scipy.ndimage as scn
import h5py

def process_args(parser):
    parser.add_argument('--filts', type=int, default=(3,3,3,3), help='size of filters') # filter sizes for each layer of network
    parser.add_argument('--feats', type=int, default=(1,32,32,64,256), help='number of filters') # Number of features at each layer
    parser.add_argument('--pools', type=int, default=   (2, 2, 1, 2), help='pooling') # Pooling for each layer
    parser.add_argument('--T', type=int, default=[0,4], nargs="+", help='T') # Vertical shifts for data augmentation
    parser.add_argument('--S', type=int, default=[0, 2, 4, 6], nargs="+", help='S') # Horizontal shifts for data augmentation
    parser.add_argument('--Z', type=float, default=[.8,1.2], nargs="+", help='Z') # Scales for data augmentation
    parser.add_argument('--drops', type=float, default=(1.,1.,1.,1.,.5)) # Dropout for each layer
    parser.add_argument('--bsz', type=int, default=50, help='mb_size (default: 500)') # Batch size
    parser.add_argument('--nepoch', type=int, default=30, help='number of training epochs') # Number of epochs
    parser.add_argument('--gpu', type=int, default=2, help='whether to run in the GPU') # Use gpu
    parser.add_argument('--seed', type=int, default=1345, help='random seed (default: 1111)') # seed
    parser.add_argument('--num_train', type=int, default=60000, help='num train (default: 60000)') # number of training data
    parser.add_argument('--model', default='base', help='model (default: base)') # Name of output file for trained model
    parser.add_argument('--optimizer', default='Adam', help='Type of optimiser') # Type of optimization
    parser.add_argument('--lr', type=float, default=.001, help='Learning rate (default: .001)') # Learning rate
    parser.add_argument('--run_existing', action='store_true', help='Use existing model') # To run existing model (not implemented yet)
    parser.add_argument('--OPT', action='store_true', help='Optimization instead of encoding') # Find optimal alignment - currently not to be used
    parser.add_argument('--CONS', action='store_true', help='Output to consol') # Output to console
    parser.add_argument('--wd', action='store_true', help='Output to consol') # weight decay
    parser.add_argument('--output_prefix', default='', help='path to model') # Path to model.

    args = parser.parse_args()
    return (args)

# Save test images together with labels.
def create_image(trin, TT, x_dim, ex_file):
        mat = []
        t = 0
        ll=len(trin)//63 *63
        page=[]
        t=0
        imlist=[]
        while (t<ll):
            page=[]
            for j in range(7):
                col=[]
                for i in range(9):
                    if (t<ll):
                        text=''.join(TT[t,:])
                        img = Image.new('L', (80+5, x_dim+20), 255)
                        #imga = Image.fromarray(np.int8(trin[t,0,0:x_dim]*200))
                        imga = Image.fromarray(trin[t,0,0:x_dim])
                        img.paste(imga, (0,0))
                        draw = ImageDraw.Draw(img)
                        font = ImageFont.truetype("Arial.ttf", 16)
                        draw.text((0,x_dim), text, 0, font=font)
                        col += [np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0])]
                        t+=1
                    else:
                        col += [np.ones((x_dim+20,85))*255]

                COL = np.concatenate(col, axis=0)
                page+=[COL]
            manifold = np.concatenate(page, axis=1)
            imlist.append(Image.fromarray(manifold))
        imlist[0].save("_Images/test.tif", compression="tiff_deflate", save_all=True,
                       append_images=imlist[1:])

        #if not os.path.isfile('_Images'):
        #    os.system('mkdir _Images')
        #imsave('_Images/' + ex_file + '.png', img)

        print("Saved the sampled images")


# Read in data
def get_data(args,lst):
    with h5py.File('pairs.hdf5', 'r') as f:
        #key = list(f.keys())[0]
        # Get the data
        pairs = f['PAIRS']
        print('tr', pairs.shape)
        all_pairs=np.uint8(pairs) #/255.
        nt=np.minimum(args.num_train,len(all_pairs))
        all_pairs=all_pairs[0:nt]
        all_pairs=all_pairs.reshape(-1,1,all_pairs.shape[1],all_pairs.shape[2])
        chunk=np.int32(args.bsz)
        lltr=np.int32(np.ceil(.8*len(all_pairs))//chunk * chunk)
        llte=np.int32((len(all_pairs)-lltr)//chunk * chunk)
        ii=np.array(range(lltr+llte))
        np.random.shuffle(ii)
        train_data = all_pairs[ii[0:lltr]]
        test_data=all_pairs[ii[lltr:lltr+llte]]
    with open('texts.txt','r') as f:
        TEXT = [line.rstrip() for line in f.readlines()]
        aa=sorted(set(' '.join(TEXT)))
        print(aa)
        if (' ' in aa):
            ll=len(aa)
            spa=0
        else:
            ll=len(aa)+1
            spa=ll-1
        args.ll = ll
        train_t=[TEXT[j] for j in ii[0:lltr]]
        test_t=[TEXT[j] for j in ii[lltr:lltr+llte]]
        lens=[len(r) for r in train_t]
        args.lenc=np.max(lens)
        print('LENC',args.lenc)
        train_text=np.ones((len(train_t),args.lenc))*spa
        for j,tt in enumerate(train_t):
            for i,ss in enumerate(tt):
                train_text[j,i]=aa.index(ss)
        test_text=np.ones((len(test_t),args.lenc))*spa
        for j,tt in enumerate(test_t):
            for i,ss in enumerate(tt):
                test_text[j,i]=aa.index(ss)
        train_text=np.int32(train_text)
        test_text=np.int32(test_text)
        print("hello")
        args.aa=aa

    return train_data, train_text, test_data, test_text

# Create shifts and scales of data.
def add_shifts_new(input,S,T,Z=[]):

    if (len(S)==1 and len(T)==1):
        input_s=input
    else:
        ss=input.shape
        if (len(Z)>0):
            input_z=np.repeat(input,len(Z)+1,axis=0)
            sh=input_z.shape[2:4]
            for i in np.arange(0,len(input_z),len(Z)+1):
                for j in range(len(Z)):
                    input_f = np.float32(input_z[i + j + 1, 0]) / 255.
                    if (Z[j]>1.):
                        tmp1 = np.maximum(0, np.minimum(1., scn.zoom(input_f, zoom=Z[j])[0:sh[0], 0:sh[1]]))
                    else:
                        tmp=np.maximum(0,np.minimum(scn.zoom(input_f,zoom=Z[j]),1.))
                        tmp1=np.ones((sh[0],sh[1]))
                        tmp1[0:tmp.shape[0],0:tmp.shape[1]]=tmp
                    input_z[i + j + 1, 0] = np.uint8(tmp1 * 255.)

            input=input_z

        ls=len(S)
        lt=len(T)
        input_s=np.repeat(input,ls*lt,axis=0)
        l=len(input_s)

        for i,s in enumerate(S):
            lls = np.arange(i*lt, l, ls*lt)
            for j,t in enumerate(T):
                llst=lls+j
                input_s[llst,:]=np.concatenate((input_s[llst,:,:,s:],255*np.ones((len(llst),ss[1],ss[2],s),dtype=np.uint8)),axis=3)
                input_s[llst,:]=np.concatenate((input_s[llst,:,t:,:],255*np.ones((len(llst),ss[1],t,ss[3]),dtype=np.uint8)),axis=2)


    return input_s
