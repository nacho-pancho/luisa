import os
import numpy as np
with open('r0566.list','r') as f:
    m = 10
    zs = np.zeros(m,dtype=np.int)
    #lista = [ l.strip() for l in f]
    ground_truth = dict()
    for l in f:
        _,l = os.path.split(l.strip())
        l,_ = os.path.splitext(l)
        print(l)
        ground_truth[l] = np.copy(zs)
    n = len(ground_truth)
    for s in range(10):
        fname = f'por_sellos/{s+1:02d}.txt'
        with open(fname,'r') as fs:
            slist = [ l.strip() for l in fs] 
            print(slist)
            for l in slist:
                _,l = os.path.split(l)
                l,_ = os.path.splitext(l)
                ground_truth[l][s] += 1

for k in ground_truth:
    print(k,end=' ')
    for v in ground_truth[k]:
        print(v,end=' ')
    print()

