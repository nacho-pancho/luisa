#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# python-bottle ------- servidor web basado en Python, Bottle
#

# bibliotecas standard de Python
#
import hashlib # generar hashes
import os
import sys
import io
import base64
import time
# 
# paquetes publicos de Python
#
from urllib.parse import quote
from PIL import Image, ImageDraw
import bottle
from datetime import datetime
# 
# paquetes propios
#
import luisadbsqlite as db
import sorteo
#
#----------------------------------------------------------------------------------------------------
# CONFIGURACION
#----------------------------------------------------------------------------------------------------
#
ROOTDIR  = os.path.dirname(os.path.realpath(__file__))
IMGDIR   = os.path.join(ROOTDIR,"../../datos/")
EXT      = "tif"
CACHEDIR = ROOTDIR + "/block_cache/"
LOCAL_EXT = EXT
CTX_MARGIN_H = 48
CTX_MARGIN_V = 96
BLOCKS_PER_FORM = 4
#----------------------------------------------------------------------------------------------------
#
# caracteres que pueden ser utilizados para rellenar campos
#
validChars = list(range(48,58)) + list(range(65,91)) + list(range(97,123))
top = len(validChars)
#### Lang: lenguaje en el.

#
#----------------------------------------------------------------------------------------------------
# FUNCIONES AUXILIARES
#----------------------------------------------------------------------------------------------------
#
def gLang(req):
    lang=req.query.lang
    if(lang==''):
        lang="es"
    return lang
#
#----------------------------------------------------------------------------------------------------
#

def lquote(str=""):
    return quote(str)
#
#----------------------------------------------------------------------------------------------------
#
def fig2array ( fig ):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw ( )
 
    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = numpy.fromstring ( fig.canvas.tostring_argb(), dtype=numpy.uint8 )
    buf.shape = ( w, h,4 )
 
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = numpy.roll ( buf, 3, axis = 2 )
    return buf
#
#----------------------------------------------------------------------------------------------------
#
def fig2pil ( fig ):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2array ( fig )
    w, h, d = buf.shape
    return Image.fromstring( "RGBA", ( w ,h ), buf.tostring( ) )
#
#----------------------------------------------------------------------------------------------------
#
def gen_img_base64(img):
    #
    # creamos un stream de salida en memoria
    #
    buff     = io.BytesIO()
    #
    # escribimos imagen en formato JPEG en memoria
    #
    img.save(buff, format="GIF")
    #
    # codificamos en Base64 e insertamos el resultado embebido
    #    en la página -- no se genera un link!
    #
    data     = str(base64.b64encode(buff.getvalue()),'utf8') #.encode('utf-8')
    # esto era para insertar en HTML:
    # return   'data:image/gif;base64,%s' % data
    # ahora devolvemos solo el stream B64
    return data
#
#----------------------------------------------------------------------------------------------------
#
def gen_imagenes(id_hoja, id_bloques):
    global CTX_MARGIN_H, CTX_MARGIN_V
    tic = time.time()
    #
    # 1. seleccionamos hoja en base a hash
    # 
    dbcursor = db.query(f"SELECT hash as hashfile, idrollo, path FROM hoja WHERE id={id_hoja}")
    row      = dbcursor.fetchone()
    hash_hoja, id_rollo, filename = row[:]
    #
    # 2. necesitamos rollo para saber ruta completa
    #
    dbcursor = db.query(f"SELECT path FROM rollo WHERE numero={id_rollo}")
    path     = dbcursor.fetchone()[0]
    #
    # 3. ruta completa del archivo 
    #
    filename = "{0:s}/{1:s}.{2:s}".format(path,filename,LOCAL_EXT)
    #
    # 4. abrimos imagen usando la funcion open de Pillow
    #
    img_hoja     = Image.open(IMGDIR+filename)
    
    b64_bloques = []
    i00,j00,i11,j11 = 10000,10000,0,0
    box_bloques = []
    for idb in id_bloques:
        row = db.query(f"SELECT hash,i0,j0,i1,j1 FROM bloque WHERE id={idb}").fetchone()        
        i0,j0,i1,j1 = row[1:5]
        hash_bloque = row[0]
        i00,j00,i11,j11 = min(i00,i0),min(j00,j0),max(i11,i1),max(j11,j1)
        #
        # insertamos imagen de cada bloque en los datos del template
        # como base64
        #
        block_box = (j0,i0,j1,i1)
        box_bloques.append(block_box)
        img_bloque = img_hoja.crop(block_box)
        print("block", hash_bloque," box ",block_box, " size", img_bloque.size)
        b64_bloque = gen_img_base64(img_bloque)        
        b64_bloques.append({'hash':hash_bloque,'b64img':b64_bloque,'width':img_bloque.size[0],'height':img_bloque.size[1] })

    #
    # imagen de contexto: engloba al contexto mas un poco de margen extra
    # resaltamos un poco los bloques para que se note mas que es lo que se
    # esta rellenando
    #
    w00 = j11 - j00
    h00 = i11 - i00
    context_box=(j00-CTX_MARGIN_H,i00-CTX_MARGIN_V,j11+CTX_MARGIN_H,i11+CTX_MARGIN_V)
    #
    # mode='L' convierte la imagen de binaria (1 bit por pixel) a escala
    # de grises.
    img_contexto = img_hoja.crop(context_box).convert(mode='L')
    img_resaltar = Image.new(mode='L',size=img_contexto.size)
    canvas = ImageDraw.Draw(img_resaltar)
    for box in box_bloques:
        relbox = ( box[0] - context_box[0], box[1] - context_box[1],
          box[2] - context_box[0], box[3] - context_box[1] )
        canvas.rectangle(relbox,fill=192,outline=255)

    dbcursor = db.query(f"SELECT hash as hashfile FROM hoja WHERE id={id_hoja}") 
    hash_hoja = dbcursor.fetchone()[0]

    img_contexto = Image.blend(img_contexto, img_resaltar, 1.0/8.0).convert(mode='L')
    b64_contexto = {'hash':hash_hoja,'b64img':gen_img_base64(img_contexto),
        'width':img_contexto.size[0], 'height':img_contexto.size[1]}; 
    return b64_bloques, b64_contexto
#
#----------------------------------------------------------------------------------------------------
# SERVICIO DE URLs / INTERFAZ DE USUARIO 
#----------------------------------------------------------------------------------------------------
#

@bottle.route('/')
def portada():
    '''
    Página principal. Utiliza la funcionalidad de templates provista por Bottle
    y el template definido en tmpl/layout.tpl incluido en el código adjunto.
    '''

#-----------------------------------------------------------------------------

def sortear_hoja():    
    frec_hoja        = list()
    id_hoja          = list()
    for row in db.query("SELECT id, apariciones FROM hoja order by id"):
        id_hoja.append( row[0] )
        frec_hoja.append( row[1] )
    return sorteo.sortearHoja( id_hoja, frec_hoja )

#-----------------------------------------------------------------------------

def sortear_bloques(id_hoja):
    print("hoja",id_hoja)
    #
    # primero elegimos fila en la hoja
    #
    rows = db.query(f"SELECT MAX(fila) FROM bloque WHERE idhoja={id_hoja}").fetchone()
    nfilas = rows[0]
    idx_fila = sorteo.sortearFila(nfilas)
    print("fila",idx_fila)
    #
    # luego elegimos un bloque al azar de esa fila
    #
    row = db.query(f"SELECT MAX(indice) FROM bloque WHERE idhoja={id_hoja} AND fila={idx_fila}").fetchone()
    nbloques = row[0]+1
    print("nbloques",nbloques)

    frec_bloques = list()
    for row in db.query(f"SELECT id, apariciones FROM bloque WHERE idhoja={id_hoja} AND fila={idx_fila}"):
        frec_bloques.append(row[1])
    if nbloques > BLOCKS_PER_FORM:
        max_idx_bloque = nbloques-BLOCKS_PER_FORM
    else:
        max_idx_bloque = nbloques
    #
    # elegimos al azar el primer bloque de BLOCKS_PER_FORM bloques consecutivos,
    # o sea que el maximo indice a sortear debe ser nbloques-BLOCKS_PER_FORM
    #
    idx_primer_bloque = sorteo.sortearBloque(frec_bloques[:max_idx_bloque])
    idx_ultimo_bloque = min(nbloques,idx_primer_bloque + BLOCKS_PER_FORM)
    id_bloques = list()
    for row in db.query(f"SELECT id FROM bloque WHERE idhoja={id_hoja} AND fila={idx_fila} AND indice >= {idx_primer_bloque} AND indice < {idx_ultimo_bloque} ORDER BY indice"):
        id_bloques.append(row[0])
    print("bloques",id_bloques)
    return id_bloques

#-----------------------------------------------------------------------------

@bottle.route('/')
def root():
    bottle.response.content_type = 'text/html; charset=latin1'
    body = "<!DOCTYPE html>\n"
    body += "<html>\n<header><title></title></header>\n"
    body += "<body>"
    body += "<h1>Servidor Sandbox</h1>\n"
    body += "<p>La URL <tt>/main</tt> devuelve un archivo de texto plano (text/plain)</p>\n"
    body += "<p>El archivo es un CSV con 4 columnas:</p>\n"
    body += "<pre>HASH GIFB64 WIDTH HEIGHT\n"
    body += "<tt>HASH GIFB64 WIDTH HEIGHT\n"
    body += "... </pre>\n"
    body += "<ul>\n"
    body += "<li>HASH es un SHA256 en hexadecimal que identifica al origen de la imagen en la base de datos</li>\n"
    body += "<li>GIFB64 es la codificación en Base64 de los pixeles de la imagen en formato GIF</li>\n"
    body += "<li>WIDTH y HEIGHT son el ancho y alto de la imagen correspondientemente</li>\n"
    body += "</ul>\n"
    body += "<p>La primera fila corresponde al hash de la hoja completa, y la imagen que le sigue es el 'contexto'</p>\n"
    body += "<p>Cada fila adicional corresponde al hash, imagen, ancho y alto de un bloque</p>\n"
    body += "</body>\n</html>"
    return body    
#-----------------------------------------------------------------------------

@bottle.route('/main')
def main():
    ''' 
    Genera una consulta de LUISA para ser procesada por una APP
    El formato de la consulta es un documento de texto plano tipo CSV
    La primera fila tiene el hash de la IMAGEN (no del bloque) y el base64 de la imagen de contexto
    En el resto de las filas, la primera columna es el hash identificador de un bloque 
    y la segunda es la imagen del bloque codificada en base64
    '''
    #
    # sorteo de hoja
    #
    id_hoja = sortear_hoja()
    #
    # sorteo de bloques a mostrar dentro de la hoja
    #
    id_bloques = sortear_bloques(id_hoja)

    # obtenemos las imagenes en base64
    # 
    bloques, contexto = gen_imagenes(id_hoja, id_bloques)
    hash_hoja = contexto["hash"]
    b64ctx  = contexto["b64img"]
    width = contexto["width"]
    height = contexto["height"]
    csv = f"{hash_hoja}\t{b64ctx}\t{width}\t{height}\n"    
    #
    # obtenemos hash de bloques
    #
    for b in bloques:
        hash_bloque = b["hash"]
        b64_bloque  = b["b64img"]
        width = b["width"]
        height = b["height"]
        csv = csv + f"{hash_bloque}\t{b64_bloque}\t{width}\t{height}\n"
    bottle.response.content_type = 'text/plain; charset=latin1'
    bottle.response.set_header('Pragma','no-cache')
    return csv

#
#----------------------------------------------------------------------------------------------------
#

@bottle.route('/procesar',method="POST")
def procesar():
    '''
    Solo redirige a main
    '''
    for xHeader in bottle.request.headers:
        print(xHeader,":",bottle.request.headers[xHeader])
    prefixPath=""

    if('X-PrefixPath' in bottle.request.headers):
        prefixPath=bottle.request.headers['X-PrefixPath']

    if('X-Forwarded-Server' in bottle.request.headers):
        hostList=bottle.request.headers['X-PrefixPath'].split(",")
        host=hostList[0]
    else:
        auxUrl=bottle.request.urlparts
        host=auxUrl[0]+"://"+auxUrl[1]

    if (prefixPath!=""):
        goto="{0:s}/main".format(prefixPath)
    else:
        goto="{0:s}/main".format(host)

    print("TIME: Procesamiento de respuesta:" , time.time() - tic0, " segundos.")    

    bottle.response.set_header('Location','main')
    bottle.response.status=303

#
#----------------------------------------------------------------------------------------------------
#
@bottle.route('/image/<img:path>')
def style(img):
    return bottle.static_file(img, root=ROOTDIR+'/image',mimetype="image/jpg")
#
#----------------------------------------------------------------------------------------------------
# INICIO DE SERVIDOR
#----------------------------------------------------------------------------------------------------
#
bottle.run(host='0.0.0.0',port='8000',debug=True)

#
#----------------------------------------------------------------------------------------------------
# FIN
#----------------------------------------------------------------------------------------------------
#

