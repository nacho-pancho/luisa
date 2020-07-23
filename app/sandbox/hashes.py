# -*- coding:utf-8 -*-
import subprocess
import hashlib

def hash_image_file(filename):
   return subprocess.getoutput(F"/usr/bin/sha256sum -b '{filename}'| cut -d' ' -f1")

def hash_block(matrix):
    hasher = hashlib.sha256()
    hasher.update(matrix.tobytes())
    return hasher.hexdigest()


