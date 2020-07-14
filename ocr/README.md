# Transcripción automática de texto 
## Optical Character Recognition (OCR)

Este proyecto trata de mejorar la transcripción automática que se realiza hoy en día.
El software que se utiliza es el Tesseract (versión 4.1 al momento de escribir esto).
Hay varios caminos para trabajar.

* Adaptar el Tesseract a los datos de LUISA (esto lo permite la aplicación)
* Crear un OCR nuevo utilizando, por ejemplo, redes convolucionales (CNN) profundas.

Esta carpeta es un extracto de la Hackathón de LUISA que se realizó a fines de 2019.
En aquel momento se almacenó la información de entrenamiento en archivos HDF5, un 
formato muy eficiente y práctico para almacenar datos de todo tipo. Por el momento
no estamos usándolo aquí, pero por las dudas y porque es interesante, dejamos
archivos de ejemplo sobre cómo manejar HDF5 en la carpeta hdf5.

En la carpeta de datos en la raíz de este repositorio encontrarán también varios
diccionarios y listas de palabras cuyo objetivo es cotejar la validez de la
salida del OCR, que no siempre es una palabra válida.

* README.md ............... Este archivo
* evaluate.py ............. Evaluación de la calidad de una transcripción.
* hdf5 .................... Ejemplos sobre cómo leer y escribir HDF5
* Ver también datos/ocr/dic
* Ver también datos/ocr/blk


