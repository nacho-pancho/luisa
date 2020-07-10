# LUISA


Este repositorio contiene la descripción, datos, instrucciones y material de apoyo para trabajar en los distintos subproblemas que involucran al sistema LUISA de transcripción de documentos.

## Problemas

Los problemas están organizados por carpetas, siendo lo único común a todos el conjunto de datos sobre el que se trabajará, que es siempre el mismo. Éste conjunto se encuentra en la carpeta datos.

La siguiente es una lista de los proyectos disponibles al momento. Cada carpeta contiene una descripción más detallada.

* alineamiento -- Se trata de rotar cada imagen de modo que el texto quede perfectamente horizontal. Este problema ya está resuelto satisfactoriamente en Python. El objetivo es implementarlo de la manera más computacionalmente eficiente posible, de modo de poder aplicarlo masivamente a millones de documentos.
* orientacion -- Algunos documentos vienen rotados. Es fundamental que el texto quede horizontal. La idea es desarrollar un método lo más preciso y rápido posible.
* bloques -- La idea es mejorar y acelerar la detección de bloques de texto, que hoy se hace de manera bastante satisfactoria pero mejorable en Python.
* clasificacion -- Agrupar los documentos según su tipo: carta, planilla, recorte de diario, ficha, formulario. La idea es que sea una clasificación no supervisada (clustering), es decir que los tipos deben determinarse automáticamente.
* maquina -- Identificar automáticamente documentos que usen la misma máquina de escribir.
* firmas -- Detectar firmas manuscritas en el documento y extraerlas
* sellos -- Detectar la presencia de los distintos tipos de sellos que pueden aparecer en los documentos
* web -- mejorar la interfaz web de LUISA en general
* webmobil -- mejorar la interfaz web de LUISA para dispositivos moviles
* luisaapp -- desarrollar una app para LUISA, si es que eso representa alguna ventaja en usabilidad respecto a usar un navegador en el celular.

## Premisas

* El código que se escriba debe ser claro, mucho y muy bien documentado
* Debe buscarse la portabilidad -- adherirse a estándares bien establecidos; no usar las últimas versiones de nada. 
* En particular, para C se recomienda el estándar C99; para C++ el C++11; Python 3.6.x a 3.7.x
* Para proyectos en C o C++ se recomienda usar herramientas de desarrollo de Unix tipo Make
* En caso de C o C++ se debe verificar que no se produzcan pérdidas de memoria (por ejemplo usando valgrind)

## Recomiendaciónes sobre  plataforma de desarrollo

En última instancia, el software de LUISA será ejecutado en plataformas Linux. Es por eso que conviene trabajar en dicho
entorno. En Macintosh es esencialmente lo mismo. Windows es el único que es significativamente distinto, pero tampoco es una
limitante siempre que lo que se haga no dependa de particulares del sistema operativo.

En todo caso, siempre se puede instalar una máquina virtual de Ubuntu sobre Windows, si eso resultara más cómodo.

## Recomendaciones para C/C++

El desarrollo en C/C++ se recomienda sólo para aquellos casos en que el objetivo sea desarrollar una versión eficiente
de algo que ya funciona bien, como el alineado de imágenes. 

Dependiendo de lo que se vaya a hacer, puede ser necesario utilizar alguna biblioteca ya existente de procesamiento
de imágenes. Dicho lo anterior, si no se precisan funciones específicas de una biblioteca, lo mejor es no usarla,
así el código queda sencillo y portátil.

Algunas bibliotecas muy buenas para procesamiento de imágenes son:

* [Leptonica (C)](https://github.com/danbloomberg/leptonica): sencilla, fácil de usar y razonablemente rápida
* [OpenCV (C++)](https://opencv.org/): grande y compleja, pero rápida. Puede aprovechar multiples cores y GPUs
* [CImg   (C++)](http://cimg.eu/): simple (un sólo archivo) y completa. 

## Recomendaciones para Python

Se recomienda usar Python para aquellos problemas que están más abiertos y que requieren mucha experimentación.
Siendo Python es extremadamente portable por lo que la plataforma de desarrollo no es un problema.
Python es muy fácil de aprender y muy versátil; se adapta a casi cualquier estilo o paradigma de programación que
se les ocurra.

Además, el servidor está implementado en Python usando la biblioteca _bottle_, o sea que todo lo que sea desarrollo
web (más allá del estilo) está hecho en Python también. Las bibliotecas relevantes en Python son las siguientes:

* [numpy](https://numpy.org/) Indispensable para manejo de matrices, en particular para manipular imágenes en su representación matricial,
  que es la más natural.
* [pillow](https://python-pillow.org/) Paquete de procesamiento de imágenes de alto nivel. Se integra muy bien con numpy.
* [matplotlib](https://matplotlib.org/) Biblioteca estandar de facto para generar gráficas y ploteos en Python.


# Recomendaciones sobre desarrollo para alta performance

La velocidad es muy importante en algunas tareas de LUISA. Procesar millones de imágenes de decenas de megapixels cada una
puede llevar mucho tiempo.

Sin embargo, como todo, conviene siempre ir de a poco. Si nunca se usó CUDA por ejemplo, es muy mala idea comenzar desarrollando
un método cualquiera directamente en CUDA. Lo ideal es comenzar con una implementación fácil pero funcional, y luego avanzar
hacia cosas cáda vez más sofisticadas.
El orden a seguir es el siguiente:

* Si se domina cualquier lenguaje interpretado tipo Python o R, tener una primera implementación funcionando en ellos.
* Implementar el algoritmo en C/C++ sin utilizar ningún tipo de aceleración de hardware
* Incorporar funciones de instrucciones múltiples de los procesadores modernos ([SIMD](https://en.wikipedia.org/wiki/SIMD)). Esto puede acelerar _dramáticamente_ la velocidad de un programa sin siquiera utilizar más de un CPU. Todos los compiladores modernos tienen soporte para SMIDs, por ejemplo [GCC](https://gcc.gnu.org/onlinedocs/gcc/Vector-Extensions.html)
* Incorporar manejo de múltiples CPUs; a esta altura todas las computadoras tienen al menos 4. Para esto existe la biblioteca estándar [OpenMP](https://www.openmp.org/). Es muy fácil de usar y ya viene incluída en todos los compiladores (GCC, Visual C++, etc.)
* Sólo si lo amerita, hacer una implementación con GPUs. Hay que tener en cuenta que para aprovechar estas funciones es necesario tener una buena GPU, y es considerablemente menos portable el código que incluya esta tecnología, así que este paso habría que considerarlo bien.
* *siempre*, *siempre*, verificar que todas las versiones que se tenga den *exactamente* igual. No alcanza con *parecido*.


 

