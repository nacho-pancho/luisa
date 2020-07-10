/*
  * Copyright (c) 2019 Ignacio Francisco Ramírez Paulino and Ignacio Hounie
  * This program is free software: you can redistribute it and/or modify it
  * under the terms of the GNU Affero General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or (at
  * your option) any later version.
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
  * General Public License for more details.
  * You should have received a copy of the GNU Affero General Public License
  *  along with this program. If not, see <http://www.gnu.org/licenses/>.
*/
/**
 * \file template.c
 * \brief Aplicación de ejemplo, sirve de base para implementar algoritmos
 * de LUISA.
 *
 *  Uses GNU argp to parse arguments
 *  see http://www.gnu.org/software/libc/manual/html_node/Argp.html
 */
#include <stdlib.h>
#include <time.h>                     // basic benchmarking
#include <argp.h>                     // argument parsing
#include <string.h>
#include <sys/stat.h>

#include "pbm.h"

#define LOG_NONE 0
#define LOG_ERROR 1
#define LOG_WARNING 2
#define LOG_INFO 3
#define LOG_DEBUG 4

/**
 * you can just change this function!! 
 */
image_t* process_image(image_t* img) {
  for (int i = 0; i < img->npixels; ++i) {
    img->pixels[i] = 1-img->pixels[i];
  }
  return img;
}

/**
 * These are the options that we can handle through the command line
 */
static struct argp_option options[] = {
  {"verbose",  'v', 0,      OPTION_ARG_OPTIONAL,  "Produce verbose output" },
  {"quiet",    'q', 0,      OPTION_ARG_OPTIONAL,  "Don't produce any output" },
  {"overwrite",    'f', 0,   0,  "Overwrite output file if it exists" },
  {"input-dir",    'i', "some dir",   0,  "Input files come from here." },
  {"output-dir",    'o', "some dir",   0,  "Processed files go here." },
  { 0 } // terminator
};

#include <sys/stat.h>   // stat
#include <stdbool.h>    // bool type

/**
 * ver si existe un archivo o directorio
 */
int file_exists (char *filename) {
  struct stat   buffer;   
  return (stat (filename, &buffer) == 0);
}

void create_subdirs(char* path) {
  char* div = strchr(path,'/');
  if (div == NULL)
    return;
  while (div != NULL) { // there are subdirectories in the file name
    *div = 0;
    if (!file_exists(path)) {
      printf("Creating output directory %s\n",path);      
      mkdir(path,S_IRWXU);
    }
    *div = '/';
    div = strchr(div+1,'/');
  }
}


/**
 * options. These are filled in by the argument parser
 */
typedef struct  {
  char overwrite;
  char* input_list;
  char* input_dir;
  char* output_dir;
} config_t;

/**
 * controls how much output the program will produce
 */
static int log_level;

/**
 * sets the current log level
 */
void set_log_level(int level) {
  log_level = level;
}

/**
 * queries the current log level 
 */
int get_log_level() {
  return log_level;
}

/**
 * options handler
 */
static error_t parse_opt ( int key, char *arg, struct argp_state *state );

/**
 * General description of what this program does; appears when calling with --help
 */
static char program_doc[] =
  "\n*** TEMPLATE: Ejemplo de programa en C    ***\
   \n*** Lee una lista de imagenes y las procesa una a una. ***";

/**
 * A general description of the input arguments we accept; appears when calling with --help
 */
static char args_doc[] = "<INPUT_LIST>";

/**
 * argp configuration structure
 */
static struct argp argp = { options, parse_opt, args_doc, program_doc };

/**
 * main function
 */
int main ( int argc, char **argv ) {
  /*
   * Default program configuration
   */
  puts( "Setting default configuration...\n" );
  config_t cfg; 
  cfg.overwrite = 0;
  cfg.input_list = "";
  cfg.input_dir = "data/";
  cfg.output_dir = "results/";
  /*
   * call parser
   */
  puts ( "Parsing arguments...\n" );
  argp_parse ( &argp, argc, argv, 0, 0, &cfg );

  clock_t t0 = clock();
  /*
   * read file list
   */
  FILE* flist = fopen(cfg.input_list,"r"); 
  if (flist == NULL) {
    fprintf(stderr,"Can't open file list %s\n",cfg.input_list);
    exit(1);
  }
  char* line = NULL;
  size_t len;
  char *path = malloc(1024*sizeof(char));
  while (getline(&line,&len,flist) > 0) {
    /*
     * remove trailing spaces from image file name
     */
    if ( strcspn(line," \r\n\t\b") < strlen(line) ) {
      line[strcspn(line," \r\n\t\b")] = 0;
    }
    /*
     * read image
     */
    sprintf(path,"%s/%s",cfg.input_dir,line);
    FILE* fimg = fopen(path,"r");
    fprintf(stdout,"Processing image file %s ",path);
    if (fimg == NULL) {
      fprintf(stderr,"Can't open file %s\n",path);
      exit(1);
    }
    int nrows,ncols;
    read_pbm_header(fimg,&nrows,&ncols);
    image_t* img = read_pbm_data(fimg,nrows,ncols);
    fclose(fimg);
    if (img == NULL) {
      fprintf(stderr,"Error reading image. Aborting.");
      exit(1);
    }
    //printf("Image has %d rows and %d columns for a total of %d pixels.\n",img->nrows,img->ncols,img->npixels);
    
    sprintf(path,"%s/%s",cfg.output_dir,line);
    if (file_exists(path) && !cfg.overwrite) {
      printf("skipping (already existing file).\n");
      continue; 
    }
    /*
     * ACTUAL IMAGE PROCESSING
     */
    image_t* outimg = process_image(img);
    /*
     * save output file. If there is a subdirectory structure
     * create it.
     */ 
    create_subdirs(path);
    /*
     * write file
     */
    FILE* fout = fopen(path,"w");
    if (fout == NULL) {
      fprintf(stderr,"Error writing image to %s \n",path);
      if (outimg != img) {
        free_image(outimg);
      }
      free_image(img);
      exit(2);
    }
    write_pbm(img,fout);
    /*
     * finished for this file
     */
    if (outimg != img) {
      free_image(outimg);
    }
    free_image(img);
    printf("DONE.\n");
  }  
  free(line);
  clock_t t1 = clock();
  double dt = ((double)( t1 - t0 )) / (double)CLOCKS_PER_SEC;
  printf( "Elapsed time: %f s\n", dt );
  free(path);
  fprintf(stdout,"Cleanup.\n");
  fprintf(stdout,"Bye.\n");
  exit ( 0 );
}


/*
 * argp callback for parsing a single option.
 */
static error_t parse_opt ( int key, char *arg, struct argp_state *state ) {
  /* Get the input argument from argp_parse,
   * which we know is a pointer to our arguments structure.
   */
  config_t *cfg = ( config_t * ) state->input;

  switch ( key ) {
  case 'q':
    set_log_level ( LOG_ERROR );
    break;

  case 'v':
    set_log_level ( LOG_DEBUG );
    break;

    case 'f':
      cfg->overwrite = 1;
      break;

    case 'i':
      cfg->input_dir = arg;
      break;

    case 'o':
      cfg->output_dir = arg;
      break;

  case ARGP_KEY_ARG:
    switch ( state->arg_num ) {
    case 0:
      cfg->input_list = arg;
      break;


    default:
      /** too many arguments! */
      fprintf (stderr, "Too many arguments!.\n" );
      argp_usage ( state );
      break;
    }

    break;

  case ARGP_KEY_END:
    if ( state->arg_num < 1 ) {
      /* Not enough mandatory arguments! */
      fprintf (stderr, "Too FEW arguments!\n" );
      argp_usage ( state );
    }

    break;

  default:
    return ARGP_ERR_UNKNOWN;
  }

  return 0;
}
