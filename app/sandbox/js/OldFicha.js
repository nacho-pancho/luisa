var ann;
//document.addEventListener("DOMContentLoaded",function(e){
$(document).ready(function(){
  console.log("dispara ready ficha.js");
  var graph=JSON.parse($("#datosFicha").text());
  console.log("graph en fichajs:",graph);
    ann=new wTemplateAnnotator({
      "ontoLinks":["/js/ontos/FichaPersonal.js"],
      "links":[],
      'tempName':'ficha4zonas',
      'selectedColor':{
        'color':getComputedStyle(document.body).getPropertyValue("--selected-zone-color"),
        'opacity':getComputedStyle(document.body).getPropertyValue("--selected-opacity-color")
      },
      'imagePath':'/img'
    });
//    console.log("loadFile:",ann);


    ann.afterLoadOntos(function(t,k){ // idem

      //$("#control").append(t.getClassSelectorHtml());
      //$("#control .owlClassSelector").alpaca(t.getAlpacaObj());
      t.afterLoadTemplate(function(lThis){
        let imgname=document.location.pathname.replace(/^\/doc\//,"/img/").replace(/\/ficha\//,"/ficha/Anverso/");
        console.log("afterLoadTemplate: antes de cargar anverso:",imgname,document.location.pathname);

        lThis.loadImage(imgname);
        console.log("afterLoadTemplate: despues de cargar anverso:",imgname);
      });
      t.loadTemplate();
      console.log("afterLoadOntos: despues de cargar template");

      $("#useImage").on("click", function(e){
        e.preventDefault();
        console.log("click on load image:",document.location.href);
        t.loadImage(document.location.href+"_a.jpg");
          //$("#archivos")[0].click();
      });
      $("#archivos").on("change",function(ev){
            console.log("change Archivos");
               var archivos=this;
               if(this.files.length > 0){
                 var readerA = new FileReader();

                //  let k=t.svg.select("image");
                //  if(k){
                //    k.remove();
                //  }
                //  k=t.svg.image(t.svgOpts.imagePath+"/"+this.files[0].name);
                //  t.svg.prepend(k)
                t.loadImage(t.svgOpts.imagePath+"/"+this.files[0].name);
              //    readerA.fname = this.files[0].name;
              //    readerA.index=0;
              //    $(readerA).on("load",function(e) {
              //      //let
              //      if (image != null){
              //        image.remove();
              //    }
              //      image=svg.image(e.target.result);
              //      svg.prepend(image);
               //
              //    });
              //  readerA.readAsDataURL(this.files[0]);
              console.log("CARGA");

        }


      });


      // fin afterLoadOntos
    });
    ann.addOntoScripts()
    // ann.afterLoadLibs(function(r,e){ // el primer parametro es el this el segundo el evento.
    //     console.log("afterLoadLibs:",r);
    //     ann.addStyle();
    //     r.addOntoScripts();
    //
    //     // $("#viewSvg").append(r.getClassSelectorHtml());
    //     // setTimeout(function(){$("#viewSvg .owlClassSelector").alpaca(ann.getAlpacaObj());},5000);
    //     //Fin afterLoadLibs
    //   });
    // // ann.afterLoadLibs(function(r,e){
    // //   setTimeout(function(){$("#viewSvg").append(r.getClassSelectorHtml());},5000);
    // // });
    // ann.addLinkScript();
  //  ann.setAllScriptLinks();
  //



// fin ready
   }

  );
