/* eslint-env es6 */
var ann;
var dataForm;
var annR;

//document.addEventListener("DOMContentLoaded",function(e){
$(document).ready(function(){
  console.log("dispara ready ficha.js: prefixUrl",prefixUrl);
  //var user=JSON.parse($("#userData").text());
  //console.log("================>user:",user);
  //var propForms=JSON.parse($("#formularios").text());
//  console.log("datos en propForms en fichajs:",propForms['DatosPersonales'].data);
    ann=new wTemplateAnnotator({
      "ontoLinks":[`${prefixUrl}/js/ontos/fp.js`],
      "links":[],
      'tempName':'ficha4zonas',
      'id':'anversoSvg',  // !importante para manejar 2
      'tempObjId':'anvHidden', // !importante para manejar 2
      'tempDirUri':`${prefixUrl}/tmpls`,
      'viewSvgId': "anversoFicha", // !importante para manejar 2
      'controlPPId':'controlPAnverso', // !importante para manejar 2
      'selectedColor':{
        'color':getComputedStyle(document.body).getPropertyValue("--selected-zone-color"),
        'opacity':getComputedStyle(document.body).getPropertyValue("--selected-opacity-color")
      },
     'imagePath':'/img'
    });
//    console.log("loadFile:",ann);
/// Hasta aquí es el anverso. Ahora viene lo mismo para el reverso.
annR=new wTemplateAnnotator({
  "ontoLinks":[],
  "links":[],
  'tempName':'fichaReverso',
  'id':'reversoSvg', // !importante para manejar 2
  'tempDirUri':`${prefixUrl}/tmpls`,
  'tempObjId':'revHidden', // !importante para manejar 2
  'viewSvgId': "reversoFicha", // !importante para manejar 2
  'controlPPId':'controlPReverso', // !importante para manejar 2
  'normalColor':{
    //'color':getComputedStyle(document.body).getPropertyValue("--selected-zone-color"),
    //'opacity':getComputedStyle(document.body).getPropertyValue("--selected-opacity-color")
    'color':'#000000',
    'opacity':1
  },
 'imagePath':'/img'
});

// Ojo Con el orden.
  // cargar panel de control
    ann.showControlPanel();
    annR.showControlPanel();

    ann.hideAnnotator();
    ann.afterLoadOntos(function(t,k){ // Despues de cargar la ontología... en el anverso...
    
      let dataname=document.location.pathname.replace(/\/doc\//,"/data/");
      console.log("ficha.js: afterLoadOntos");
      dataForm=fp.propForms;
      t.afterLoadTemplate(function(lThis){ // Despues de cargar el template en el anverso...
        let imgname=document.location.pathname.replace(/\/doc\//,"/img/").replace(/\/ficha\//,"/ficha/Anverso/");
        console.log("afterLoadTemplate: antes de cargar anverso:",imgname,document.location.pathname);
        lThis.afterLoadImage((e)=>{
          lThis.showAnnotator();
        });
        lThis.loadImage(imgname);
        console.log("afterLoadTemplate: despues de cargar anverso:",imgname,"pronto para cargar datos de:",dataname);
        // Trae los datos del servidor que corresponden a la ficha de trabajo.
  //      t.showAnnotator();
        // fin trae datos.
      });
      fetch(dataname,{credentials:"same-origin"})
        .then(function(resp){
          console.log("===>Rresp.body",resp.url);
          resp.json()
          .then((d)=>{ // Los formlarios se completan con los datos recibidos.
            // seteamos la variable general para acceder a los datos.
            // lastData=d;          
            for (let k of Object.keys(d.propForms)){
              if(k!="UNK"){
                dataForm[k]=dataForm[k]||{};
                dataForm[k]['data']=d.propForms[k];
              }
            }
            console.log("===>Data:",dataForm);

              t.setPropForms(dataForm);
              t.docUri=d.docUri;
              t.loadTemplate();
              //annR.setPropForms(dataForm);
              annR.propForms=ann.propForms;
              annR.afterLoadTemplate(function(lThis){
                let imgname=document.location.pathname.replace(/\/doc\//,"/img/").replace(/\/ficha\//,"/ficha/Reverso/");
                console.log("afterLoadTemplate: antes de cargar reverso:",imgname,document.location.pathname);
                lThis.afterLoadImage((e)=>{
                  console.log("AfterLoadImage annR:");
                  lThis.showAnnotator();
                });
                lThis.loadImage(imgname);
              });
              //annR.addOntoScripts();
              annR.setPropForms(dataForm);

              annR.loadTemplate();
              console.log("afterLoadOntos: despues de cargar template");
            })
          .catch((err)=>{console.log("=======> error en fetch.json:",err);});
        })
        .catch((err)=>{console.log("error en fetch:",err);});

      });
ann.addOntoScripts();



//annR.hideAnnotator();
// annR.afterLoadOntos(function(t,k){ // idem
// //   t.setPropForms(propForms);
//   // console.log("ann propforms:",ann.propForms);
//   //$("#control").append(t.getClassSelectorHtml());
//   //$("#control .owlClassSelector").alpaca(t.getAlpacaObj());
//   let dataname=document.location.pathname.replace(/\/doc\//,"/data/");
//   console.log("ficha.js: afterLoadOntos");
//  t.setPropForms(dataForm);
//
//   t.afterLoadTemplate(function(lThis){
//     let imgname=document.location.pathname.replace(/\/doc\//,"/img/").replace(/\/ficha\//,"/ficha/Reverso/");
//     console.log("afterLoadTemplate: antes de cargar reverso:",imgname,document.location.pathname);
//     t.afterLoadImage((e)=>{
//       console.log("AfterLoadImage annR:");
//       e.showAnnotator();
//     })
//     lThis.loadImage(imgname);
//     t.docUri=d.docUri;
//     t.loadTemplate();
//     console.log("afterLoadTemplate: despues de cargar reverso:",imgname,"pronto para cargar datos de:",dataname);
//     // Trae los datos del servidor que corresponden a la ficha de trabajo.
//     //t.showAnnotator();
//     // fin trae datos.
//   });
//   // fetch(dataname,{credentials:"same-origin"})
//   //   .then(function(resp){
//   //     console.log("===>Rresp.body",resp.url);
//   //     resp.json()
//   //     .then((d)=>{
//   //       let dataForm=fp.propForms;
//   //       for (let k of Object.keys(d.propForms)){
//   //         dataForm[k]['data']=d.propForms[k];
//   //       }
//   //       console.log("===>Data:",dataForm);
//   //
//   //         t.setPropForms(dataForm);
//   //
//   //   t.docUri=d.docUri;
//   //   t.loadTemplate();
//   //   console.log("afterLoadOntos: despues de cargar template");})
//   //     .catch((err)=>{console.log("=======> error en fetch.json:",err);});
//   //   })
//   //   .catch((err)=>{console.log("error en fetch:",err);});
//
//   // fin afterLoadOntos
//







// fin ready
   }

  );