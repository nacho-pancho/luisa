import numpy as np
import torch
import torch.nn.functional as F
from torch import nn, optim
import os
import sys
import argparse
import time
import aux

# Network module
class CLEAN(nn.Module):
    def __init__(self, device, x_dim, y_dim, args):
        super(CLEAN, self).__init__()

        self.first=True
        self.lenc=args.lenc # Maximal number of characters in string. All strings padded with spaces to that length
        self.bsz=args.bsz # Batch size - gets multiplied by number of shifts so needs to be quite small.
        self.x_dim=x_dim # Dimensions of all images.
        self.y_dim=y_dim
        self.full_dim=x_dim*y_dim
        self.dv=device
        self.ll=args.ll # Number of possible character labels.
        self.weights=torch.ones(self.ll).to(device)
        self.weights[0]=1.
        self.pools = args.pools # List of pooling at each level of network
        self.drops=args.drops # Drop fraction at each level of network
        ff=len(args.filts) # Number of filters = number of conv layers.
        # Create list of convolution layers with the appropriate filter size, number of features etc.
        self.convs = nn.ModuleList([torch.nn.Conv2d(args.feats[i], args.feats[i+1],
                                                    args.filts[i],stride=1,padding=np.int32(np.floor(args.filts[i]/2)))
                                    for i in range(ff)])

        # The loss function
        self.criterion=nn.CrossEntropyLoss(weight=self.weights,reduction='sum')
        self.criterion_shift=nn.CrossEntropyLoss(reduce=False)
        if (args.optimizer == 'Adam'):
            self.optimizer = optim.Adam(self.parameters(), lr=args.lr)
        else:
            self.optimizer = optim.SGD(self.parameters(), lr=args.lr)

    # Apply sequence of conv layers up to the final one that will be determined later.
    def forward_pre(self,input):

        out=input
        if (self.first):
            self.pool_layers=[]
        for i, cc in enumerate(self.convs):
            if (self.first):
                print(out.shape)
            out=cc(out)
            pp=torch.fmod(torch.tensor(out.shape),self.pools[i])
            if (self.pools[i]>1):
                if (self.first):
                    self.pool_layers+=[nn.MaxPool2d(self.pools[i],padding=tuple(pp[2:4]))]
                out=self.pool_layers[i](out)
            else:
                if (self.first):
                    self.pool_layers+=[None]
            if (self.drops[i]<1.):
                out=nn.functional.dropout(out,self.drops[i])
            # Relu non-linearity at each level.
            out=F.relu(out)
        return(out)

    # Full network
    def forward(self,input):

        out=self.forward_pre(input)

        # During first pass check if dropout required.
        if (self.drops[-1]<1.):
            if (self.first):
                self.dr2d=nn.Dropout2d(self.drops[-1])
            out=self.dr2d(out)
        # If first time running through setup last layer.
        if (self.first):
            # Get dimensions of current output
            self.sh=out.shape
            # Create x-size of new filter, y-size is full y-dimension
            self.sh2a = np.int32(np.floor(self.sh[3] / self.lenc))
            # Compute padding to the end of the array
            self.pad = self.sh2a * (self.lenc)+1 - self.sh[3]
            print('pre final shape',out.shape,self.sh[2],self.sh2a, self.pad, self.lenc)
        # Concatenate the padding
        out=torch.cat((out,torch.zeros(out.shape[0],self.sh[1],self.sh[2],self.pad).to(self.dv)),dim=3)
        if (self.first):
            # Define last conv layer that has as many output features as labels - this is the vector of
            # of outputs that go to the softmax to define label probs.
            self.l_out=torch.nn.Conv2d(out.shape[1],args.ll,[self.sh[2],self.sh2a+1],stride=[1,self.sh2a]).to(self.dv)
        # Apply last layer
        out=self.l_out(out)
        if (self.first):
            print('final shape',out.shape)
            self.first=False

        return(out)


    # Get loss and accuracy (all characters and non-space characters).
    def get_acc_and_loss(self,out,targ):

        v,mx=torch.max(out,1)
        # Non-space characters
        targa=targ[targ>0]
        mxa=mx[targ>0]
        numa = targa.shape[0]
        # Total loss
        loss=self.criterion(out,targ)
        loss/=len(targ)
        # total accuracy
        acc=torch.sum(mx.eq(targ))
        # Accuracy on case insensitive
        mxc=1+torch.fmod((mx-1),26)
        targc=1+torch.fmod((targ-1),26)
        accc=torch.sum(mxc.eq(targc))
        # Accuracy on non-space
        acca=torch.sum(mxa.eq(targa))

        return loss, acc, acca, numa, accc, mx

    # Find optimal shift/scale for each image


    # GRADIENT STEP
    def loss_and_grad(self, input, target, type='train'):

        # Get output of network
        out=self.forward(input)

        if (type == 'train'):
            self.optimizer.zero_grad()
        # Compute loss and accuracy
        loss, acc, acca, numa, accc, mx=self.get_acc_and_loss(out.permute(1,0,2,3).reshape([self.ll,-1]).transpose(0,1),target.reshape(-1))

        # Perform optimizer step using loss as criterion
        if (type == 'train'):
            loss.backward()
            self.optimizer.step()

        return loss, acc, acca, numa, accc, mx

    # Epoch of network training
    def run_epoch(self, train, text, epoch, fout, type):

        if (type=='train'):
            self.train()
        else:
            self.eval()
        num_tr=train.shape[0]
        ii = np.arange(0, num_tr, 1)
        #if (type=='train'):
        #   np.random.shuffle(ii)
        trin=train[ii]
        targ=text[ii]

        full_loss=0; full_acc=0; full_acca=0; full_numa=0; full_accc=0
        rmx=[]
        # Loop over batches.
        jump=self.bsz
        for j in np.arange(0, num_tr, jump):
            data = (torch.from_numpy(trin[j:j + jump]).float()/255.).to(self.dv)
            target = torch.from_numpy(targ[j:j + jump]).to(self.dv)
            target=target.type(torch.int64)

            loss, acc, acca, numa, accc, mx= self.loss_and_grad(data, target, type)
            full_loss += loss.item()
            full_acc += acc.item()
            full_acca+=acca.item()
            full_accc += accc.item()
            full_numa+=numa
            rmx+=[mx.cpu().detach().numpy()]
        fout.write('====> Epoch {}: {} Full loss: {:.4F}, Full acc: {:.4F}, Non space acc: {:.4F}, case insensitive acc {:.4F}\n'.format(type,epoch,
                    full_loss /(num_tr/self.bsz), full_acc/(num_tr*model.lenc), full_acca/full_numa, full_accc / (num_tr * model.lenc)))

        return(rmx)


    def get_scheduler(self,args):
        scheduler = None
        if args.wd:
            l2 = lambda epoch: pow((1. - 1. * epoch / args.nepoch), 0.9)
            scheduler = torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda=l2)

        return scheduler



os.environ['KMP_DUPLICATE_LIB_OK']='True'

parser = argparse.ArgumentParser(fromfile_prefix_chars='@',
    description='Variational Autoencoder with Spatial Transformation'
)


args=aux.process_args(parser)

use_gpu=0
if (torch.cuda.is_available()):
    use_gpu = args.gpu
if (use_gpu and not args.CONS):
    fout=open('OUT.txt','w')
else:
    args.CONS=True
    fout=sys.stdout

fout.write(str(args)+'\n')
args.fout=fout
fout.flush()

torch.manual_seed(args.seed)
np.random.seed(args.seed)

cuda_string="cuda:"+str(use_gpu-1)
device = torch.device(cuda_string if use_gpu else "cpu")
fout.write('Device,'+str(device)+'\n')
fout.write('USE_GPU,'+str(use_gpu)+'\n')

ll=0
# S,T shifts in x and y directions, Z - scalings
S = args.S #[0, 2, 4, 6]
T = args.T #[0, 4]
Z = args.Z #[.8,1.2]
# Total number of copies per image.
lst=1
if (len(S)>0 and len(T)>0 and len(Z)>=0):
    lst=len(S)*len(T)*(len(Z)+1)

# Assume data is stored in an hdf5 file, split the data into 80% training and 20% test.
train_data,  train_text, test_data, test_text = aux.get_data(args,lst)

fout.write('num train '+str(train_data.shape[0])+'\n')
fout.write('num test '+str(test_data.shape[0])+'\n')

x_dim=np.int32(train_data[0].shape[1])
y_dim=train_data[0].shape[2]

# Add axis for pytorch modules
train_data=train_data[:, :, 0:x_dim, :]
test_data=test_data[:, :, 0:x_dim, :]


# Create the shifts and scales to augment training data
train_data_shift=aux.add_shifts_new(train_data,S,T,Z)
fout.write('num train shifted '+str(train_data_shift.shape[0])+'\n')
train_text_shift=np.repeat(train_text,lst,axis=0)

# Get the model
model=CLEAN(device,x_dim, y_dim, args).to(device)
model.lst=lst
# Run it on a small batch to initialize some modules that need to know dimensions of output
model.run_epoch(train_data[0:model.bsz], train_text, 0, fout, 'test')

# Output all parameters
tot_pars=0
for keys, vals in model.state_dict().items():
    fout.write(keys+','+str(np.array(vals.shape))+'\n')
    tot_pars+=np.prod(np.array(vals.shape))
fout.write('tot_pars,'+str(tot_pars)+'\n')

scheduler=model.get_scheduler(args)


if (scheduler is not None):
            scheduler.step()

# Loop over epochs
for epoch in range(args.nepoch):

    t1=time.time()
    # If optimizing over shifts and scales for each image

    model.run_epoch(train_data_shift, train_text_shift, epoch, fout, 'train')
    # Then test on original test set.
    model.run_epoch(test_data, test_text, epoch, fout, 'test')

    #fout.write('test: in {:5.3f} seconds\n'.format(time.time()-t3))
    fout.write('epoch: {0} in {1:5.3f} seconds\n'.format(epoch,time.time()-t1))
    fout.flush()

# Run one more time on test

rx=model.run_epoch(test_data, test_text,0,fout, 'test')
# Get resulting labels for each image.
rxx=np.int32(np.array(rx)).ravel()
tt=np.array([args.aa[i] for i in rxx]).reshape(len(test_text),args.lenc)
# Create tif file that pastes the computed labeling below the original image for each test image
aux.create_image(test_data,tt,model.x_dim,'try')

# Store the trained model.
ex_file=args.model
if not os.path.isfile('_output'):
    os.system('mkdir _output')
torch.save(model.state_dict(),'_output/'+ex_file+'.pt')
fout.write("DONE\n")
fout.flush()

if (not args.CONS):
    fout.close()
