/**
 * \file pbm.h
 * \brief Handling of Portable Bitmap files (PBM)
 */
#ifndef PBM_H
#define PBM_H

#include "binmat.h"
/**
 * Codigos de error para biblioteca de entrada/salida imagenes
 */
typedef enum error_code {
    PBM_OK=0,
    PBM_READ_ERROR=1,
    PBM_FILE_NOT_FOUND=2,
    PBM_INVALID_HEADER=3,
    PBM_INVALID_DATA=4,
    PBM_WRITE_ERROR=5,
    PBM_INVALID_FORMAT=6
} ErrorCode;

ErrorCode read_pbm_header(FILE* fimg, idx_t& rows, idx_t& cols);
ErrorCode read_pbm_data(FILE* fimg, binary_matrix& A);
ErrorCode write_pbm(binary_matrix& A, FILE* fimg);

#endif
