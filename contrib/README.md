# Dependencias

Esta carpeta incluye las bibliotecas más comunes que pueden llegar a ser
necesarias para desarrollar para LUISA en C/C++.

Esto es especialmente útil en plataformas que no tienen un sistema de
paquetes incorporado, como Windows o Mac (aunque en el último hay varios
que pueden instalarse a mano).

Si se trabaja en Linux, todas estas bibliotecas son parte de los repositorios
oficiales y *no es necesario compilarlas*, alcanza con instalarlas desde
los repositorios.

## Imagenes

Como dice el README.md en la raiz del proyecto, las bibliotecas más comunes son Leptonica (C),
CImg (C++) y OpenCV (C++).

En Ubuntu (Debian) y todas sus variantes pueden instalarse desde los repositorios oficiales
con el comando (o bien desde Synaptic o algún manejador gráfico de paquetes):

apt-get install libleptonica-dev  
apt-get install cimg-dev cimg-doc cimg-examples

Ya OpenCV es tan grande y compleja que no se distribuye en un paquete sino en varios paquetes
según grupos de aplicaciones. Si uno no se quiere complicar, puede instalarlos todos:

apt-get install libopencv-*

No incluimos una copia de OpenCV aquí por ser muy grande.

### TIFF

Las imágenes originales de LUISA están en formato TIFF, por lo que se recomienda
también instalar libtiff5-dev.

apt-get install libtiff-dev

# CUDA

CUDA es una biblioteca para utilizar los GPUs de NVIDIA. Es desarrollada y distribuida por
NVIDIA. En Ubuntu:

apt-get install libcuda-dev

