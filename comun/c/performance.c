#include <stdio.h>
#include <stdlib.h>

#include <omp.h> // OpenMP!
#include <time.h>

#define NROWS 4096
#define NCOLS 4096
#define REPS 100

// See https://gcc.gnu.org/onlinedocs/gcc/Vector-Extensions.html
#define base_type char 
#define number_of_bytes 16

typedef base_type simd16chars __attribute__(( vector_size(number_of_bytes) ));

//----------------------------------------------------------------------------

char rand_char() {
    return (int)(255.0*(double)rand()/(double)RAND_MAX);
}
// number of bytes / size of base type
#define STRIDE 16

//----------------------------------------------------------------------------

char* init_matrix() {
    char* mat;
    mat = (char*) malloc( NCOLS*NROWS*sizeof(base_type) );
    for (int i = 0, k = 0; i < NROWS; ++i) {
        for (int j = 0; j < NCOLS; ++j, ++k) {
            mat[k] = rand_char();            
        }
    }
    return mat;
}

//----------------------------------------------------------------------------

void zero_matrix(char* mat) {
    for (int i = 0, k = 0; i < NROWS; ++i) {
        for (int j = 0; j < NCOLS; ++j, ++k) {
            mat[k] = 0;            
        }
    }
}

//----------------------------------------------------------------------------

unsigned short hash_matrix(char* mat) {
    long hash = 0;
    for (int i = 0, k = 0; i < NROWS; ++i) {
        for (int j = 0; j < NCOLS; ++j, ++k) {
            hash += k*mat[k];            
        }
    }
    return (unsigned short) (hash & 0xffff);
}

//----------------------------------------------------------------------------

void test_single_no_simd(const char* A, const char* B, char* C) {
    for (int R = 0; R < REPS; R++) {
        for (int i = 0, k = 0; i < NROWS; ++i) {
            const char* const Ai = &A[NCOLS*i];
            const char* const Bi = &B[NCOLS*i];
            char* const Ci = &C[NCOLS*i];
            for (int j = 0; j < NCOLS; ++j, ++k) {
                Ci[j] = Ai[j] + 2*Bi[j];                        
            }
        }
    }
}

//----------------------------------------------------------------------------

void test_single_simd(const char* A, const char* B, char* C) {
    const simd16chars* const Asimd = (simd16chars*) A;
    const simd16chars* const Bsimd = (simd16chars*) B;
    simd16chars* const Csimd = (simd16chars*) C;
    const int NCOLSsimd = NCOLS / STRIDE;
    for (int R = 0; R < REPS; R++) {
        for (int i = 0; i < NROWS; ++i) {
            const simd16chars* const Ai = &Asimd[NCOLSsimd*i];
            const simd16chars* const Bi = &Bsimd[NCOLSsimd*i];
            simd16chars* const Ci = &Csimd[NCOLSsimd*i];
            for (int j = 0; j < NCOLSsimd; ++j) {
                Ci[j] = Ai[j] + 2*Bi[j];                        
            }
        }
    }
}

//----------------------------------------------------------------------------
void test_omp_no_simd(const char* A, const char* B, char* C) {
    for (int R = 0; R < REPS; R++) {
#pragma omp parallel for firstprivate(A,B,C)
        for (int i = 0; i < NROWS; ++i) {
            const char* const Ai = &A[NCOLS*i];
            const char* const Bi = &B[NCOLS*i];
            char* const Ci = &C[NCOLS*i];
            for (int j = 0; j < NCOLS; ++j) {
                Ci[j] =  Ai[j] + 2*Bi[j]; 
            }
        }
    }
}

//----------------------------------------------------------------------------

void test_omp_simd(const char* A, const char* B, char* C) {
    const simd16chars* Asimd = (simd16chars*) A;
    const simd16chars* Bsimd = (simd16chars*) B;
    simd16chars* Csimd = (simd16chars*) C;
    const int NCOLSsimd = NCOLS / STRIDE;
    for (int R = 0; R < REPS; R++) {
#pragma omp parallel for firstprivate(Asimd,Bsimd,Csimd)
        for (int i = 0; i < NROWS; ++i) {
            const simd16chars* const Ai = &Asimd[NCOLSsimd*i];
            const simd16chars* const Bi = &Bsimd[NCOLSsimd*i];
            simd16chars* const Ci = &Csimd[NCOLSsimd*i];
            for (int j = 0; j < NCOLSsimd; ++j) {
                Ci[j] = Ai[j] + 2*Bi[j];                        
            }        
        }
    }
}

//----------------------------------------------------------------------------

int main() {
    double t0,t1;
    double dt;
    printf("INIT\n");
    srand(5651300);
    char* A = init_matrix();
    char* B = init_matrix();
    char* C = init_matrix();    

    zero_matrix(C);    
    t0 = omp_get_wtime(); 
    test_single_no_simd(A,B,C);
    t1 = omp_get_wtime();
    dt = t1 - t0;
    printf("PLAIN %f hash=%d\n",dt,hash_matrix(C));

    // OpenMP, no simd
    int NT = 1;
#pragma omp parallel
{
    omp_set_num_threads(omp_get_max_threads());    
    NT = omp_get_num_threads();
}
    zero_matrix(C);    
    t0 = omp_get_wtime(); 
    test_omp_no_simd(A,B,C);
    t1 = omp_get_wtime();
    dt = t1 - t0;
    printf("OpenMP(x%d)  %f hash=%d\n",NT,dt,hash_matrix(C));

    // single CPU, no simd
    zero_matrix(C);    
    t0 = omp_get_wtime(); 
    test_single_simd(A,B,C);
    t1 = omp_get_wtime();
    dt = t1 - t0;
    printf("SIMD  %f hash=%d\n",dt,hash_matrix(C));

    // single CPU, no simd
    zero_matrix(C);    
    t0 = omp_get_wtime(); 
    test_omp_simd(A,B,C);
    t1 = omp_get_wtime();
    dt = t1 - t0;
    printf("OpenMP(x%d) + SIMD %f hash=%d\n",NT,dt,hash_matrix(C));
    free(C);
    free(B);
    free(A);
}
