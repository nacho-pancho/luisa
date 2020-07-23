
    function addScroll(){
    // agrega scroll si el bloque es muy grande.
        var imgs=$(".captcha-block");
        var captchaBlock = $(".captcha-out");
        for (i=0;i<imgs.length;i++)
        {
            var auxE=$(imgs[i]);
            if (auxE.width() > captchaBlock.width()){
                    auxE.css("overflow-x","scroll");
            } else {
                auxE.css("overflow-x", "visible");
            }
        } 
    }
    const urlParams = new URLSearchParams(window.location.search);
    var lang = urlParams.get('lang');
    //var lang=location.search.split("=")[1]; // si hay parametro, toma el valor del primer parámetro.
    var hostLocal=location.host;
// setea o trae el lenguaje
    function getLang(){
        let lLang;
        let idioma={
            'es':'Idioma',
            'en':'Language',
            'fr':'Langue'
        };
        lLang=localStorage.getItem('Lang');
        if (!lLang){
            localStorage.setItem('Lang',"es");
            lLang="es";
        }
        $("#langSelector").text(idioma[lLang]);
        $(".slang").find(".active").removeClass("active");
        $(`#${lLang}`).addClass("active");
        return lLang;
    }
    function setLang(lang){
        localStorage.setItem('Lang',lang);
        lang=getLang();
    }
    function loadLang(plang){ // recibe el lenguaje previo y carga la página correcta
        let lPrevLang=plang; // 
        let lang=getLang(); // carga el lenguaje del storage
        if (lPrevLang!=lang){
            location.search=`lang=${lang}`;
        }
        return lang;
    }
    function addLangParam(url,lang){ // Ojo... limpia todos los parámetros de la url que se le pasa.
        return url.replace(/\?.*$/,"")+"?lang="+lang;
    }
    // if (lang!={{get('lang')}}){
    //     location.search=`lang=${lang}`;
    // }
    $(document).ready(
        function(){
            //let plang=lang;
           lang=loadLang(lang); // hay que pasar el lenguaje... esto podría cargar la página o no.
            $(".slang").on("click",(ev)=>{
                ev.preventDefault();
                let plang=lang;
                setLang($(ev.target).attr("id")); // setea el idioma con el id del link del idioma.
                lang=loadLang(plang);
                // if (plang!=lang){
                //     location.search=`lang=${lang}`;
                // }
                //  $(ev.target).parent().find(".active").removeClass("active");
                //  $(ev.target).addClass("active");
            });
            $('a:not([role="button"])').on("click",(ev)=>{
                let lHref=$(ev.target).attr("href");
                if(lHref){
                    ev.preventDefault();
                    if(lHref.match(hostLocal)||(!lHref.match(/^(https?:)/))){
                        location.href=addLangParam(lHref,lang);
                    } else {
                        location.href=lHref;
                    }
                }
            }
            );
            $(window).on("resize",function(ev){
                $(".overlay").css("height",parseFloat($("#mainNav").css("height"))+5+"px");
            });
            // Se corrige el overlay
            $(".overlay").css("height",parseFloat($("#mainNav").css("height"))+5+"px");
        }
    );

    