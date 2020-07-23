const LDCtx = {
	'owl': 'http://www.w3.org/2002/07/owl#',
	'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
	'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
	'xsd': "http://www.w3.org/2001/XMLSchema#",
'mh':{
	'@id':'http://mh.uy/',
	'@type':'@vocab'
	},
'fichaOnto':{
	'@id':'http://mh.uy/FichaPersonal#',
	'@type':'@vocab'
    },
'docOnto':{
        '@id': 'http://mh.uy/Documentos/',
        '@type': '@vocab'
    },
'docRes':{
	'@id':'http://mh.uy/datos/',
	'@type':'@vocab'
	},
'fichaRes':{
	'@id':'http://mh.uy/datos/FichaPersonal/',
	'@type':'@vocab'
	},
'fichaResFicha':{
	'@id':'http://mh.uy/datos/FichaPersonal/Ficha/',
	'@type':'@vocab'
	},
'fichaResReverso':{
	'@id':'http://mh.uy/datos/FichaPersonal/Reverso/',
	'@type':'@vocab'
	},
'fichaResAnverso':{
	'@id':'http://mh.uy/datos/FichaPersonal/Anverso/',
	'@type':'@vocab'
	},
'carpetasOnto':{ 
	'@id':'http://mh.uy/Carpetas#',
	'@type':'@vocab'
 },
'formAnnot':{
	 '@id':'http://mh.uy/FormAnnotations#',
	 '@type':'@vocab'
},
'contenido':{
	'@id':'http://mh.uy/Contenido#',
	'@type':'@vocab'
},
'gcat':{
	'@id':'http://www.fing.edu.uy/csi/2018/03/graphCatalog#',
	'@type':'@vocab'
	},
'mhsys':{
	'@id':'http://mh.uy/sys/',
	'@type':'@vocab'
	},
'user':{
	'@id':'http://mh.uy/sys/user/',
	'@type':'@vocab'
	},
'userOnto':{
	'@id':'http://mh.uy/sys/user#',
	'@type':'@vocab'
	},
'uGroup':{
	'@id':'http://mh.uy/sys/userGroup/',
	'@type':'@vocab'
	},
'uGroupOnto':{
	'@id':'http://mh.uy/sys/userGroup#',
	'@type':'@vocab'
    }
};


if (typeof module != "undefined") {
    console.log("cargando contexto LD Module");
    module.exports = exports = LDCtx;
} else {
    console.log("cargando fp NO Module");
    exports = LDCtx;
}