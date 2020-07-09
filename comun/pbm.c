#include "pbm.h"
#include <cstdio>

ErrorCode read_pbm_header(FILE* fimg, idx_t& rows, idx_t& cols) {
    char magic;
    int ancho,alto, aux = 0;
    magic = fgetc(fimg);
    /* 1. numero magico */
    if (magic != 'P')
        return PBM_INVALID_HEADER;
    magic = fgetc(fimg);
    if (magic != '4')
        return PBM_INVALID_HEADER;
    /* ancho */
    aux = fscanf(fimg," %d",&ancho);
    if ((ancho == 0) || (aux == 0))
        return PBM_INVALID_HEADER;
    /* alto */
    aux = fscanf(fimg," %d ",&alto);
    if ((alto == 0) || (aux == 0))
        return PBM_INVALID_HEADER;
    rows = alto;
    cols = ancho;
    /* un espacio al final */
    //aux = fgetc(fimg);
    return PBM_OK;
}

ErrorCode read_pbm_data(FILE* fimg, binary_matrix& A) {
    register idx_t i,li;
    A.clear();
    const idx_t m = A.get_rows();
    const idx_t n = A.get_cols();
    for (i = 0, li=0; i < m; ++i) {
        unsigned short mask = 0;
        idx_t j;
        short r = 0;
        for (j = 0; j < n; ++j, ++li) {
            if (!mask) {
                r = fgetc(fimg);
                mask = 0x80;
                if (r < 0) return PBM_INVALID_DATA;
            }
            A.set(i,j,(r & mask) != 0);
            mask >>= 1;
        }
    }
    if (li < n)
        return PBM_INVALID_DATA;
    else
        return PBM_OK;
}

ErrorCode write_pbm(binary_matrix& A, FILE* fimg) {
    fprintf(fimg,"P4\n%lu %lu\n",A.get_cols(),A.get_rows());
    const idx_t ancho = A.get_cols();
    const idx_t alto = A.get_rows();
    register idx_t i,j;
    for (i = 0; i < alto; ++i) {
        unsigned short mask = 0x80;
        unsigned short word = 0x00;
        for (j = 0; j < ancho; ++j) {
            if (A.get(i,j)) {
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



