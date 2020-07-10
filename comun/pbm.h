/**
 * \file pbm.h
 * \brief Basic Handling of Portable Bitmap files (PBM)
 */
#ifndef PBM_H
#define PBM_H

#include <stdio.h>

/**
 * Codigos de error para biblioteca de entrada/salida imagenes
 */
enum  {
    PBM_OK=0,
    PBM_READ_ERROR=1,
    PBM_FILE_NOT_FOUND=2,
    PBM_INVALID_HEADER=3,
    PBM_INVALID_DATA=4,
    PBM_WRITE_ERROR=5,
    PBM_INVALID_FORMAT=6
};

typedef struct image { 
    int nrows;
    int ncols;
    int npixels;
    char* pixels;
} image_t;

int read_pbm_header(FILE* fimg, int* nrows, int *ncols );

image_t* read_pbm_data(FILE* fimg, const int nrows, const int ncols);

int write_pbm(const image_t* img, FILE* fimg);

void free_image(image_t* img);

image_t* alloc_image(const unsigned rows, const unsigned cols);

#endif
