/* eslint-env es6 */
/**
 * Permite anotar una imagen en función de un template.
 * Usa bootstrap, jquery, snap,alpaca y font-awesome-4 y es para browser inicialmente.
 * Asume además que se cargaron los compilados para las clases y propiedades en jsonld.
 *
 * Un template es un svg con rectángulos que se van a poner sobre la imagen. Los rectángulos tienen ciertos atributos que informan
 * sobre las clases y formularios que se usan.
 * Antes de este hay que cargar la siguiente secuencia:
 *   <meta charset="utf-8" />
   <!--
   ESTO ES LO QUE HAY QUE CARGAR Y EN ESTE ORDEN....
 -->
 <link rel="stylesheet" href="js/font-awesome-4.7.0/css/font-awesome.min.css">

 <link rel="stylesheet" href="js/bootstrap/css/bootstrap.min.css">
 <link type="text/css" href="js/alpacaBootstrap/bootstrap/alpaca.min.css" rel="stylesheet" />

 <script src="js/jquery/jquery-3.2.1.min.js"></script>
 <!--script src="https://cdnjs.cloudflare.com/ajax/libs/d3/4.12.0/d3.min.js"></script-->
 <script src="js/popper.js"></script>
 <script src="js/Snap.svg-0.5.1/dist/snap.svg-min.js"></script>
 <script src="js/bootstrap/js/bootstrap.min.js"></script>

 <script type="text/javascript" src="./js/alpacaLib/handlebars/handlebars.min.js"></script>
 <link type="text/css" href="./js/alpacaLib/jquery-ui/themes/cupertino/jquery-ui.css" rel="stylesheet" />
 <!-- alpaca -->

 <script type="text/javascript" src="./js/alpacaBootstrap/alpaca.js"></script>
   <link type="text/css" href="./js/alpaca/build/alpaca/bootstrap/alpaca.min.css" rel="stylesheet" />
 */
var lDocument=window.document;
var CloseButton = function (context) { // boton que oculta el summernote.
  var ui = $.summernote.ui;

  // create button
  var button = ui.button({
    contents: '<i class="fa fa-times-circle" aria-hidden="true"/>',
    tooltip: 'Close',
    container: false,
    click: function () {
      // invoke insertText method with 'hello' on editor module.
      context.layoutInfo.toolbar.addClass('hide');
    }
  });

  return button.render();   // return button as jquery object
}
//var commData={};
var dataToSend={}; /// Tienen que estar a este nivel Posiblemente se puedan poner dentro del objeto
// Pero seguramente con inicializacion.
//console.log("annotWithTemplate loading...",lDocument);
class wTemplateAnnotator {
  constructor(svgOpts){
    this.document=lDocument;
  //  console.log("wTemplate",document);
    this.commData={};
    this.svgOpts=Object.assign({
      "id":"fichaASvg",
      "selectedColor":{"color":"#0000ff","opacity":0.2},
      "normalColor":{"color":"#00ff00","opacity":0.1},
      "annotId":"annot",
      "tempDirUri":"/tmpl",
      "tempName":"lastTemplate",
      "tempObjId":"hiddenLoadObj",
      "viewSvgId":"viewSvg",
      "loadLinkScript": true,
      "docUri":null,
      "jquery":"js/jquery/jquery-3.2.1.min.js",
      "afterLoadTemplate":null,
      "links": [
        "./js/css/font-awesome.min.css",
        "./js/bootstrap.min.css",
        "./js/alpacaLib/jquery-ui/themes/cupertino/jquery-ui.css",
        "./js/popper.js",
        "./js/snap.svg-min.js",
        "./js/bootstrap.min.js",
        "./js/alpacaLib/handlebars/handlebars.min.js",
        "./js/alpaca/alpaca.js"
      ],
      "propForms":null,
      "optionsOnDataType":{
        "array":{
          "hideToolbarWithChildren":false,
          "toolbarPosition":"bottom",
          "toolbarSticky":true,
           "toolbar":{
             //"toolbarPosition":'bottom',

             "showLabels": false,
             "actions": [{
                  "action": "add",
                  "iconClass":"fa fa-plus",
                  "label": "add Línea",
                  "enabled": true,
                  // "click": function(key, action) {
                  //  //var item = this.children[itemIndex];
                  //    console.log("AGREGANDO en toolbar!",key,action,this);
                  // }
              }]
           },
           "actionbarStyle":"bottom",
           "actionbar":{
                        "actions": [{
                             "action": "add",
                             "iconClass":"fa fa-user",
                             "label": "add Línea",
                             "enabled": false,
                             "click": function(key, action, itemIndex) {
                              var item = this.children[itemIndex];
                                console.log("AGREGANDO!",itemIndex,this.label);
                             }
                         },
                         {
                              "action": "up",
                              "iconClass":"fa fa-chevronUp",
                              "label": "add Línea",
                              "enabled": false,
                              "click": function(key, action, itemIndex) {
                               var item = this.children[itemIndex];
                                 console.log("AGREGANDO!",itemIndex,this.label);
                              }
                          },{
                               "action": "down",
                               "iconClass":"fa fa-chevronDown",
                               "label": "add Línea",
                               "enabled": false,
                               "click": function(key, action, itemIndex) {
                                var item = this.children[itemIndex];
                                  console.log("AGREGANDO!",itemIndex,this.label);
                               }
                           },
                     {
                     "action": "remove",
                     "label": "Eliminar",
                     "enabled": true
                      }
                       ]
                     }
        }
      },
      "optionsOnFieldType":{
        "date":{
          "picker": {
              "format": "DD/MM/YYYY"
            },
        },
        "summernote":{
           "summernote":{
                 dialogsInBody: true,
              "toolbar": [
                            ['style', ['bold', 'italic', 'underline', 'clear']],
                            ['font', ['strikethrough', 'superscript', 'subscript']],
                            ['fontsize', ['fontsize']],
                            ['color', ['color']],
                            ['para', ['ul', 'ol', 'paragraph']],
                            ['height', ['height']],
                            ['controlButtons',['close']]
                          ],
                "buttons": {
                            "close": CloseButton
                },
            "popover": {
              "air": [
                ['color', ['color']],
                ['font', ['bold', 'underline', 'clear']]
              ]
            }
          },
          "events":{
              "focus":function(e){
                  console.log("focus textarea con",this.getValue());
                  $(e.target).parents(".note-editor").find(".note-toolbar").removeClass("hide");
              },
              "ready":function(e){
                console.log("ready textarea");
                //$(e.target).css("z-index","5000 !important");
                    //$(e.target).summernote(this.options.summernote);
                    this.domEl.find(".note-toolbar").addClass("hide");
                    this.domEl.find(".note-editable").on("focus",function(e){
                    $(e.target).parents(".note-editor").find(".note-toolbar").removeClass("hide");
                });
              }
            }
          }
        },
      "ontoLinks": [],
      "linkScript": '<link rel="stylesheet" async href="js/font-awesome-4.7.0/css/font-awesome.min.css">\
    \
      <link rel="stylesheet" async href="js/bootstrap/css/bootstrap.min.css">\
      <link type="text/css" async href="js/alpacaBootstrap/bootstrap/alpaca.min.css" rel="stylesheet" />\
    \
      <!--script src="https://cdnjs.cloudflare.com/ajax/libs/d3/4.12.0/d3.min.js"></script-->\
      <script src="js/popper.js" async=true ></script>\
      <script src="js/Snap.svg-0.5.1/dist/snap.svg-min.js" async ></script>\
      <script src="js/bootstrap/js/bootstrap.min.js" async></script>\
    \
      <script type="text/javascript" src="./js/alpacaLib/handlebars/handlebars.min.js" async></script>\
      <link type="text/css" href="./js/alpacaLib/jquery-ui/themes/cupertino/jquery-ui.css" rel="stylesheet" async />\
      <!-- alpaca -->\
    \
      <script type="text/javascript" src="./js/alpacaBootstrap/alpaca.js"></script>\
        <link type="text/css" href="./js/alpaca/build/alpaca/bootstrap/alpaca.min.css" rel="stylesheet" async />',
        "ontoScripts":null,
        "idClassSelector":"classes",
        "labelClassSelector":"Tipos de Cosas",
        "imagePath":"../dataServer/public/doc/ficha",
        "dblclick":(e)=>{
          e.stopPropagation();
          let k=this.svg.selectAll(".zone");
          console.log("dblclick svg:",e,k);
          if(k){
            k.forEach((d)=>d.removeClass("onFormOpen"));
          }
        }
    },svgOpts);
    //this.checkOpts();
    this.aLoadLibH=[];
    this.aLoadOntoH=[];
    this.svg=null;

  //  this.setSvg();
  //  this.tempUri=template||"/lastTemplate";
  //  this.addStyle();
  }
get tempPath(){
  console.log("tempPath:",this.svgOpts.tempDirUri+"/"+this.svgOpts.tempName+".svg")
  return this.svgOpts.tempDirUri+"/"+this.svgOpts.tempName+".svg";
}

showAnnotator(){
    $("#"+this.svgOpts.annotId).removeClass("hide");
}
hideAnnotator(){
    $("#"+this.svgOpts.annotId).addClass("hide");
}
copyData(data){
  let currData={};
  if (typeof data=="object"){
    for (let [i,v] of Object.entries(data)){
      currData[i]=this.copyData(v);
    }
  } else {
    currData=data;
  }
  return currData;
}

loadImage(url){
  let k=this.svg.select("image");
  if(k){
    k.undrag();
    k.remove();
  }
  console.log("laodImage: imageUrl:",url);
  k=this.svg.image(url);
  $(k.node).on("load",(e)=>{
    if (this.svgOpts.afterLoadImage){
      this.svgOpts.afterLoadImage(this);
    }
  });
  this.svg.prepend(k);
  k.drag(function(dx,dy,x,y,e){
    this.attr({
                transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, dy]
            });
  },function(){
    this.data('origTransform', this.transform().local );
  },null);
}
afterLoadTemplate(f){
  this.svgOpts.afterLoadTemplate=f;
}
afterLoadImage(f){
  this.svgOpts.afterLoadImage=f;
}
loadTemplate(){
  let lThis=this;
  console.log("Load Template.",this.tempPath,"propForm",this.propForms," id ",this.svgOpts.id);
//  $(document.body).prepend(`<div style="visibility:hidden">\
//  <object id="${this.svgOpts.tempObjId}" data="${this.tempPath}" width="100%" type="image/svg+xml"></object>\
// </div>`);
$(document.body).prepend(`<div style="visibility:hidden">\
<object id="${this.svgOpts.tempObjId}" data="${this.tempPath}" width="100%" type="image/svg+xml"></object>\
</div>`);
 $(`#${this.svgOpts.tempObjId}`).on("load",function(e){
   $(e.target).css("display","none");
    $(e.target.contentDocument.documentElement)
      .attr("id",lThis.svgOpts.id)
      .css("position","relative");
    //  lThis.showTemplate();
    $("#"+lThis.svgOpts.viewSvgId).append($(e.target.contentDocument.documentElement).clone());

    //lThis.svg=Snap(lThis.svgOpts.id);
    lThis.setSvg();
    lThis.setAnnZoneHandlers();
    console.log("loadTemplate: on load obj:",lThis.svgOpts.viewSvgId,lThis.svgOpts.id,lThis.svg);
    let oldALT=lThis.svgOpts.afterLoadTemplate;
    // lThis.afterLoadTemplate((lThis)=>{
    //   if(oldALT){
    //     oldALT(lThis);
    //   }
    //   parentHideId.removeClass("hide");
    // });
    if(lThis.svgOpts.afterLoadTemplate){
      lThis.svgOpts.afterLoadTemplate(lThis);
    }
    console.log("onload Object");
  } );
// $("#"+this.svgOpts.viewSvgId).append($($("#"+this.svgOpts.tempObjId)[0].contentDocument.documentElement).clone());
  // let cont1=$(document.body).prepend('<');
  // cont1.addClass("hiddenContainer");
  // cont1.append("object").attr("id",this.svgOpts.tempObjId).attr("data",this.svgOpts.tempPath).attr("type","image/svg+xml");
}

getLinkId(link){
      link=link||"";
      return link.replace(/([^/]*\/)+([^/]+)$/g,"$2").replace(/\./g,"");
  }

afterLoadLibs(handler){ // los handlers deben setearse antes de ejecutar loadLib
  // Recibe this y el evento e, típicamente el onload del último.
  //console.log("afetLoadLibs: setting ",handler.toSource());
  this.aLoadLibH.push(handler);
}

afterLoadOntos(handler){ // los handlers deben setearse antes de ejecutar loadLib
  // Recibe this y el evento e, típicamente el onload del último.
  //console.log("afetLoadLibs: setting ",handler.toSource());
  this.aLoadOntoH.push(handler);
}
setSrcLinkScript(link){
  let type = /css$/.test(link)?"text/css":"application/javascript";ann
  let lib;
  console.log("setscriptlink:",link,this.getLinkId(link),type);
  switch (type) {
    case "text/css":
    //  lib=$(`link[href=${link}]`)[0];
      lib=document.querySelector(`#${this.getLinkId(link)}`);
      console.log("setscriptlink:",lib);
      lib.href=link;
      break;
    case "application/javascript":
    //  lib=$(`script[src=${link}]`)[0]; document.queryAll()
    lib=document.querySelector(`#${this.getLinkId(link)}`);
    lib.src=link;
      break;
  }
}



loadLib(idx,top,link,isonto,listLib){

  let lib;
  isonto=isonto||false;
  top=top||false;
  listLib=listLib||this.svgOpts.links;
  if(listLib.length!=0){
    link=link||listLib[idx];
    if ((typeof idx != "undefined")&&(typeof link != "undefined")){ // si hay idx.
      // si idx >= 0, y no hay link, hay que tomar esa posición del array por defecto y seguir...
      // if((idx >=0)&& (typeof link == "undefined")){ // si idx >=0 y no hay link, entonces se toma la posición del array por defecto.
      //   link=this.svgOpts.links[idx];
      // //  console.log("LoadLib asignando Link",link);
      // };
      //hay link, se pone el que se pasó en el lugar indicado y de allí se sigue con el array por defecto.
      let type = /css$/.test(link)?"text/css":"application/javascript";
    console.log("loadLib:","idx:",idx,"top:",top,"link:",link,"type:",type);
      switch (type) {
        case "text/css":
          lib=document.createElement("link");
          //lib.href=link;
          lib.type=type;
          lib.rel="stylesheet";
          lib.async="true";
          break;
        case "application/javascript":
          lib=document.createElement("script");
          //lib.src=link;
          lib.type="application/javascript";
          lib.async="true";
      }
        lib.id=this.getLinkId(link);
      if(top){
      document.head.prepend(lib);
    } else {
      document.head.append(lib);
    }
    var lThis=this;

    console.log("LoadLib previo:",lib,idx,listLib.length,link );
    if ((idx < this.svgOpts.links.length-1)&&(idx >= -1)){
      //si idx +1 puede estar en el array, entonces se sigue cargando el array.
      // si no, sólo se cargó el link indicado.
    lThis.idx=idx;
      lib.onload=function(e){
        console.log("onload de ",e.target.id);
        lThis.loadLib(lThis.idx+1,top,undefined,isonto,listLib);
      };
      console.log("LoadLib then:",lib,idx,listLib.length,link );
      //setTimeout((e)=>this.setSrcLinkScript(link),1000);
    }

    if (idx == listLib.length-1){ // si es el último se setean los after.
  console.log("LoadLib Else idx = length:",lib,idx,listLib.length,link );
    if(isonto){ // si se procesan las ontologías, entonces se carga el after onto
      lib.onload=function(e){
        for( let i in lThis.aLoadOntoH){
          lThis.aLoadOntoH[i](lThis,e);
        }
      }
    } else { //si no, se carga el afterlib
      lib.onload=function(e){
        for( let i in lThis.aLoadLibH){
          lThis.aLoadLibH[i](lThis,e);
        }
      }
    }
  }
  this.setSrcLinkScript(link);

  return lib;
} else { // si llegó aquí, hay un error
  this.error("LoadLib - idx or link are undefined");
  return undefined;
}
} else {
  // se corren los after directamente.
  if(isonto){ // si se procesan las ontologías, entonces se carga el after onto
      for( let i in this.aLoadOntoH){
        this.aLoadOntoH[i](this);
      }
  } else { //si no, se carga el afterlib
      for( let i in this.aLoadLibH){
        this.aLoadLibH[i](this);
      }
  }

}

//  console.log("loading",lib);

}

addLinkScript(){
  //console.log("addLinkScript",document,document.createElement);
  let p;
  if (this.svgOpts.links.length!=0){
      if(typeof $ == "undefined"){
      /*    let jq=document.createElement("script");
          jq.src=this.svgOpts.jquery;
          jq.type="application/javascript";
          jq.async=true;
          jq.onload = function() {
            var $ = window.jQuery;
          // $("head").append(lThis.svgOpts.linkScript);
        */
            p=this.loadLib(-2,true,this.svgOpts.jquery);
            //this.setSrcLinkScript(this.svgOpts.jquery);
          //  this.svgOpts.links.map((e)=>this.loadLib(e));
        }
        p=this.loadLib(0);
        //this.setAllScriptLinks();

       p=this.loadLib(-3,false,"./js/alpacaBootstrap/bootstrap/alpaca.min.css");
} else {
  let comment=document.createComment("Scripts not loaded by Template Annotator")
  document.head.append(comment);
  p=this.loadLib(-74);
}
}

setAllScriptLinks(){

  this.svgOpts.links.map((e)=>this.setSrcLinkScript(e));
}


addOntoScripts(ontoLinks){
  ontoLinks=ontoLinks||this.svgOpts.ontoLinks;
  console.log("addOntoScripts:",ontoLinks);
  if(ontoLinks.length!=0){
  //  $("head").append(ontoScripts);
  //  Se instalan desde 0, abajo,no hay link específico, son ontologías, el array es ontolink.
    this.loadLib(0,false,undefined,true,ontoLinks);
    // return  ontoLinks.map((e)=>{
    //   this.loadLib(-5,false,e);
    //
    //   this.setSrcLinkScript(e);
    // });

  } else {
      let comment=document.createComment("Ontology not loaded by Template Annotator")
      document.head.append(comment);
      this.loadLib(-74,false,undefined,true,ontoLinks);
    }

  }
addPropForms(cForm){
  let optionsOnFT=this.svgOpts.optionsOnFieldType;
  let optionsOnDT=this.svgOpts.optionsOnDataType;
  // Hay que recorrer el PF y según el tipo del esquema, agregar las DataType y según el tipo de las Options, el FT.
  // Todo hay que agrgarlo en options del campo correspondiente.
  let cp=cForm.schema;
  switch (cForm.schema['type']){
    case 'object':
      for (let p of Object.keys(cForm.schema.properties)){
        cForm.options.fields[p]=this.addPropForms({
            'schema':cForm.schema.properties[p],
            'options':(cForm.options.fields[p])?cForm.options.fields[p]:{}
          }).options; // sólo hay que asignar options.
      }
    break;
    case 'array':
     cForm.options=Object.assign({},optionsOnDT[cForm.schema['type']],optionsOnFT[cForm.options['type']],cForm.options);
      cForm.options.items=this.addPropForms({
          'schema':cForm.schema.items,
          'options':cForm.options.items
        }).options; // sólo hay que asignar options.
    break;
    default:
      // Aquí deberían llegar los tipos y tomar los datos adecuados.
      cForm.options=Object.assign({},optionsOnDT[cForm.schema['type']],optionsOnFT[cForm.options['type']],cForm.options);
    break;
  }



  return cForm;
}

setPropForms(pf){
  this.propForms=this.propForms||pf;
  for (let form of Object.keys(pf)){ //form es el indice.
    this.propForms[form]=this.addPropForms(pf[form]);
    this.commData[form]=this.copyData(this.propForms[form].data);
  }
}
getClassSelectorHtml(id,label)
{
  let res;
  id=id||this.svgOpts.idClassSelector;
  label=label||this.svgOpts.labelClassSelector;
  res=`<div id=${id} class="owlClassSelector">\n`;
  if(label){
    res=res+`<label>${label}</label>\n`;
  }
  res=res+`</div>`;
  console.log("getClassSelectorHtml:",res);
  return res;
}

getWorkingPanel(id,label){

}

getAlpacaObj(){
  console.log("classes:",ontoClases);
  let lThis=this;
  let alpacaObj={
    "schema": {
      "type": "object",
      "properties": {
        "clase": {
          "type": "string"
        }
      }
    },
    "options": {
        "fields" : {
          "clase": {
            "type": "select",
            "title": "Tipo de Objetos",
            "nonLabel":"",
            "dataSource": ontoClases['options']['fields']['clases']['dataSource'],
            "events": {
              "change": function() {
                console.log(this.name + ": change to -> " +
                        this.getValue(),lThis.svg.selected);
                        if (typeof lTHis.svg.selected != "undefined"){
                          $(lThis.svg.selected.node).attr("owlClassName",this.getValue());
                        }
                // $("#props").html(""):
                // if(this.getValue()!="None"){
                //   $("#props").alpaca(propForms[this.getValue()]);
                // }
              }
            }
          }
        }
      }
  };
  return alpacaObj;
}

  error(m){
    let errMsg="Template Annotator Failed: ";
    console.log(errMsg+m);
    throw(errMsg+m);
  }



  // checkOpts(){
  //   let o=this.svgOpts;
  //   ["selectedColor","normalColor","tempDirUri","tempUri","tempObjId"].map((e)=>
  //   {
  //     if (typeof e == "undefined"){
  //       this.error(`Field "${e}" undefined in options`);
  //     }
  //   })
  //
  // }

  setSvg(){
    this.docUri=document.location.pathname.replace(/^\/.+\/([^/]+)$/,"$1");
   //this.commData={};
    var lThis=this;
    let propForms=this.propForms||null;
    dataToSend={};
    this.svg=Snap(`#${this.svgOpts.id}`);
    console.log("setSvg: svg is",this.svg," id ",this.svgOpts.id, "docUri",lThis.docUri);

    this.svg.selectedColor=this.svgOpts.selectedColor; // color de lo seleccionado.
    this.svg.normalColor=this.svgOpts.normalColor; // color de lo no seleccionado.
    // hay que setear los colores de las zonas a normal.
    // this.svg.selectAll('.zone').items.map((e)=>{
    //   console.log("set color to normal zone ",e,this.svg.normalColor);
    //   e.attr("fill",this.svg.normalColor.color);
    // });
    console.log("setSvg:",this.svg);
    this.svg.dblclick(this.svgOpts.dblclick);
    // Se setea el post-render de los formularios disponibles.

    for (let i of Object.keys(propForms)){
      let formName=i;
      lThis=this;
      console.log("formName:",formName,propForms[i],lThis);
      let rForm=propForms[i]["options"]["form"];
        propForms[i]["postRender"]= (control)=>{
            //  lThis.currForm=control;
              //control.data=lThis.commData[i];
              lThis.commData.currForm=control;
               console.log("control data:",control.data);
              //this.origData=this.currForm.getValue();
              //this.origData=this.currForm.data
              //lThis.commData.origData=lThis.copyData(this.getValue());
              //console.log("origData:",lThis.commData.origData,"lThis",lThis);
        };
      rForm["buttons"]=rForm["buttons"]||{};
      if( (fForm) && (typeof rForm["buttons"]["borrar"] == "undefined")){
        rForm["buttons"]["borrar"]={
            "title": "Borrar",
            "styles": "btn btn-secondary",
            "attributes": {
              "style": "background-color:red"
            },
            "click":function(){
                        let form=$(this.domEl).alpaca("get");
                        console.log("click borrar data:",this.form.data(),this.getValue(),this.form,form);
                        form.data={};
                        form.clear();
                      }
        };
        rForm["buttons"]["guardar"]={
            "title": "Guardar",
            "styles": "btn btn-primary",
            "attributes": {
              "data-dismiss": "modal"
            }};


        rForm["buttons"]["guardar"]["click"]=function(evt){
                  //evt.stopPropagation();
                  let updtUri="";
                  let re=new RegExp(`^${prefixUrl}\/doc\/`);
                  if(document.location.pathname.match(re)){
                     updtUri=document.location.pathname.replace(re,`${prefixUrl}/updt/`);
                  } else {
                     updtUri=dataTest.replace(/^\/data\//,"/updt/");
                  }
                  dataToSend={ 'new':{
                                          '@id':"fichaRes:"+lThis.docUri,
                                          '@type':"fichaOnto:Ficha",
                                        },
                            //        'old':lThis.origData,
                                    'resUri':lThis.docUri
                                  };
                  dataToSend['old']=lThis.propForms[formName].data;
                  let myHeaders=new Headers();
                  let currValue=this.getValue();
                  let currVItem=currValue;
                  if (currValue.itemName){
                    currVItem=currValue[currValue.itemName];
                  // Metemos el índice, si no está y estamos en un array.
                    for (let idx in Object.keys(currVItem).filter((e)=>(e.charAt(0)!='@'))) {
                      console.log("idx",currVItem);
                      if(idx.match("^[0-9]+$")&&(typeof currVItem[idx]['index']=="undefined")){
                        currVItem[idx]['index']=(1+parseInt(idx));
                      }
                    }
                  }
                  myHeaders.append('Content-Type', 'application/json');
                  //let form=$(this.domEl).alpaca("get");
                  console.log("click guardar data:",currValue);
                  dataToSend['new']=Object.assign(dataToSend['new'],currValue);
                  console.log("Datos a enviar===>:",dataToSend);
                  console.log("Enviar a===>:",updtUri);
                //  alert(JSON.stringify(currValue,"utf-8",2));
                   //return; // para cortar y testear cosas
                  // console.log("OJO: Comentado el llamado a update !!!!");
                   fetch(updtUri,{
                    method:"POST",
                    body:JSON.stringify(dataToSend),
                    headers:myHeaders,
                    credentials: 'same-origin',
                    mode: 'cors'
                    // headers: {
                    //     'content-type': 'application/json'
                    // }
                  })
                  .then((e)=>{
                    console.log("Data Sent : resp:",e);
                    return {"dataSent":dataToSend.new,"rec":e};
                  })
                  .then((e)=>{
                    console.log("Proc after res",e.dataSent);
                    propForms[formName]['data']=e.dataSent;
                    lThis.commData[formName]=lThis.copyData(e.dataSent);
                  //  lThis.propForms[i].data=e.dataSent;
                  })
                  .catch((e)=>{console.log("Error on data sent:",e.mesage,e.status);});
                  console.log("despues de enviar:");
                };
              // rForm["buttons"]["cerrar"]={
              //         "title": "cerrar ventana",
              //         "styles": "btn btn-secondary",
              //         "attributes": {
              //           "data-dismiss": "modal"
              //         }
              //       };
              // rForm["buttons"]["cerrar"]["click"]=function(evt){
              //   if (typeof lThis.commData[formName]=="undefined"){
              //     lThis.commData[formName]=lThis.copyData(lThis.propForms[formName].data);
              //  } else {
              //     propForms[formName]['data']=lThis.copyData(lThis.commData[formName]);
              //   }
              //     console.log("EVT",evt,propForms[formName]['data']);
              //
              // }
        //  propForms[formName]['data']=currValue;
      }
    }
    //this.svg.dblclick((e)=>alert("bdlclick en svg"));
  }

  setAnnZoneHandlers(){
    //let lThis=this;
    //let zones=this.svg.selectAll("g[owlclassname]");
    let zones=this.svg.selectAll(".zone");
    let lThis=this;
    let propForms=this.propForms||null;
    console.log("zones",zones);
    $('#showForm').on('shown.bs.modal', (e)=> {
      // Se hace lugar :-)
      console.log("show.bs.modal",this.svgOpts.viewSvgId);
      propForms.zIndex=$(e.target).css("z-index");
      //$(`#${this.svgOpts.viewSvgId}`).css("width","49%");
      $(`#${this.svgOpts.viewSvgId}`).addClass("onFormOpen");
    });
    $('#showForm').on('hidden.bs.modal', (e) =>{
  //    console.log("hidden.bs.modal",e,lThis.currForm.getValue());
   if((this.lastFormIdx)&&(propForms[this.lastFormIdx])){
      propForms[this.lastFormIdx]["data"]=(lThis.commData.currForm)?lThis.commData.currForm.getValue():{};
    }
      // Se ocupa lugar :-)
      //$(`#${this.svgOpts.viewSvgId}`).css("width","100%");

      $(`#${this.svgOpts.viewSvgId}`).removeClass("onFormOpen");
    });
  // zones.items.map((e)=>e.dblclick(function(e){
    zones.forEach((e)=>e.dblclick(function(e){
      e.stopPropagation();
      let propForms=lThis.propForms||null;
      let lFormName=$(e.target.parentElement).attr("owlClassName");
      if ((typeof propForms[lFormName].data=="undefined")||(jQuery.isEmptyObject(propForms[lFormName].data))) {
        propForms[lFormName].data=Object.assign({},lThis.commData[lFormName]); // esto es para garantizar que no se pierdan los datos.
        // las funciones que cierran los formularios tienen que recuperar losd datos.
      }
       console.log("dblClick zone:",propForms,lThis.propForms);
       lThis.svg.selectAll(".zone.onFormOpen").forEach((e)=>e.removeClass("onFormOpen"));
       $(e.target).addClass("onFormOpen");
      //e.target.addClass("onFormOpen");
       $('#showForm').modal({backdrop:false});
       //$("#showForm").modal("show");
        $("#fFormCont").html("");
        $("#fFormCont").css("z-index",lThis.propForms.zIndex+10);
        $("#fFormCont").alpaca(propForms[lFormName]);
        lThis.lastFormIdx=$(e.target.parentElement).attr("owlClassName");
      //  console.log("click zone:alp:",alp);
        //$("#showForm .formTitle").text($(e.target.parentElement).attr("owlClassName"));
      },undefined));
  }


  getGroupID(a){
    return a.attr("id")+"_Group";
  }

  unselect(a){//chequar antes que svg.selected no sea undefined y pasar sólo el rectangulo.
    console.log("unselect:",a);
    if (a !== null){
        a.attr("fill",this.svg.normalColor.color)
            .attr("opacity",this.svg.normalColor.opacity);
        this.svg.selected.undrag();
        this.svg.selected=undefined;
        this.dropGrips(a);
  }
    return a;
  }

  selectThis(a){ // recibe un rectangulo y selecciona el grupo adecuado.
    console.log("select This:",a);

    this.svg.selected=a.parent(); // selected es un objeto D3 así pero this es html.
    a.attr("fill",this.svg.selectedColor.color)
      .attr("opacity",this.svg.selectedColor.opacity);
      // Al seleccionar algo se habilita el drag.
      a.drag(move,start,null);
      //svg.selected.drag(move,start,null);
  }

  dropGrips(a){
    console.log("dropGrips",a);
    var grips=a.parent().selectAll(".grip");
    for (let i=0;i<=grips.length;i++){
      if (typeof grips[i]!=="undefined")
        grips[i].remove();
    }
  }

  putGrips(a){ // recibe un rectángulo
        // Top Left
        var handleGroup,grips;
        console.log("putGrips:",a);
        var bb=a.getBBox();
        var handle=new Array();
        var gripClass={class:"grip draggable",fill:"white",stroke:"black"};
        //handle[0] = svg.circle(bb.cx,bb.y,'10').attr({class: 'grip fa fa-arrows',fill:"white",opacity:"0.5",stroke:"black"});
        // ANGULOS
        // handle[0] = svg.circle(bb.x,bb.y,5).attr(gripClass);
        // handle[1] = svg.circle(bb.x+bb.width,bb.y,5).attr(gripClass);
        // handle[2] = svg.circle(bb.x+bb.width,bb.y+bb.height,5).attr(gripClass);
        // handle[3] = svg.circle(bb.x,bb.y+bb.height,5).attr(gripClass);
        handle[0] = a.parent().circle(bb.x+bb.width,bb.y+bb.height,5).attr(gripClass);

        for (i in handle){
          handle[i].data("id",i);
        }

        //grips=svg.group(handle[0], handle[1],handle[2],handle[3]).attr({"id":getGripsID(a)});
        handleGroup=a.parent().append(handle[0]);
        //handleGroup=a;

        return handleGroup;
  }

  activateGrips(a){ // recibe un rectángulo
    var g=a; // Podría ser a.parent()
    var bbox=g.getBBox();
    this.putGrips(a);
    allGrips=a.parent().selectAll(".grip");
    for(let i=0;i<allGrips.length;i++){
      allGrips[i].drag(function(dx,dy) {
           //  let cdy=1,cdx=1;
             let cbox=this.getBBox();
             let gbox=g.getBBox();
             let cdy=dy;
             let cdx=dx;
                console.log("resize ",cbox.x,cbox.y,gbox.x,gbox.y);
             if((cbox.y>gbox.y) && (cbox.x>gbox.x)){
               cdy=dy+1;
               cdx=dx+1;
             }
              this.attr({
                          transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [cdx, cdy]
                      });
              g.attr({
                 transform: a.data("origTransform")+(this.data('origTransform') ? "S" : "s") + [1+cdx/bbox.width,1+cdy/bbox.height]+ (a.data('origTransform') ? "T" : "t") + [cdx/2, cdy/2]
              });
      },this.startResize,function(){
         a.data('origTransform', a.transform().local );
         this.data('origTransform', this.transform().local );
      });
    }
  }
  deActivateGrips(a){ // recibe un rectángulo
    this.dropGrips(a);
  }

  startResize(){
    var a=this.parent().parent().select(".zone");
    var h=this.parent().selectAll(".grip");
    let b=a.getBBox();
    a.data('origTransform', a.transform().local );
    a.data('xOrig',b.x);
    a.data('yOrig',b.y);
    this.data('origTransform', this.transform().local );
    console.log("startResize",a.data('xOrig'),a.data('yOrig'));
    for(let i=0;i<h.length;i++){
        if(""+i!==this.data("id")){
          console.log("drop grip",i,this.data("id"));
          h[i].remove();
        }
    }
  }

  addZone(e){ // realmente agrega un rectangulo con grips para resize.
    let bbox=this.svg.getBBox()
    let r=this.svg.rect(bbox.width/2,bbox.height/2,50,50);
    r.attr({"id":"rect_"+svg.count++,
            "z-index":10});
    r.addClass("draggable zone");
    let g=this.svg.group(r).attr({"id":this.getGroupID(r)});
  //    rj=$(r.node);

    if(typeof this.svg.selected !== "undefined")
      unselect(this.svg.selected.select(".zone"));
    //svg.selected=r;


    this.svg.selected=putGrips(r);
    this.selectThis(r);
    this.deActivateGrips(r);
    console.log("svg addZone:",e.clientX,e.clientY);
  //  svg.selected.t=Snap.matrix();
    //unselect(svg.selected);
    this.setZoneEHandlers(r);
    }

    setZoneEHandlers(r){ // recibe una zona, en ppio un rectángulo, que debería estar dentro de un grupo.
      // Al agregar un rectángulo, se le pone que el click lo selecciona
      let lThis=this; // hay que hacer esto para poder pasarlo adentro de los handlers
      r.click(function(e){
        e.stopPropagation();
      //  let rj=$(e.target);
        lThis.deActivateGrips(this);
        lThis.selectThis(this);

      //  console.log("click en ",rj.attr("id"),"xm",e.clientX,"ym",e.clientY,"tx",svg.selected.attr("x"),"tx",svg.selected.attr("y"));

        //console.log("en click, svg selected:",svg.selected);
      });
      r.dblclick(function(e){
        e.stopPropagation();
      //  let rj=$(e.target);
        lThis.selectThis(this);
        lThis.activateGrips(this);
      //  console.log("click en ",rj.attr("id"),"xm",e.clientX,"ym",e.clientY,"tx",svg.selected.attr("x"),"tx",svg.selected.attr("y"));

        //console.log("en click, svg selected:",svg.selected);
      });

    }

   getClasAlpObj(){ // hay que cambiarlo por fetch en la versión web
    console.log("classes:",ontoClases);
    var alpacaObj={
      "schema": {
        "type": "object",
        "properties": {
          "clase": {
            "type": "string"
          }
        }
      },
      "options": {
          "fields" : {
            "clase": {
              "type": "select",
              "title": "Tipo de Objetos",
              "nonLabel":"",
              "dataSource": ontoClases['options']['fields']['clases']['dataSource'],
              "events": {
                "change": function() {
                  console.log(this.name + ": change to -> " +
                          this.getValue(),svg.selected);
                          if (typeof svg.selected != "undefined"){
                            $(svg.selected.node).attr("owlClassName",this.getValue());
                          }
                  // $("#props").html(""):
                  // if(this.getValue()!="None"){
                  //   $("#props").alpaca(propForms[this.getValue()]);
                  // }
                }
              }
            }
          }
        }
    };
    return alpacaObj;
  };

  addStyle(){
    $("head").append(`\
      <style>\
      svg {\
        z-index:1100 !important;\
      }\
      rect.draggable {\
        cursor: move;\
      }\
\
      text.draggable {\
        cursor: pointer;\
      }\
\
      .grip {\
        font-family: "FontAwesome";\
      }\
\
      .owlClassSelector {\
        display:inline-block;\
        border: 1px;\
      }\
\
      .card-body {\
        min-height: 10em;\
        overflow-y: scroll;\
      }\
\
      .propForm {\
        left:52%;\
        z-index:1100 !important;\
        display: none;\
      }\
\
.dispImg.onFormOpen {\
  width:55%;\
  border:1px solid black;\
  position:relative\
}\
  .dispImg:not(.onFormOpen) {\
        width:90%;\
        border:1px solid black;\
        position:relative;\
      }\
      \
      .dispForm {\
        display:inline-block;\
        border: 1px;\
        height:2em;\
        font-size:20pt; \
        padding-top: 5pt;\
      }\
      .zone {\
        fill: ${this.svgOpts.normalColor.color};\
        opacity:${this.svgOpts.normalColor.opacity};\
      }\
      .zone.onFormOpen,\
      .zone.onFormOpen:hover {\
        fill: ${this.svgOpts.selectedColor.color};\
        opacity:${this.svgOpts.selectedColor.opacity-0.1} !important;\
      }
      .zone:not(.onFormOpen):hover {\
        fill: ${this.svgOpts.selectedColor.color};\
        opacity:${this.svgOpts.selectedColor.opacity};\
      }\
      </style>\
      `
    );
  }

}
