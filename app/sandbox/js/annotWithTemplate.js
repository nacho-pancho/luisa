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
var resizeList=[];
var resizeTimeout;
var runResize=true;
var zpdActive=false;

function getProp(p,source){
  return source.reduce(
    (prev,act)=>
              (act&&act[p])?prev.concat([act[p]]):prev
    ,[])
    .slice(-1);
}

function toggleInitZpd(lThis){
  if (!zpdActive){
    lThis.svg.zpd("toggle");
    zpdActive=true;
  }
}
$(window).on("resize.annot",function(e){
  //e.stopPropagation();
  if((!resizeTimeout)&&runResize){
    runResize=false;
    resizeTimeout=setTimeout(function(){
      resizeTimeout=null;
    //  console.log("resize window",resizeList);
      for (let elId of resizeList){
        $("#"+elId).trigger("resize.annot");
      }
      runResize=true;
    },100 );
  }
});
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
      "annotId":"annot", // container de todo.
      "tempDirUri":"/tmpl",
      "tempName":"lastTemplate",
      "tempObjId":"hiddenLoadObj",
      "viewSvgId":"viewSvg", // container del template y la imagen
      "showForm":"showForm",// Contenerdor de formularios. Es un padre (en algún nivel) de lo que contiene al formulario alpaca. Posiblemente deba ser un array.
      "formCont":"fFormCont",// en este id se aplica la función alpaca.
      "loadLinkScript": true,
      "docUri":null,
      "zpd":{},
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
      "propForms":null, // Formularios. Se setea despues.
      "optionsOnDataType":{ // opciones de acuerdo al tipo de datos, o sea en esquema
        "array":{
          //"fieldClass":"d-flex",
          "items":{
            "fieldClass":"arrayItem"
          },
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
                     },
        }
      },
      "optionsOnFieldType":{ // opciones de acuerdo al tipo de campo, o sea en opciones.
        //Se deberían aplicar despues que las otras
        "date":{
          "picker": {
              "format": "DD/MM/YYYY"
            },
        },
        "summernote":{
           "summernote":{
              "dialogsInBody": true,
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
      "controlPPId":"controlParent", // en donde se despliega el control panel (elemento padre, en donde se cuelga).
      // Debe ser distinto para cada elemento de la clase que se cree.
      "controlPanelIdx":0, // indice que controla el nombre del panel del control.
      "controlPanelActions":{}, // aquí van los eventos del control panel. El seteo por defecto de esto está en get controlPanel.
      "ontoScripts":null,
      "idClassSelector":"classes",
      "labelClassSelector":"Tipos de Cosas",
        "imagePath":"../dataServer/public/doc/ficha",
        "dblclick":(e)=>{
          e.stopPropagation();
          let k=this.svg.selectAll(".zone");
          console.log("dblclick svg:",e,k);
          // if(k){
          //   k.forEach((d)=>d.removeClass("onFormOpen")); // limpia onFormOpen... pero no debería haber. Lo sacamos por un rato :-)
          // }
        }
    },svgOpts);
    //this.checkOpts();
    this.aLoadLibH=[];
    this.aLoadOntoH=[];
    this.svg=null;
    this.svgOpts.controlPanelIdx++;
    if (!this.ident){
        this.ident=1;
    } else {
      this.ident++;
    }
    this.localId=this.ident;
    this.svgOpts.controlPanelIdx=this.localId;
  //
  //  elementos que hay que redibujar en resize para el resize de viewSvgId.
  resizeList.push(this.svgOpts.viewSvgId);
  }
// identificación de la instancia. Hay que tenerla para generar nombres distintos. La forma es usar getter y setter

static get ident(){
    return this.constructor.ident;
}

static set ident(v){
    this.constructor.ident=v;
}
get ident(){
    return this.constructor.ident;
}

set ident(v){
    this.constructor.ident=v;
}

get tempPath(){
  console.log("tempPath:",this.svgOpts.tempDirUri+"/"+this.svgOpts.tempName+".svg")
  return this.svgOpts.tempDirUri+"/"+this.svgOpts.tempName+".svg";
}

showAnnotator(){
    $("#"+this.svgOpts.annotId).removeClass("invisible");
}
/**
 * Devuelve el código del controlPanel.
 * Si se quieren agregar controles, es aquí en donde se debe hacer.
 * @return {string} Html para construir el control panel.
 */
get controlPanel(){
  let lCPanel=`
  <div id="control_${this.svgOpts.controlPanelIdx}" class="dispForm">
    <a  id="toggleZoom_${this.svgOpts.controlPanelIdx}" class="button controlButton toggleZoom" title="Zoom y Mover Todo">
      <i id="zoomIcon_${this.svgOpts.controlPanelIdx}" class="fa fa-search-plus"></i>
    </a>
    <a  id="toggleImgDrag_${this.svgOpts.controlPanelIdx}" class="button controlButton" title="Mover Imagen">
      <i id="dragImgIcon_${this.svgOpts.controlPanelIdx}" class="fa fa-arrows"></i>
    </a>
  </div>`;
  /**
   * Uno puede estar tentado a que esto sean clases, pero si son clases se pisa con seteos de diferentes anotadores en la misma página.
   * Por eso, son prefijos de los id de cada elemento.
   * En el caso particular del zoom, dado que es con zpd, es necesario generar el click para todos  los otros elementos que haya en todos los paneles
   * Por eso ahora admitimos con clases... si empieza con . asumimos que es una clase y que las identificaciones
   *   se llaman igual pero sin . y con el id del annot (ident o controlPanelIdx).
   * En este caso particular, se setea para que todos los elementos de la clase sean "solidarios" .
   * Esto tiene que ser sólo en el cambio de color.
   * @type {Object}
   */
  this.svgOpts.controlPanelActions={
        ".toggleZoom": {
            "click":(e)=>{
                // toggle zpd
                this.svg.zpd("toggle",(err,state)=>{
                  for(let elem of $(".toggleZoom")){ // para cada uno que coincide en la clase, cambiamos el color.
                      if (state){
                          if(!$(elem).hasClass("text-danger")){
                             $(elem).addClass("text-danger");
                          }
                        } else {
                            $(elem).removeClass("text-danger");
                        }
                      }
                });
          }
        },
      "toggleImgDrag": {
        "click":(e)=>{
            // toggle zpd
            let img=this.svg.select("image");
            let onDrag=img.data("onDrag");
            if (!onDrag){ // habilitamos drag
               img.drag(function(dx,dy,x,y,e){
                    this.attr({
                                transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, dy]
                            });
                  },function(){
                      this.data('origTransform', this.transform().local );
                  },null);
              $(e.target).addClass("text-danger");
            } else {
              img.undrag();
              $(e.target).removeClass("text-danger");
            }
            img.data("onDrag",(!onDrag));
      }
    }
  };
  return lCPanel;
}
/**
 * Agrega el controlPanel el id que se indique. El id, si se pasa, no tiene #.
 * @param  {string} idPanel Identificación del padre del controlPanel. Si es indefinido se toma this.svgOpts.contolPPId
 * @return {[type]}         [description]
 */
showControlPanel(idPanel){ // agrega el  controlPanel en el lugar que se indique.
  if (typeof idPanel == "undefined"){
    idPanel="#"+this.svgOpts.controlPPId
  }
  let ctrlP=$(idPanel);
  if (ctrlP.length == 0 ){
    throw("No control panel parent to add");
  }
  ctrlP.append(this.controlPanel); // Aquí se agrega el controlPanel al DOM.
  // lo siguiente en un on load?
    console.log("load controlPanel",this.svgOpts.controlPanelActions);
      for(let [button, actions] of Object.entries(this.svgOpts.controlPanelActions)){
        for (let [ev,fun] of Object.entries(actions)){
          console.log("showControlPanel: setting ",ev,`on #${button}__${this.svgOpts.controlPanelIdx}`);
          // Si el nombre del boton empieza con ., entonces seleccionamos como clase, sin _ nada.
          if(button.charAt(0)=="."){
              $(`#${button.substr(1)}_${this.svgOpts.controlPanelIdx}`).on(ev,fun);
          } else {
            $(`#${button}_${this.svgOpts.controlPanelIdx}`).on(ev,fun);
        }
        }
      }
}
hideAnnotator(){
    $("#"+this.svgOpts.annotId).addClass("invisible");
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
//  let lZpd=Snap.select('#snapsvg-zpd-'+paper.id);
  let aspect=1;
  let bbIm=0;
  let bbIm2=0;
  let svgW=this.svg.asPX("width");
  let k=this.svgOpts.zpd.select("image");
  if(k){
    //k.undrag();
    k.remove();
  }
  console.log("loadImage: imageUrl:",url);
  // if((this.svg)&&(this.svg.zpd)){
  //   this.svg.zpd("destroy");
  // }
  //$(this.svg.node.parentElement).css("visibility","hidden");
  k=this.svg.image(url); // cuando se carga la imagen hay que setear el with y height del svg.

  //this.svg.attr("width",k.asPX("width"));
  //this.svg.attr("height",k.asPX("height"));
  //bbIm=k.getBBox();

  $(k.node).on("load",(e)=>{
    if (this.svgOpts.afterLoadImage){
      this.svgOpts.afterLoadImage(this);
    }
    this.origSvg();
    $(`#${this.svgOpts.viewSvgId}`).parent().css("visibility","visible"); // hace visible el template despues de cargar la imagen.
  });
//  this.svg.prepend(k);
 //this.svg.zpd("toggle");

 this.svgOpts.zpd.prepend(k);
//k.attr("width","100%");
 //$(k.node).attr("width","100%");
 //bbIm2=this.svg.getBBox();
//aspect=svgW/imW;
//$(k.node).attr({"width":bbIm2.width,"heigth":bbIm.height*aspect});


 //this.svg.zoomTo(aspect);
 //this.svg.panTo(0,0);

 //this.svg.zpd("toggle");
 //k.data("dblclick",0);  // inicializa cuenta al cargar.
 // LOGICA DE ACTIVACION CON MOUSDOWN MOUSE UP
 //
 $(k.node).on("contextmenu",function(e){ // hay que bloquear el contextmenu.
   e.preventDefault();
 });
 // Activación con mousedown.
 // k.data("rightbutton",0); // unicializo cuenta de botón derecho.
 // k.mousedown(function(e){
 //   e.preventDefault();
 //   console.log("mousedown -img");
 //   switch(e.buttons){
 //     case 1:
 //      console.log("mousedown -img on left button:",$(e.target).attr("id"));
 //      break;
 //     case 2:
 //      console.log("mousedown -img on right button",$(e.target).attr("id"));
 //      this.data("rightbutton",this.data("rightbutton")+1);
 //      switch (this.data("rightbutton")){
 //        case 1: // habilita drag
 //          k.drag(function(dx,dy,x,y,e){
 //               this.attr({
 //                           transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, dy]
 //                       });
 //             },function(){
 //                 this.data('origTransform', this.transform().local );
 //             },null);
 //        break;
 //        case 2: // desabilita drag y resetea cuenta.
 //          k.undrag();
 //          this.data("rightbutton",0);
 //        break;
 //      }
 //    break;
 //    case 4:
 //       console.log("mousedown -img on middle button",$(e.target).attr("id"));
 //       break;
 //   }
 //
 // });
 // LO SIGUIENTE ES LA LOGICA DE ACTIVACION CON DBL dblClick
 // k.dblclick(function(e){
 //     let dblclickCount=this.data("dblclick")+1
 //      console.log("dblclick on image:",this.data("dblclick"),dblclickCount);
 //      switch (dblclickCount){
 //        case 1: // espera un tiempo adecuado y luego desactiva el "dblclick" pendiente.
 //          console.log("on 1 dblclick");
 //          setTimeout(()=>{
 //            if(this.data("dblclick")==1){
 //              this.data("dblclick",0);
 //              console.log("disable pending dblclick");
 //            } else {
 //            console.log("not disable pending dblclick",dblclickCount);
 //          }
 //        },1600);
 //        break;
 //        case 2: // activa el drag de la imagen.
 //          k.drag(function(dx,dy,x,y,e){
 //            this.attr({
 //                        transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, dy]
 //                    });
 //          },function(){
 //            this.data('origTransform', this.transform().local );
 //          },null);
 //        break;
 //        case 3: // desactiva el drag y resetea count:
 //          k.undrag();
 //          dblclickCount=0;
 //        break;
 //        }
 //        this.data("dblclick",dblclickCount);
 //  }
 //  );
  // k.drag(function(dx,dy,x,y,e){
  //   this.attr({
  //               transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, dy]
  //           });
  // },function(){
  //   this.data('origTransform', this.transform().local );
  // },null);
  //$(this.svg.node.parentElement).css("visibility","visible");

}
afterLoadTemplate(f){
  this.svgOpts.afterLoadTemplate=f;
}
afterLoadImage(f){
  this.svgOpts.afterLoadImage=f;
}
origSvg(){
  let lThis=this;
  let localSvgParentId="#"+this.svgOpts.viewSvgId;
  this.svg.zoomTo($(localSvgParentId).width()/this.svg.asPX("width"),100); // ajusta el tamaño
  setTimeout(()=>{this.svg.panTo(0,0);},105);

}
loadTemplate(){
  let lThis=this;
  let localSvgParentId="#"+lThis.svgOpts.viewSvgId;
  //$(localSvgParentId).css("visibility","hidden"); // hay que sacarlo en el load del mismo. Se vuelve a ver cuando se cargue la imagen.

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
      .css({
        "position":"relative",
        "width":"100%",
      })
      .attr("width",getComputedStyle(document.body).getPropertyValue("--widthSvg"))
      .attr("height",getComputedStyle(document.body).getPropertyValue("--heightSvg"));
    //  lThis.showTemplate();
    if ($(localSvgParentId).length == 0){
      throw("annotWithTemplate: Adjust setting in viewSvgId. Not exists dom element with id - "+lThis.svgOpts.viewSvgId);
    }

    $(localSvgParentId).append($(e.target.contentDocument.documentElement).clone());

    //lThis.svg=Snap(lThis.svgOpts.id);
    lThis.setSvg();
  //  lThis.origSvg(); en realidad no se necesita hasta que esté cargada la imagen.
     // posiciona a 0,0
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
    //$(localSvgParentId).css("visibility","visible");
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
  let type = /css$/.test(link)?"text/css":"application/javascript";
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

addPropForms(cForm){ // recorre un formulario y setea opciones por defecto
  // según el tipo de datos ( en el esquema) y segun el tipo de campo.
  // Primero hay
  let optionsOnFT=this.svgOpts.optionsOnFieldType;
  let optionsOnDT=this.svgOpts.optionsOnDataType;
  let resForm={};
  // Copiamos el primer nivel de todas las opciones a resOptions.
  let dataType=cForm["schema"]["type"];
  let fieldType=cForm["options"]["type"]||"NA";
  resForm["options"]=Object.assign({},
                                  optionsOnDT[dataType]||{},
                                  optionsOnFT[fieldType]||{}
                            ); // El orden importa para que cuando hay colisiones queden las últimas.
  resForm["schema"]=Object.assign(
                          {},
                          cForm["schema"]
                        );
  return resForm;
}


// addPropForms2(cForm){
//   let optionsOnFT=this.svgOpts.optionsOnFieldType;
//   let optionsOnDT=this.svgOpts.optionsOnDataType;
//   // Hay que recorrer el PF y según el tipo del esquema, agregar las DataType y según el tipo de las Options, el FT.
//   // Todo hay que agrgarlo en options del campo correspondiente.
//   let cp=cForm.schema;
//   switch (cForm["schema"]['type']){
//     case 'object':
//       for (let p of Object.keys(cForm["schema"]["properties"])){
//         cForm.options.fields[p]=this.addPropForms({
//             'schema':cForm["schema"]["properties"][p],
//             'options':cForm["options"]["fields"][p]?cForm["options"]["fields"][p]:{}
//           }).options; // sólo hay que asignar options.
//       }
//     break;
//     case 'array':
//      //cForm.options=objJoin(objJoin(cForm.options,optionsOnDT[cForm.schema['type']]),optionsOnFT[cForm.options['type']]);
//     cForm.options.items=this.addPropForms({ // se aplica recursivamente sobre items
//           'schema':cForm["schema"]["items"],
//           'options':cForm["options"]["items"]
//         }).options; // sólo hay que asignar options.
//     // falta agregar las opciones del nivel que no son los items
//       for (let p of Object.keys(cForm["options"]).filter((e)=>(!["items","index"].includes(e)) ) ){
//                 cForm["options"][p]=Object.assign(
//                             {},
//                             ...getProp(p,[ // devuelve la lista de valores del campo p entre toda la lista.
//                               //Luego completa la lista de parámetros de la otra función con este array.
//                                         cForm["options"][p],
//                                         optionsOnDT[cForm["schema"]['type']?cForm["schema"]['type'][p]:"UNK"],
//                                         optionsOnFT[cForm["options"]['type']?cForm["options"]['type'][p]:"UNK"]
//                                       ]
//                                     )
//                                   );
//                                 }
//     break;
//     default:
//       // Aquí deberían llegar los tipos y tomar los datos adecuados.
//       cForm.options=Object.assign(
//                       {},
//                       ...[    cForm["options"],
//                           optionsOnDT[cForm["schema"]['type']],
//                           optionsOnFT[cForm["options"]['type']]
//                     ]
//                   );
//     break;
//   }
//   return cForm;
// }

setPropForms(pf){
  let lThis=this;
  let optionsOnFT=this.svgOpts.optionsOnFieldType;
  let optionsOnDT=this.svgOpts.optionsOnDataType;
  this.propForms=this.propForms||pf;

  for (let form of Object.keys(pf)){ //form es el indice.
    let allDataCF=$(`#${lThis.svgOpts.showForm}`).data(form)||{};
    allDataCF["data"]=this.propForms[form].data; // datos actuales. esto se actualiza en varios lugares.
    allDataCF["oldData"]=allDataCF["data"]; // datos viejos. Esto es lo que se cargó del servidor.
    $(`#${lThis.svgOpts.showForm}`).data(form,allDataCF);
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
    let propForms=this.propForms||{};
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
    this.svg.zpd({ // carga zpd.
         "zoom":true,
         "pan":true,
         "drag":false,
         "zoomScale":0.05,
         "touch":false,
         "zoomThreshold":[0.05,5]
         });
    toggleInitZpd(this);
    this.svgOpts.zpd=Snap.select('#snapsvg-zpd-'+this.svg.id);

     // Handler para mantener siempre el tamaño adecuado. O no...
     var lTout;
     $(`#${this.svgOpts.viewSvgId}`).on("resize.annot",function(e){
      // console.log("RESIZE:",JSON.stringify(resizeList));
      console.log("resizing ",lThis.svgOpts.viewSvgId);
      //     e.stopPropagation();
      if((!lTout)&&($(`#${lThis.svgOpts.viewSvgId}`).css("visibility")=="hidden")){
          lTout=setTimeout(()=>{
       if ($(`#${lThis.svgOpts.viewSvgId}`).attr("lastWidth") == $(e.target).width()){
          $(`#${lThis.svgOpts.viewSvgId}`).css("visibility","visible");
        }
       },500);
      }
    //    $(`#${lThis.svgOpts.viewSvgId}`).css("visibility","hidden");
       if(!$(e.target).data("lastWidth")||$(e.target).data("lastWidth") != $(e.target).width()){
         //console.log("on resize "+lThis.svgOpts.viewSvgId);
         $(e.target).data("lastWidth",$(e.target).width());
         lThis.origSvg();
     }
     });
    for (let i of Object.keys(propForms)){
      let formName=i;
      lThis=this;
      console.log("formName:",formName,propForms[i],lThis);
      propForms[i]["options"]["form"]=propForms[i]["options"]["form"]||{}
      let rForm=propForms[i]["options"]["form"];
        propForms[i]["postRender"]= (control)=>{
            //  lThis.currForm=control;
              //control.data=lThis.commData[i];
              lThis.commData.currForm=control;
              $(`#${lThis.svgOpts.showForm}`).data(i)["currForm"]=control;
               console.log("control data:",control.data);
              //this.origData=this.currForm.getValue();
              //this.origData=this.currForm.data
              //lThis.commData.origData=lThis.copyData(this.getValue());
              //console.log("origData:",lThis.commData.origData,"lThis",lThis);
        };
      rForm["buttons"]=rForm["buttons"]||{};
      if( (rForm) && (typeof rForm["buttons"]["borrar"] == "undefined")){
        rForm["buttons"]["borrar"]={ // Borrar limpia el formulario y desecha los cambios que se hayan realizado.
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

        rForm["buttons"]["guardar"]={ // Guardar guardar los cambios. Por eso el click es complejo.
                                      // Posiblemente debiera ser una función aparte.
            "title": "Guardar",
            "styles": "btn btn-primary",
            "attributes": {
              "data-dismiss": "modal"
            }};


        rForm["buttons"]["guardar"]["click"]=function(evt){
                  //evt.stopPropagation();
                  let updtUri="";
                  let re=new RegExp(`^${prefixUrl}\/doc\/`);
                  let locStr=document.location.pathname.toString(); // path o location? path
                  if(locStr.match(re)){
                     updtUri=locStr.replace(re,`${prefixUrl}/updt/`); // se setea la URL de actualización.
                  } else {
                     updtUri=dataTest.replace(/^\/data\//,"/updt/");
                  }
                  let oldData=$(`#${lThis.svgOpts.showForm}`).data(formName)["oldData"]; // Old son los datos oldData recibidos del servidor.

                  dataToSend={ 'new':{ // inicialiación del new.
                                          '@id':"fichaRes:"+lThis.docUri,
                                          '@type':"fichaOnto:Ficha",
                                        },
                                    'old':oldData,
                                    'resUri':lThis.docUri
                                  };
                  //dataToSend['old']=lThis.propForms[formName].data;

                  //dataToSend['old']=oldData;
                  let myHeaders=new Headers();
                  let currValue=this.getValue();
                  let currVItem=currValue;
                  for(let iName of Object.keys(currValue)){
                    if(Array.isArray(currValue[iName])){
                      // Metemos el índice, si no está y estamos en un array.
                        currVItem=currValue[iName];
                        for (let idx in Object.keys(currVItem).filter((e)=>(e.charAt(0)!='@'))) { // porqué hay cosas con @? no debería !
                          console.log("idx",currVItem);
                          if(idx.match("^[0-9]+$")){
                            if(typeof currVItem[idx]['index'] == "undefined"){
                              currVItem[idx]['index']=parseInt(idx)+1; //// aquí hay que... sumar 1 .
                            }
                          }
                    }
                  }
                }
                  // if (currValue.itemName){ // Para tratar los array's... itemName tiene el nombre de lo que hay que "repetir".
                  //   currVItem=currValue[currValue.itemName];
                  // // Metemos el índice, si no está y estamos en un array.
                  //   for (let idx in Object.keys(currVItem).filter((e)=>(e.charAt(0)!='@'))) {
                  //     console.log("idx",currVItem);
                  //     if(idx.match("^[0-9]+$")){
                  //       if(typeof currVItem[idx]['index'] == "undefined"){
                  //         currVItem[idx]['index']=(1+parseInt(idx));
                  //       }
                  //     }
                  //   }
                  // }
                  myHeaders.append('Content-Type', 'application/json');
                  //let form=$(this.domEl).alpaca("get");
                //  console.log("click guardar data:",currValue);
                  dataToSend['new']=Object.assign(dataToSend['new'],currValue);
                  console.log(`Enviar a ${updtUri} los siguientes datos:`,JSON.stringify(dataToSend,"utf-8",2));
                  //console.log("Enviar a===>:",updtUri);
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
                    let allDataCF=$(`#${lThis.svgOpts.showForm}`).data(formName);
                    console.log("Proc after res",e.dataSent);
                    propForms[formName]['data']=e.dataSent;
                    //lThis.commData[formName]=lThis.copyData(e.dataSent);
                    allDataCF["data"]=e.dataSent;
                    $(`#${lThis.svgOpts.showForm}`).data(formName,allDataCF);
                  //  lThis.propForms[i].data=e.dataSent;
                  })
                  .catch((e)=>{console.log("Error on data sent:",e.mesage,e.status);});
                  console.log("despues de enviar:");
                };
              rForm["buttons"]["cerrar"]={ // Cerrar cierra la ventana pero no pierde los cambios.
                      "title": "Cerrar",
                      "styles": "btn btn-secondary",
                      "attributes": {
                        "data-dismiss": "modal"
                      }
                    };
      }
    }
    //this.svg.dblclick((e)=>alert("bdlclick en svg"));

  }

  setAnnZoneHandlers(){ // setea los handlers para los formularios y las zonas.

    let zones=this.svg.selectAll(".zone");
    let lThis=this;
    let propForms=this.propForms||null;
    function showFormHandler(e){ // OpenForm open
      // Lo primero es setear bien el LTHIS aquí dentro. Es el valor que tiene el e.target en viewSvgThis
      let lThis=$(e.target).data("viewSvgThis");
      //  lThis=lThis?lThis[0]:undefined;
      console.log("showFormHandler: target id",$(e.target).attr("id"),$(e.target).data());
        let lastFormIdx=$(e.target).data("lastFormIdx");// se guarda qué formulario es el abierto.
        console.log("showModal: lastFormIDX:",$(e.target).data("lastFormIdx"),"open on: ",lThis.svgOpts.viewSvgId);
        // si está seteado, se recuperan los datos del "buffer" al formulario. Tiene que ser los actuales.
        propForms[lastFormIdx].data=$(e.target).data(lastFormIdx).data;
         // Se despliega el formulario.
         $(`#${lThis.svgOpts.formCont}`).html("");
         $(`#${lThis.svgOpts.formCont}`).css("z-index",lThis.propForms.zIndex+10);
         $(`#${lThis.svgOpts.formCont}`).alpaca(propForms[lastFormIdx]);

        propForms.zIndex=$(e.target).css("z-index");
        //$(`#${this.svgOpts.viewSvgId}`).css("width","49%");
        $(`#${lThis.svgOpts.viewSvgId}`).addClass("onFormOpen");
        $(`#${lThis.svgOpts.viewSvgId}`).trigger("resize.annot");
    };
    function hideFormHandler(e){
      // Lo primero es setear bien el LTHIS aquí dentro. Es el valor que tiene el e.target en viewSvgThis
      let lThis = $(e.target).data("viewSvgThis");
      let lastFormIdx=$(e.target).data("lastFormIdx"); // Esto debería existir siempre porque está abierta la ventana.
      let currFormCtrl;
      let lastFormIdxData=$(e.target).data(lastFormIdx); // Esto debería existir siempre porque se cargó cuando se hizo el setPropForms.
      currFormCtrl=lastFormIdxData["currForm"]; // Esto debería estar seteado porque se pone en el postrender.
      console.log("hideModal: lastFormIDX",$(e.target).data("lastFormIdx"),"currFormCtrlData",currFormCtrl.getValue());

    //    console.log("hidden.bs.modal",e,lThis.currForm.getValue());
        if((lastFormIdx)&&(propForms[lastFormIdx])){ // debería ser true siempre.
          //propForms[lThis.lastFormIdx]["data"]=(lThis.commData.currForm)?lThis.commData.currForm.getValue():{};
          propForms[lastFormIdx]["data"]=currFormCtrl?currFormCtrl.getValue():{}; // Se setean los datos del formulario (QUE YA DEBERIAN ESTAR)
          // Se guardan los datos actuales en el buffer
          lastFormIdxData["data"]=currFormCtrl.getValue();
          $(e.target).data(lastFormIdx,lastFormIdxData);
        }

      $(`#${lThis.svgOpts.viewSvgId}`).removeClass("onFormOpen");
      $('.zone.onFormOpen').removeClass("onFormOpen");
      $(`#${lThis.svgOpts.viewSvgId}`).trigger("resize.annot");
    };
    console.log("zones",zones);
    $(`#${lThis.svgOpts.showForm}`).off('shown.bs.modal.annot');
    $(`#${lThis.svgOpts.showForm}`).on('shown.bs.modal.annot', showFormHandler);
    $(`#${lThis.svgOpts.showForm}`).off('hidden.bs.modal.annot');
    $(`#${lThis.svgOpts.showForm}`).on('hidden.bs.modal.annot', hideFormHandler);
  // zones.items.map((e)=>e.dblclick(function(e){
  //
    zones.forEach((e)=>e.dblclick(function(e){
      //let notIsFClick=$(e.target).data("notIsFClick");
      e.stopPropagation();
      let propForms=lThis.propForms||null;
      let lFormName=$(e.target.parentElement).attr("owlClassName");
      //lThis.lastFormIdx=lFormName;
      $(`#${lThis.svgOpts.showForm}`).data("lastFormIdx",lFormName); // se guarda el último formulario usado.
      if ((typeof propForms[lFormName].data=="undefined")||(jQuery.isEmptyObject(propForms[lFormName].data))) {
        //propForms[lFormName].data=Object.assign({},lThis.commData[lFormName]); // esto es para garantizar que no se pierdan los datos.
        propForms[lFormName].data=$(`#${lThis.svgOpts.showForm}`).data(lFormName).data;
        // las funciones que cierran los formularios tienen que recuperar losd datos. Pero no anda.
      }
       console.log("dblClick zone:",propForms,lThis.propForms);
       lThis.svg.selectAll(".zone.onFormOpen").forEach((e)=>e.removeClass("onFormOpen"));
       $(e.target).addClass("onFormOpen");
      //e.target.addClass("onFormOpen");
      $(`#${lThis.svgOpts.showForm}`).data("viewSvgThis",lThis); 
      // viewSvgThis tiene el dispImg en el que se activó el evento actual. Esto se necesita en showFormHandler 
       $(`#${lThis.svgOpts.showForm}`).modal({backdrop:false}); // esto ya abre el formulario.
       //$("#showForm").modal("show");
       // Todo lo que sigue sobre formCont, se va al open (show.bs) sigue
        // $(`#${lThis.svgOpts.formCont}`).html("");
        // $(`#${lThis.svgOpts.formCont}`).css("z-index",lThis.propForms.zIndex+10);
        // $(`#${lThis.svgOpts.formCont}`).alpaca(propForms[lFormName]);

        //console.log("ZONECLICK: lastFormIDX",$(`#${lThis.svgOpts.showForm}`).data("lastFormIdx"));

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
        //this.svg.selected.undrag();
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
      //a.drag(move,start,null);
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
   this.svgOpts.zpd.append(g);

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
      .zone.onFormOpen:hover {\onFormOpen
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
