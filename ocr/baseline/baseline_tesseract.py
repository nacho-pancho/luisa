#!/usr/bin/python3
# USAGE
# nohup python run_tesseract_on_dataset.py --dataset '/home/DOCDIC/feature_extraction/rollos_a_procesar' --results-dir '/home/DOCDIC/data/tesseract' > salida_tesseract.txt &
#
import numpy as np
import argparse
import os
from PIL import Image
import subprocess
import csv
import h5py
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------------
ROOT_DIR = "/bigdata/microfilm/"
IMG_DIR = "{}/1.hojas_alineadas/".format(ROOT_DIR)
TESS_DATA = "/home/nacho/workspace/microfilm/luisaimg/contrib/"
TESS_BIN = "/usr/local/bin/tesseract"
TMP_DIR = "/tmp/"
IMG_EXT = ".tif"

# --------------------------------------------------------------------------------

def execute_tesseract(img_filename, output_filename_without_extension):
    # command = "tesseract %s %s %s 2> /dev/null" %  (tesseract_config, img_filename, output_filename_without_extension)
    command = "tesseract %s %s %s 2> /dev/null" % (tesseract_config, img_filename, output_filename_without_extension)
    print(command)
    subprocess.call(command, shell=True)


# --------------------------------------------------------------------------------

if __name__ == '__main__':
    ## USAR UNA SOLA GPU
    if False:
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        # The GPU id to use, usually either "0" or "1"
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--tessdata", type=str, default="fast",
                    help="use tessdata best or fast")
    ap.add_argument("--padding_cols", type=int, default=4,
                    help="padding to add in cols in pixels (add padding_cols to the left, add padding_cols to the right)")
    ap.add_argument("--padding_rows", type=int, default=4,
                    help="padding to add in rows in pixels (add padding_rows to the top, add padding_rows to the bottom)")
    ap.add_argument("--save_image_blocks", action='store_true',
                    help="save the image blocks")
    ap.add_argument("--skip_existing", action='store_true',
                    help="Do not OCR images with previous results")
    ap.add_argument("-f", "--file", required=True,
                    help="HDF5 source file")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    print(args)
    tessdata = args["tessdata"]
    hdf5_fname = args["file"]
    padding_cols = args["padding_cols"]
    padding_rows = args["padding_rows"]
    lang = "spa"
    #
    # configurar Tesseract
    #
    if tessdata == "best":
        tessdata_dir = "{}/tessdata_best".format(TESS_DATA)
    else:
        tessdata_dir = "{}/tessdata_fast".format(TESS_DATA)

    # psm 7 : Treat the image as a single text line.
    # las hojas son de relación muy cercana a 8/11 (A4)
    # asumiendo eso se llega a que la resolución de escaneo es aprox. 444 dpi 
    tesseract_config = '-l %s --tessdata-dir %s --psm 7 --dpi 444' % (lang, tessdata_dir)

    #
    # los archivos de imagen se convierten a png con ImageMagick
    # y se guardan temporalmente en este archivo
    #
    tmp_block_fname = '{}/archivo_temporal_53_53_456.png'.format(TMP_DIR)
    # tesseract le pone la extensión .txt:
    tmp_tesseract_output_fname_without_ext = '{}/archivo_temporal_tesseract_0980_2342342344'.format(TMP_DIR)
    # tesseract le pone la extensión .txt:
    tmp_tesseract_output_fname = tmp_tesseract_output_fname_without_ext + '.txt'
    #
    # reporte
    #
    print("tmp_input:", tmp_block_fname)
    print("tmp_output:", tmp_tesseract_output_fname)
    print("tesseract config.:", tesseract_config)
    print("tesseract data:", tessdata_dir)
    #
    # PROCESAMIENTO
    #
    with h5py.File(hdf5_fname, 'r') as hdf5_file:  # Pythonic way to open a file
        #
        # get the three datasets
        #
        block_hash_ds = hdf5_file['hash']
        block_text_ds = hdf5_file['text']
        block_bits_ds = hdf5_file['bits']
        block_dim_ds = hdf5_file['dim']
        print(len(block_text_ds))
        #
        # read the entries in the dataset sequentially
        # starting at index 0
        block_idx = 0  # first index to read
        tsv_file = open('foo.tsv','w')
        while block_idx < 10:
            # while len(block_text_ds[block_idx]) > 0:
            #
            # read block info
            #
            block_hash = block_hash_ds[block_idx].tobytes()  # get hash for current block
            block_text = block_text_ds[block_idx]  # get text for current block
            block_dim = block_dim_ds[block_idx]  # get dimension for current block
            block_len = int(block_dim[0]) * int(block_dim[1])  # number of pixels
            block_bits = block_bits_ds[block_idx]  # get packed bits
            block_pixels = np.unpackbits(block_bits)  # unpack bits into boolean pixels
            block_pixels = block_pixels[:block_len]  # discard trailing bits generate during packing
            block_array = np.reshape(block_pixels, block_dim)  # reshape pixels as 2D image
            padded_block_array = np.pad(block_array, (padding_rows,padding_cols),constant_values=(1,1))
            padded_block_array = padded_block_array.astype(np.uint8)*255
            block = Image.fromarray(padded_block_array, mode='L')
            block.save(tmp_block_fname, format="png")
            print('idx',block_idx,'hash',block_hash)
            #
            # ejecutar Tesseract
            #
            execute_tesseract(tmp_block_fname, tmp_tesseract_output_fname_without_ext)
            #
            # recoger salida de Tesseract
            #
            if os.path.isfile(tmp_tesseract_output_fname):
                with open(tmp_tesseract_output_fname, 'r') as f:
                    tesseract_text = f.readline().splitlines()[0]
            else:
                tesseract_text = ''
            #
            # mostrar en pantalla
            #
            print('ground truth',block_text, 'text', tesseract_text)
            hash = str(block_hash,encoding='utf-8')
            print(f'{hash}\t{tesseract_text}',file=tsv_file)
            #
            # agrergar resultados del bloque al TSV
            #
            #plt.imshow(block)
            #plt.show()
            block_idx = block_idx + 1
        tsv_file.close()
#
# fin if __main__ == ...
#
# --------------------------------------------------------------------------------
