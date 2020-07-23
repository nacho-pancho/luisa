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

//console.log("annotWithTemplate loading...",lDocument);
class templateEditor {
  constructor(svgOpts){
    this.document=lDocument;
  //  console.log("wTemplate",document);
    this.svgOpts=Object.assign({
      "id":"fichaASvg",
      "selectedColor":{"color":"#0000ff","opacity":0.2},
      "normalColor":{"color":"#00ff00","opacity":0.1},
      "annotId":"annot",
      "tempDirUri":"/tmpl",
      "tempName":"lastTemplate",
      "tempObjId":"hiddenLoadObj",
      "viewSvgId":"viewSvg",
      'controlId':'controles', // Este y el siguiente son específicos del editor.
      'controlList':[], // son parejas id, eventos.
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
    // se setean lo handlers indicados de los controles.
    for (let ctrl of Object.values(this.svgOpts.controlList)){
      // en cada contol hay que agregar el editor para poder accederlo despues.
      console.log("contructor editor: ctrl:",ctrl);
      $(`#${ctrl.id}`)[0].editor=this;
      console.log("contructor editor: ctrl:",ctrl,$(`#${ctrl.id}`)[0]);
      for (let ev in ctrl.events){
        $(`#${ctrl.id}`).on(ev,ctrl.events[ev]);
      }
    }
  //  this.setSvg();
  //  this.tempUri=template||"/lastTemplate";
  //  this.addStyle();
  }
get tempPath(){
  if(this.svgOpts.tempPath){
    return this.svgOpts.tempPath;
  } else {
    console.log("tempPath:",this.svgOpts.tempDirUri+"/"+this.svgOpts.tempName+".svg")
    return this.svgOpts.tempDirUri+"/"+this.svgOpts.tempName+".svg";
  }
}

set tempPath(p){
  this.svgOpts.tempPath=p;
}

showAnnotator(){
    $("#"+this.svgOpts.annotId).removeClass("hide");
}
hideAnnotator(){
    $("#"+this.svgOpts.annotId).addClass("hide");
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
newTemplate(){
  $("#"+this.svgOpts.viewSvgId).append(`<svg id="${this.svgOpts.id}"   viewport="0 0 1840 1227" viewbox="0 0 1840 1227" style="border:solid 1px blue;position:relative;top:0;left:0">
  </svg>`);
  this.setSvg();
}
loadTemplate(){
  let lThis=this;
  alert("REVISAR LOS EVENTOS");
  console.log("Load Template.",this.tempPath,"propForm",this.propForms," id ",this.svgOpts.id);
 $(document.body).prepend(`<div style="visibility:hidden;position:fixed;z-index:15000">\
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
    lThis.setZoneAllEHandlers();
    console.log("loadTemplate: on load obj:",lThis.svgOpts.viewSvgId,lThis.svgOpts.id,lThis.svg);
    let oldALT=lThis.svgOpts.afterLoadTemplate;
    // lThis.afterLoadTemplate((lLThis)=>{
    //   if(oldALT){
    //     oldALT(lThis);
    //   }
    //   parentHideId.removeClass("hide");
    // });
    if(lThis.svgOpts.afterLoadTemplate){
      lThis.svgOpts.afterLoadTemplate(lThis);
    }
    $(e.target).remove();
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

setPropForms(pf){
  this.propForms=pf;
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

  move(dx,dy) {
          let childs=this.children();
          this.attr({
                      transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, dy]
                  });
          // for (i in childs){
          //   childs[i].attr({
          //               transform: childs[i].data('origTransform') + (childs[i].data('origTransform') ? "T" : "t") + [dx, dy]
          //           });
          // }

  }

start() {
       let childs=this.children();
       this.data('origTransform', this.transform().local );
       // for(let i in childs){
       //   childs[i].data('origTransform', childs[i].transform().local );
       // }
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
    let lThis=this;
    let propForms=this.propForms||null;
    this.svg=Snap(`#${this.svgOpts.id}`);
    console.log("setSvg: svg is",this.svg," id ",this.svgOpts.id);

    this.svg.selectedColor=this.svgOpts.selectedColor; // color de lo seleccionado.
    this.svg.normalColor=this.svgOpts.normalColor; // color de lo no seleccionado.
    // hay que setear los colores de las zonas a normal.
    // this.svg.selectAll('.zone').items.map((e)=>{
    //   console.log("set color to normal zone ",e,this.svg.normalColor);
    //   e.attr("fill",this.svg.normalColor.color);
    // });
    console.log("setSvg:",this.svg);
    this.svg.dblclick(this.svgOpts.dblclick);
    // Se setea el post-render de los formularios disponibles. Por ahora no se necesita aquí.
    // for (let i of Object.keys(propForms)){
    //   let rForm=propForms[i]["options"]["form"];
    //   console.log("i:",i);
    //
    //   propForms[i]["postRender"]= (control)=>{
    //     this.currForm=control;
    //   };
    //   if( (fForm) && !("borrar" in rForm["buttons"])){
    //     rForm["buttons"]["borrar"]={
    //         "title": "Borrar",
    //         "styles": "btn btn-secondary",
    //         "attributes": {
    //           "style": "background-color:red"
    //         },
    //         "click":function(){
    //                     let form=$(this.domEl).alpaca("get");
    //                     console.log("click borrar data:",this.form.data(),this.getValue(),this.form,form);
    //                     form.data={};
    //                     form.clear();
    //                   }
    //     };
    //     rForm["buttons"]["guardar"]={
    //         "title": "Guardar",
    //         "styles": "btn btn-primary",
    //         "attributes": {
    //           "data-dismiss": "modal"
    //         },
    //         "click":function(){
    //                   let updtUri=document.location.pathname.replace(/^\/doc\//,"/updt/");
    //                   let dataToSend={'@id':"fichaRes:"+lThis.docUri,
    //                                   '@type':"fichaOnto:Ficha"
    //                                 };
    //                   let myHeaders=new Headers();
    //                   myHeaders.append('Content-Type', 'application/json');
    //                   //let form=$(this.domEl).alpaca("get");
    //                   console.log("click guardar data:",this.getValue());
    //                   dataToSend=Object.assign(dataToSend,this.getValue());
    //                   console.log("Datos a enviar:",dataToSend);
    //                   fetch(updtUri,{
    //                     method:"POST",
    //                     body:JSON.stringify(dataToSend),
    //                     headers:myHeaders,
    //                     credentials: 'same-origin',
    //                     mode: 'cors'
    //                     // headers: {
    //                     //     'content-type': 'application/json'
    //                     // }
    //                   })
    //                   .then((e)=>{console.log("Data Sent : resp:",e);})
    //                   .catch((e)=>{console.log("Error on data sent:",e.mesage,e.status);});
    //                   console.log("despues de enviar:");
    //                 }
    //     };
    //   }
    // }
    //this.svg.dblclick((e)=>alert("bdlclick en svg"));
  }

  setZoneHandlers(){
    //let lThis=this;
    //let zones=this.svg.selectAll("g[owlclassname]");
    let zones=this.svg.selectAll(".zone");
    let lThis=this;
    let propForms=this.propForms||null;
    console.log("zones",zones);
    $('#showForm').on('shown.bs.modal', (e)=> {
      // Se hace lugar :-)
      console.log("show.bs.modal",this.svgOpts.viewSvgId);
      //$(`#${this.svgOpts.viewSvgId}`).css("width","49%");
      $(`#${this.svgOpts.viewSvgId}`).addClass("onFormOpen");
    });
    $('#showForm').on('hidden.bs.modal', (e) =>{
  //    console.log("hidden.bs.modal",e,lThis.currForm.getValue());
   if((this.lastFormIdx)&&(propForms[this.lastFormIdx])){
      propForms[this.lastFormIdx]["data"]=(lThis.currForm)?lThis.currForm.getValue():{};
    }
      // Se ocupa lugar :-)
      //$(`#${this.svgOpts.viewSvgId}`).css("width","100%");

      $(`#${this.svgOpts.viewSvgId}`).removeClass("onFormOpen");
    });
  // zones.items.map((e)=>e.dblclick(function(e){
    zones.forEach((e)=>e.dblclick(function(e){
      let alp;
      let propForms=lThis.propForms||null;
      e.stopPropagation();
       console.log("dblClick zone:",propForms,lThis.propForms);
       lThis.svg.selectAll(".zone.onFormOpen").forEach((e)=>e.removeClass("onFormOpen"));
       $(e.target).addClass("onFormOpen");
      //e.target.addClass("onFormOpen");
       $('#showForm').modal({backdrop:false});
       //$("#showForm").modal("show");
        $("#fFormCont").html("");
        $("#fFormCont").alpaca(propForms[$(e.target.parentElement).attr("owlClassName")]);
        lThis.lastFormIdx=$(e.target.parentElement).attr("owlClassName");
        console.log("click zone:alp:",alp);
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
      a.drag(this.move,this.start,null);
      //svg.selected.drag(move,start,null);
  }

  dropZone(a){
    this.unselect(a);
    a.remove();
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

        for (let i in handle){
          handle[i].data("id",i);
        }

        //grips=svg.group(handle[0], handle[1],handle[2],handle[3]).attr({"id":getGripsID(a)});
        handleGroup=a.parent().append(handle[0]);
        //handleGroup=a;

        return handleGroup;
  }

  activateGrips(a){ // recibe un rectángulo
    let g=a; // Podría ser a.parent()
    let bbox=g.getBBox();
    this.putGrips(a);
    let allGrips=a.parent().selectAll(".grip");
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
    if(!this.svg){
      this.newTemplate();
    }
    let bbox=this.svg.getBBox()
    let r=this.svg.rect(bbox.width/2,bbox.height/2,50,50);
    r.attr({"id":"rect_"+this.svg.count++,
            "z-index":10});
    r.addClass("draggable zone");
    let g=this.svg.group(r).attr({"id":this.getGroupID(r)});
  //    rj=$(r.node);

    if(typeof this.svg.selected !== "undefined")
      this.unselect(this.svg.selected.select(".zone"));
    //svg.selected=r;


    this.svg.selected=this.putGrips(r);
    this.selectThis(r);
    this.deActivateGrips(r);
    console.log("svg addZone:",e.clientX,e.clientY);
  //  svg.selected.t=Snap.matrix();
    //unselect(svg.selected);
    this.setZoneEHandlers(r);
    }

    setZoneAllEHandlers(){
      let zones=this.svg.selectAll(".zone");
      zones.forEach(
        (r)=>
          this.setZoneEHandlers(r)
        );
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
