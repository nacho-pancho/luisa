function onTH(e, d) {
    console.log('th datum:', d);
    //$(e.target).data('datum',d);
    this['datum'] = d;
}

$.alpaca.Fields.CustomField = $.alpaca.Fields.TextField.extend({
    getFieldType: function () {
        return "button";
    },
    setValue: function (value) {
        // be sure to call into base method
        // if applicable, update the max length indicator
        //this.updateMaxLengthIndicator();
    },
    getValue: function () {
        var self = this;
        return self.ensureProperType(this.data);
    },
   /*  'onFocus': function (e) {
        $(this.domEl).on('typeahead:select',
            onTH
        );
    },
    'onBlur': function (e) {
        $(this.domEl).off('typeahead:select',
            onTH
        );
    }, */
    'view': {
        'type':'display',
        'templates': {
            'control-button':`<button type="{{options.bType}}" 
                                name="{{options.name}}" 
                                class="fieldButton {{options.fieldClass}}">{{#if data{{options.content}}</button>`,
        }
    }
});

Alpaca.registerFieldClass("button", Alpaca.Fields.CustomField);
