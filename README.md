# LUISA

Este repositorio contiene la descripción, datos, instrucciones y material de apoyo para trabajar en los distintos subproblemas que involucran al sistema LUISA de transcripción de documentos.

Los problemas están organizados por carpetas, siendo lo único común a todos el conjunto de datos sobre el que se trabajará, que es siempre el mismo. Éste conjunto se encuentra en la carpeta datos.

La siguiente es una lista de los proyectos disponibles al momento. Cada carpeta contiene una descripción más detallada.

* alineamiento -- Se trata de rotar cada imagen de modo que el texto quede perfectamente horizontal. Este problema ya está resuelto satisfactoriamente en Python. El objetivo es implementarlo de la manera más computacionalmente eficiente posible, de modo de poder aplicarlo masivamente a millones de documentos.
* orientacion -- Algunos documentos vienen rotados. Es fundamental que el texto quede horizontal. La idea es desarrollar un método lo más preciso y rápido posible.
* det_bloques -- La idea es mejorar y acelerar la detección de bloques de texto, que hoy se hace de manera bastante satisfactoria pero mejorable en Python.
* clasificacion -- Agrupar los documentos según su tipo: carta, planilla, recorte de diario, ficha, formulario. La idea es que sea una clasificación no supervisada (clustering), es decir que los tipos deben determinarse automáticamente.
* maquina -- Identificar automáticamente documentos que usen la misma máquina de escribir.
* firmas -- Detectar firmas manuscritas en el documento y extraerlas
* sellos -- Detectar la presencia de los distintos tipos de sellos que pueden aparecer en los documentos
* web -- mejorar la interfaz web de LUISA en general
* webmobil -- mejorar la interfaz web de LUISA para dispositivos moviles
* luisaapp -- desarrollar una app para LUISA, si es que eso representa alguna ventaja en usabilidad respecto a usar un navegador en el celular.
