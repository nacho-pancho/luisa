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
IMGDIR   = ROOTDIR + "/img/"
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
    return   'data:image/gif;base64,%s' % data
#
#----------------------------------------------------------------------------------------------------
#
def gen_imagenes(id_hoja, idx_bloques):
    global CTX_MARGIN_H, CTX_MARGIN_V
    tic = time.time()
    #
    # 1. seleccionamos hoja en base a hash
    # 
    dbcursor = db.queryExec("SELECT hash as hashfile,rollo,filename FROM hoja WHERE hash=?",(id_hoja,))
    row      = dbcursor.fetchone()
    hash_hoja, id_rollo, filename = row[:]
    #
    # 2. necesitamos rollo para saber ruta completa
    #
    dbcursor = db.queryExec("SELECT path FROM rollo WHERE numero=?",(id_rollo,))
    path     = dbcursor.fetchone()[0]
    #
    # 3. ruta completa del archivo 
    #
    filename = "{0:s}/{1:s}.{2:s}".format(path,filename,LOCAL_EXT)
    #
    # 4. abrimos imagen usando la funcion open de Pillow
    #
    img_hoja     = Image.open(IMGDIR+filename)
    #dbcursor = db.callProc('getBloques',[id_hoja,idx_bloques,int(BLOCKS_PER_FORM/2)])    
    #OJO Cambio id_hoja por hash_hoja
    # Se agregó como último atributo el hash viejo (oldHash)
    dbcursor = db.callProc('getBloques',[hash_hoja,idx_bloques,int(BLOCKS_PER_FORM/2)])
    
    b64_bloques = []
    i00,j00,i11,j11 = 10000,10000,0,0
    box_bloques = []
    for row in dbcursor.fetchall():
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
        b64_bloques.append({'hash':hash_bloque,'b64img':b64_bloque,'width':img_bloque.size[0],'oldHash':hash_bloque })

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
    img_contexto = Image.blend(img_contexto, img_resaltar, 1.0/8.0).convert(mode='L')
    b64_contexto = gen_img_base64(img_contexto)
    return b64_bloques,b64_contexto,img_contexto.size
#
#----------------------------------------------------------------------------------------------------
# SERVICIO DE URLs / INTERFAZ DE USUARIO 
#----------------------------------------------------------------------------------------------------
#

@bottle.route('/favicon.ico')
def favicon():
    '''
    responde a la URL especificada arriba, que sólo devuelve un ícono para el sitio. 
    '''
    return bottle.static_file('favicon.ico', root=ROOTDIR,mimetype="image/ico")

#
#----------------------------------------------------------------------------------------------------
#

@bottle.route('/')
def portada():
    '''
    Página principal. Utiliza la funcionalidad de templates provista por Bottle
    y el template definido en tmpl/layout.tpl incluido en el código adjunto.
    '''
    lang=gLang(bottle.request)
    return bottle.SimpleTemplate(name="tmpl/layout.tpl", lookup=["."]).render({
            'lang':lang,
            'inner':"tmpl/"+lang+"/index_"+lang+".tpl",
            'extraclass':"luisa-portada-header",
            'horas':horas
        })

@bottle.route('/docdic')
def docdic():
    ''' 
    Genera una consulta web de LUISA.
    Cada consulta sortea una página al azar, y luego un conjunto de bloques consecutivos
    dentro de la página. Dichos bloques se muestran junto con campos de texto a rellenar
    por el usuario. Finalmente, debajo de lo bloques, se muestra una imagen que permite
    ver el contexto en donde se encuentran los bloques seleccionados, para facilitar la
    transcripción.
    '''
    global cantConexiones
    lang=gLang(bottle.request);
    tic0 = time.time()
    cantConexiones=cantConexiones+1   # sumamos una conexión.
    row={}
    if horas==0:
        #
        # sorteamos una hoja
        #
        tic = time.time()
        frec_pag = list()
        id_pag = list()
        minver_pag=list()
        cantbloques_pag=list()
        ##### Se agrega minver_pag y cant bloquespag. Cant bloques es la cantidad de bloques con el mínimo y que no son ni vacíos ni completos.
        ### Ojo. Una vez seleccionada la hoja, no interesa el estado de los bloques. Siempre hay que seleccionar uno.
        # for row in db.queryExec("SELECT id,apariciones,mincantver,cantbloques\
        #      FROM hoja\
        #      where mincantver < {0} and cantbloques > 0\
        #      order by id".format(topeBloque)):
        #### La consulta selecciona hojas que tengan una cantidad una mínima cantidad de version < el tope (5) y al menos un bloque en esa cantidad.
        #### Esto hace que una hoja no se seleccione cuando tiene al menos 5 como bloque mínimo o una cantidad de bloques mínima 0. 
        #### La segunda condición no se debería dar nunca, porque cuando se llega a 0 bloques, entonces el mínimo debería haber subido.
        #### Conclusión: sobra una condición que la sacamos.
        for row in db.queryExec("SELECT hash as hashfile,apariciones,mincantver,cantbloques\
             FROM hoja\
             where mincantver <= ? and cantbloquesmin > 1\
             order by id",(topeBloque,)):
            id_pag.append( row[0] )
            frec_pag.append( row[1] )
            minver_pag.append(row[2])
            cantbloques_pag.append(row[3])

        if (len(frec_pag)==0): ### TERMINAMOS !!!!!!!!
            page = bottle.SimpleTemplate(name="tmpl/layout.tpl", lookup=["."]).render({
                'lang':lang,
                'inner': "tmpl/terminamos_"+lang+".tpl",
                #'inner':"tmpl/statusSum.tpl",
                'horas': horas,
                'iparams': simpleStatus(),
                'extraclass': 'luisa-portada-header'
                #'overClass':"dashboard"
            })
            return page
        ### Hay que volver el sorteo a que devuelva el índice así se puede usar para seleccionar tambien el mínimo de la pagina
        idx_hoja = sorteo.sortearPagina(id_pag,cantbloques_pag, frec_pag)
        id_hoja = id_pag[idx_hoja]
        minver_hoja=minver_pag[idx_hoja]
       
        ### Aqui se podría agregar la recuperacion del mínimo a buscar.
        dbcursor = db.queryExec("SELECT hash as hashfile FROM hoja WHERE hash=?",(id_hoja,)) 
        hash_hoja = dbcursor.fetchone()[0]
        # registramos tiempo de consulta de hoja
        dt_sorteo_hoja = time.time() - tic 
        print("TIME: Sorteo de  hoja:",dt_sorteo_hoja," segundos.")
        #
        # sorteo de bloques a mostrar dentro de la hoja
        #
        tic = time.time()
        frec_bloques = list()
        indices_bloques=list()

       
        for row in db.queryExec("SELECT indice,apariciones\
             FROM bloque\
            WHERE hashhoja=? and\
                apariciones=?",(id_hoja,minver_hoja)):
            frec_bloques.append(row[1])
            indices_bloques.append(row[0])

        print("=(1)=> En la hoja",id_hoja," hay ",len(frec_bloques)," bloques disponibles. \n")
        idx_bloque = indices_bloques[sorteo.sortearBloque(frec_bloques)] ### esto ya es el hashid nuevo. Deberíamos al menos por un tiempo, agregar también el viejo?
        nbloques = len(frec_bloques)
	#
        # obtenemos las imagenes en base64
        # 
        bloques, contexto, size_contexto = gen_imagenes(id_hoja, idx_bloque)
        
        print(size_contexto)
        ctx_width = size_contexto[0]*0.75
        ctx_height = size_contexto[1]*0.75

        page = bottle.SimpleTemplate(name="tmpl/layout.tpl", lookup=["."]).render(
            {
                'lang':lang,
                'inner':"tmpl/"+lang+"/form_"+lang+".tpl",
                'horas':horas,
               'iparams': {
                    'hash_hoja':hash_hoja,
                    'page_generation_timestamp': time.time(),
                    'contexto':contexto,
                    'bloques':bloques,
                    'width':ctx_width,
                    'height':ctx_height
                    }
            }
        )

        dt_gen_pag = time.time() - tic0
        print("TIME: Generacion de pagina",dt_gen_pag," segundos.")
        cantConexiones=cantConexiones-1
        return page
    else:
        cantConexiones=cantConexiones-1
        return bottle.SimpleTemplate(name="tmpl/layout.tpl", lookup=["."]).render({
            'lang':lang,
            'inner': "tmpl/index_"+lang+".tpl",
            'extraclass': "luisa-portada-header",
            'horas': horas
        })

    
#
#----------------------------------------------------------------------------------------------------
#

@bottle.route('/procesar',method="POST")
def procesar():
    '''
    Procesa la respuesta a una consulta de LUISA. Esto se da
    luego de que el usuario completa los campos y presiona 'ingresar' o bien
    presiona enter.
    Los datos ingresados son subidos a la base de datos, se registra
    un conjunto de estadísticas anónimas mínimas (temporalmente), y luego
    se muestra automáticamente una nueva consulta.
    '''
    lang=gLang(bottle.request)
    for xHeader in bottle.request.headers:
        print(xHeader,":",bottle.request.headers[xHeader])
    prefixPath=""
    goto=""
    if('X-PrefixPath' in bottle.request.headers):
        prefixPath=bottle.request.headers['X-PrefixPath']
    if('X-Forwarded-Server' in bottle.request.headers):
        hostList=bottle.request.headers['X-PrefixPath'].split(",")
        host=hostList[0]
    else:
        auxUrl=bottle.request.urlparts
        host=auxUrl[0]+"://"+auxUrl[1]
    if (prefixPath!=""):
        goto="{0:s}/docdic".format(prefixPath)
    else:
        goto="{0:s}/docdic".format(host)
    print("TIME: Procesamiento de respuesta:" , time.time() - tic0, " segundos.")    
    #print "REDIRECT A",goto
    bottle.response.set_header('Location','docdic?lang='+lang)
    bottle.response.status=303
#
#----------------------------------------------------------------------------------------------------
#

@bottle.route('/css/<style_file:path>')
def style(style_file):
    return bottle.static_file(style_file, root=ROOTDIR+'/css',mimetype="text/css")

@bottle.route('/js/<js_file:path>')
def style(js_file):
    return bottle.static_file(js_file, root=ROOTDIR+'/js',mimetype="application/javascript")

@bottle.route('/image/<img:path>')
def style(img):
    return bottle.static_file(img, root=ROOTDIR+'/image',mimetype="image/jpg")
#
#----------------------------------------------------------------------------------------------------
#

#
#----------------------------------------------------------------------------------------------------
#
@bottle.route('/about')
def about():
    lang=gLang(bottle.request)
    return bottle.SimpleTemplate(name="tmpl/layout.tpl", lookup=["."]).render({
            'lang':lang,
            'inner':"tmpl/"+lang+"/sobreEquipo_"+lang+".tpl",
            'extraclass':"luisa-about-page"
        })

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

