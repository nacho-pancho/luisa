#include "pbm.h"
#include <stdio.h>
#include <malloc.h>
#include <string.h>

//----------------------------------------------------------------------------

void free_image(image_t* img) {
    free(img->pixels);
    free(img);
}

//----------------------------------------------------------------------------

image_t* alloc_image(const unsigned nrows, const unsigned ncols) {
    image_t* img = (image_t*) malloc(sizeof(image_t));
    img->ncols = ncols;
    img->nrows = nrows;
    img->npixels = ncols*nrows;
    img->pixels = (char*) malloc(img->npixels*sizeof(char));
    return img;
}

//----------------------------------------------------------------------------

int read_pbm_header(FILE* fimg, int* nrows, int *ncols ) {

    char magic;
    int aux = 0;

    magic = fgetc(fimg);
    /* 1. numero magico */
    if (magic != 'P')
        return PBM_INVALID_HEADER;
    magic = fgetc(fimg);
    if (magic != '4')
        return PBM_INVALID_HEADER;

    /* ncols */
        aux = fscanf(fimg," %d",ncols);
    if ((ncols == 0) || (aux == 0))
        return PBM_INVALID_HEADER;

    /* nrows */
    aux = fscanf(fimg," %d ",nrows);
    if ((nrows == 0) || (aux == 0))
        return PBM_INVALID_HEADER;

    return PBM_OK;
}

//----------------------------------------------------------------------------
image_t* read_pbm_data(FILE* fimg, const int nrows, const int ncols) {
    int i,li;
    image_t* img = alloc_image(nrows,ncols);

    for (i = 0, li=0; i < nrows; ++i) {
        unsigned short mask = 0;
        int j;
        int r = 0;
        for (j = 0; j < ncols; ++j, ++li) {
            if (!mask) {
                r = fgetc(fimg);
                mask = 0x80;
                if (r < 0) return NULL;
            }
            img->pixels[li] = (r & mask) != 0 ? 1 : 0;
            mask >>= 1;
        }
    }
    if (li < img->npixels)
        return NULL;
    else
        return img;
}

//----------------------------------------------------------------------------

int write_pbm(const image_t* img, FILE* fimg) {
    const int ncols = img->ncols;
    const int nrows = img->nrows;
    int i,j,li;

    fprintf(fimg,"P4\n%d %d\n",ncols,nrows);

    for (i = 0, li = 0; i < nrows; ++i) {
        unsigned short mask = 0x80;
        unsigned short word = 0x00;
        for (j = 0; j < ncols; ++j, ++li) {
            if (img->pixels[li]) {
                word |= mask;
            }
            mask >>=1;
            if (!mask) {
                fputc(word, fimg);
                mask = 0x80;
                word = 0;
            }
        }
        if ((mask > 0) && (mask != 0x80))
            fputc(word, fimg);
    }
    return PBM_OK;
}

//----------------------------------------------------------------------------


