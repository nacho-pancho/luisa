/* eslint-env es6
sourceType= module;*/
var ___ontoSchema___={
  "schema": {
    "type": "object",
    "properties": {
      "clase": {
        "type": "string"
      }
    }
  }
};
var ___ontoClases___={
  "options": {
    "fields": {
      "clases": {
        "type": "select",
        "dataSource": [
          "DatosSocioPoliticos",
          "DatosPersonales",
          "DatosItemReverso",
          "DatosBiometricos",
          "DatosCiviles"
        ]
      }
    }
  }
};
var ___propForms___={
  "DatosSocioPoliticos": {
    "schema": {
      "type": "object",
      "properties": {
        "actuacion_F": {
          "type": "string"
        },
        "capital_F": {
          "type": "string"
        },
        "ideologia_F": {
          "type": "string"
        },
        "ocupacion_F": {
          "type": "string"
        },
        "otrasActividades_F": {
          "type": "string"
        },
        "profesion_F": {
          "type": "string"
        },
        "situacionEconomica_F": {
          "type": "string"
        },
        "vehiculo_F": {
          "type": "string"
        }
      },
      "title": "Datos Socio Politicos"
    },
    "options": {
      "fields": {
        "actuacion_F": {
          "order": "4",
          "type": "text",
          "label": "Actuación"
        },
        "capital_F": {
          "order": "7",
          "type": "text",
          "label": "Capital"
        },
        "ideologia_F": {
          "order": "5",
          "type": "text",
          "label": "Ideología"
        },
        "ocupacion_F": {
          "order": "2",
          "type": "text",
          "label": "Ocupación"
        },
        "otrasActividades_F": {
          "order": "3",
          "type": "text",
          "label": "Otras Actividades"
        },
        "profesion_F": {
          "order": "1",
          "type": "text",
          "label": "Profesión"
        },
        "situacionEconomica_F": {
          "order": "6",
          "type": "text",
          "label": "Situación Económica"
        },
        "vehiculo_F": {
          "order": "8",
          "type": "text",
          "label": "Vehículo"
        }
      },
      "form": {
        "buttons": {
          "cancel": {
            "title": "Cerrar",
            "styles": "btn btn-secondary",
            "attributes": {
              "data-dismiss": "modal"
            }
          }
        }
      }
    }
  },
  "DatosPersonales": {
    "schema": {
      "type": "object",
      "properties": {
        "aliasNombre_F": {
          "type": "string"
        },
        "apellidoMaterno_F": {
          "type": "string"
        },
        "apellidoPaterno_F": {
          "type": "string"
        },
        "cedula_F": {
          "type": "string"
        },
        "credencial_F": {
          "type": "string"
        },
        "domicilio_F": {
          "type": "string"
        },
        "fechaNacimiento_F": {
          "type": "string"
        },
        "lugarNacimiento_F": {
          "type": "string"
        },
        "nacionalidad_F": {
          "type": "string"
        },
        "nombre_F": {
          "type": "string"
        },
        "seccionPolicial_F": {
          "type": "string"
        },
        "telefono_F": {
          "type": "string"
        }
      },
      "title": "Datos Personales"
    },
    "options": {
      "fields": {
        "aliasNombre_F": {
          "order": "12",
          "type": "text",
          "label": "Alias de la Persona"
        },
        "apellidoMaterno_F": {
          "order": "2",
          "type": "text",
          "label": "Apellido Materno"
        },
        "apellidoPaterno_F": {
          "order": "1",
          "type": "text",
          "label": "Apellido Paterno"
        },
        "cedula_F": {
          "order": "5",
          "type": "text",
          "label": "Cédula de Identidad"
        },
        "credencial_F": {
          "order": "4",
          "type": "text",
          "label": "Credencial Cívica"
        },
        "domicilio_F": {
          "order": "6",
          "type": "text",
          "label": "Domicilio"
        },
        "fechaNacimiento_F": {
          "order": "11",
          "type": "text",
          "label": "Fecha de Nacimiento"
        },
        "lugarNacimiento_F": {
          "order": "10",
          "type": "text",
          "label": "Lugar de Nacimiento"
        },
        "nacionalidad_F": {
          "order": "9",
          "type": "text",
          "label": "Nacionalidad"
        },
        "nombre_F": {
          "order": "3",
          "type": "text",
          "label": "Nombre"
        },
        "seccionPolicial_F": {
          "order": "8",
          "type": "text",
          "label": "Sección Policial"
        },
        "telefono_F": {
          "order": "7",
          "type": "text",
          "label": "Teléfono"
        }
      },
      "form": {
        "buttons": {
          "cancel": {
            "title": "Cerrar",
            "styles": "btn btn-secondary",
            "attributes": {
              "data-dismiss": "modal"
            }
          }
        }
      }
    }
  },
  "DatosItemReverso": {
    "schema": {
        "type":"object",
        "title": "Legajo",
      "properties":{
        "itemName":{
          "type":"string",
          "default":"itemReverso"
        },
        "itemReverso":{
          "type": "array",
          "items":{
            "title":"<hr/>",
            "type":"object",
            "properties": {
              "index":{
                "type":"integer",
                "title":"Linea"
              },
              "fechaItem_F": {
                "type": "string",
                  "title": "Fecha"
              },
              "documentoItem_F": {
                "type": "string",
                  "title": "Documento"
              },
              "origenItem_F": {
                  "type": "string",
                    "title": "Origen"
                },
                "antecedentesItem_F": {
                  "type": "string",
                  "title": "Antededentes"
                }
              } // properties
            } //items
          } //itemReverso
      } //properties
    }, //schema
    "options": {
      "fields":{
        "itemName":{
          "type":"hidden",
          "label":""
        },
        "itemReverso":  {
          "label":"", //
            "items" : {
                "size":50,
                "fields" : {
                  "index":{
                    "order":"0",
                    "type":"text",
                    "label": "Linea",
                    "fieldClass":"col-sm-2"
              },
                  "antecedentesItem_F": {
                    "order": "4",
                    "type": "summernote",
                    "label": "Antededentes",
                    "fieldClass":"col-sm-12"
                  },
              "documentoItem_F": {
                  "order": "2",
                  "type": "text",
                  "label": "Documento",
                  "fieldClass":"col-sm-6"
              },
              "fechaItem_F": {
                    "order": "1",
                    "type": "date",
                    "label": "Fecha",
                    "fieldClass":"col-sm-4"
              },
              "origenItem_F": {
                  "order": "3",
                  "type": "text",
                  "label": "Origen",
                  "fieldClass":"col-sm-12"
              }
            }
          }
      }
      },
      "form": {
        "buttons": {
          "cancel": {
            "title": "Cerrar",
            "styles": "btn btn-secondary",
            "attributes": {
              "data-dismiss": "modal"
            }
          }
        }
      }
  }
},
  "DatosBiometricos": {
    "schema": {
      "type": "object",
      "properties": {
        "colorCabello_F": {
          "type": "string"
        },
        "colorOjos_F": {
          "type": "string"
        },
        "complexion_F": {
          "type": "string"
        },
        "estatura_F": {
          "type": "string"
        },
        "peso_F": {
          "type": "string"
        },
        "raza_F": {
          "type": "string"
        },
        "señas_F": {
          "type": "string"
        }
      },
      "title": "Datos Biometricos"
    },
    "options": {
      "fields": {
        "colorCabello_F": {
          "order": "4",
          "type": "text",
          "label": "Color de cabello"
        },
        "colorOjos_F": {
          "order": "5",
          "type": "text",
          "label": "Color de ojos"
        },
        "complexion_F": {
          "order": "6",
          "type": "text",
          "label": "Complexión"
        },
        "estatura_F": {
          "order": "2",
          "type": "text",
          "label": "Estatura (m.cm)"
        },
        "peso_F": {
          "order": "3",
          "type": "text",
          "label": "Peso (Kg)"
        },
        "raza_F": {
          "order": "1",
          "type": "text",
          "label": "Raza"
        },
        "señas_F": {
          "order": "7",
          "type": "text",
          "label": "Señas"
        }
      },
      "form": {
        "buttons": {
            "cancel": {
            "title": "Cerrar",
            "styles": "btn btn-secondary",
            "attributes": {
              "data-dismiss": "modal"
            }
          }
        }
      }
    }
  }
  ,
  "DatosCiviles": {
    "schema": {
      "type": "object",
      "properties": {
        "conyugueApellidoMaterno_F": {
          "type": "string"
        },
        "conyugueApellidoPaterno_F": {
          "type": "string"
        },
        "conyugueEstado_F": {
          "type": "string"
        },
        "conyugueNacionalidad_F": {
          "type": "string"
        },
        "conyugueNombre_F": {
          "type": "string"
        },
        "estadoCivil_F": {
          "type": "string"
        },
        "estudiosCursados_F": {
          "type": "string"
        },
        "madreApellidoMaterno_F": {
          "type": "string"
        },
        "madreApellidoPaterno_F": {
          "type": "string"
        },
        "madreEstado_F": {
          "type": "string"
        },
        "madreNacionalidad_F": {
          "type": "string"
        },
        "madreNombre_F": {
          "type": "string"
        },
        "otrosDatosCiviles_F": {
          "type": "string"
        },
        "padreApellidoMaterno_F": {
          "type": "string"
        },
        "padreApellidoPaterno_F": {
          "type": "string"
        },
        "padreEstado_F": {
          "type": "string"
        },
        "padreNacionalidad_F": {
          "type": "string"
        },
        "padreNombre_F": {
          "type": "string"
        }
      },
      "title": "Datos Civiles"
    },
    "options": {
      "fields": {
        "conyugueApellidoMaterno_F": {
          "order": "3",
          "type": "text",
          "label": "Conyugue: apellido materno"
        },
        "conyugueApellidoPaterno_F": {
          "order": "2",
          "type": "text",
          "label": "Conyugue: apellido paterno"
        },
        "conyugueEstado_F": {
          "order": "6",
          "type": "text",
          "label": "Conyugue: estado"
        },
        "conyugueNacionalidad_F": {
          "order": "5",
          "type": "text",
          "label": "Conyugue: nacionalidad"
        },
        "conyugueNombre_F": {
          "order": "4",
          "type": "text",
          "label": "Conyugue: nombre"
        },
        "estadoCivil_F": {
          "order": "1",
          "type": "text",
          "label": "Estado civil"
        },
        "estudiosCursados_F": {
          "order": "18",
          "type": "text",
          "label": "Estudios cursados"
        },
        "madreApellidoMaterno_F": {
          "order": "14",
          "type": "text",
          "label": "Madre: apellido materno"
        },
        "madreApellidoPaterno_F": {
          "order": "13",
          "type": "text",
          "label": "Padre: apellido paterno"
        },
        "madreEstado_F": {
          "order": "17",
          "type": "text",
          "label": "Madre: estado"
        },
        "madreNacionalidad_F": {
          "order": "16",
          "type": "text",
          "label": "Madre: nacionalidad"
        },
        "madreNombre_F": {
          "order": "15",
          "type": "text",
          "label": "Madre: nombre"
        },
        "otrosDatosCiviles_F": {
          "order": "19",
          "type": "text",
          "label": "Otros datos"
        },
        "padreApellidoMaterno_F": {
          "order": "9",
          "type": "text",
          "label": "Padre: apellido materno"
        },
        "padreApellidoPaterno_F": {
          "order": "10",
          "type": "text",
          "label": "Padre: apellido paterno"
        },
        "padreEstado_F": {
          "order": "12",
          "type": "text",
          "label": "Padre: estado"
        },
        "padreNacionalidad_F": {
          "order": "11",
          "type": "text",
          "label": "Padre: nacionalidad"
        },
        "padreNombre_F": {
          "order": "10",
          "type": "text",
          "label": "Padre: nombre"
        }
      },
      "form": {
        "buttons": {
          "cancel": {
            "title": "Cerrar",
            "styles": "btn btn-secondary",
            "attributes": {
              "data-dismiss": "modal"
            }
          }
        }
      }
    }
  }
};
var          ___PropZone___={
  "actuacion_F": "DatosSocioPoliticos",
  "capital_F": "DatosSocioPoliticos",
  "ideologia_F": "DatosSocioPoliticos",
  "ocupacion_F": "DatosSocioPoliticos",
  "otrasActividades_F": "DatosSocioPoliticos",
  "profesion_F": "DatosSocioPoliticos",
  "situacionEconomica_F": "DatosSocioPoliticos",
  "vehiculo_F": "DatosSocioPoliticos",
  "aliasNombre_F": "DatosPersonales",
  "apellidoMaterno_F": "DatosPersonales",
  "apellidoPaterno_F": "DatosPersonales",
  "cedula_F": "DatosPersonales",
  "credencial_F": "DatosPersonales",
  "domicilio_F": "DatosPersonales",
  "fechaNacimiento_F": "DatosPersonales",
  "lugarNacimiento_F": "DatosPersonales",
  "nacionalidad_F": "DatosPersonales",
  "nombre_F": "DatosPersonales",
  "seccionPolicial_F": "DatosPersonales",
  "telefono_F": "DatosPersonales",
  "antecedentesItem_F": "DatosItemReverso",
  "documentoItem_F": "DatosItemReverso",
  "itemReverso":"DatosItemReverso" ,
  "itemName":"DatosItemReverso",
  "fechaItem_F": "DatosItemReverso",
  "origenItem_F": "DatosItemReverso",
  "colorCabello_F": "DatosBiometricos",
  "colorOjos_F": "DatosBiometricos",
  "complexion_F": "DatosBiometricos",
  "estatura_F": "DatosBiometricos",
  "peso_F": "DatosBiometricos",
  "raza_F": "DatosBiometricos",
  "señas_F": "DatosBiometricos",
  "conyugueApellidoMaterno_F": "DatosCiviles",
  "conyugueApellidoPaterno_F": "DatosCiviles",
  "conyugueEstado_F": "DatosCiviles",
  "conyugueNacionalidad_F": "DatosCiviles",
  "conyugueNombre_F": "DatosCiviles",
  "estadoCivil_F": "DatosCiviles",
  "estudiosCursados_F": "DatosCiviles",
  "madreApellidoMaterno_F": "DatosCiviles",
  "madreApellidoPaterno_F": "DatosCiviles",
  "madreEstado_F": "DatosCiviles",
  "madreNacionalidad_F": "DatosCiviles",
  "madreNombre_F": "DatosCiviles",
  "otrosDatosCiviles_F": "DatosCiviles",
  "padreApellidoMaterno_F": "DatosCiviles",
  "padreApellidoPaterno_F": "DatosCiviles",
  "padreEstado_F": "DatosCiviles",
  "padreNacionalidad_F": "DatosCiviles",
  "padreNombre_F": "DatosCiviles"
};

var fp={"propZone":___PropZone___,"ontoSchema":___ontoSchema___,"propForms":___propForms___,"ontoClases":___ontoClases___};
if(typeof module != "undefined"){
    console.log("cargando fp Module");
		  module.exports=exports=fp;
} else {
  console.log("cargando fp NO Module");
		  exports=fp;
}

//export {fp};
