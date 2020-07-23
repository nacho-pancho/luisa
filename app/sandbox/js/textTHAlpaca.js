function onTH(e, d) {
    console.log('th datum:', d);
    //$(e.target).data('datum',d);
    this['datum'] = d;
}

$.alpaca.Fields.CustomField = $.alpaca.Fields.TextField.extend({
    getFieldType: function () {
        return "textTH";
    },
    setValue: function (value) {
        if (this.control && this.control.length > 0) {
            if (Alpaca.isEmpty(value)) {
                if (this.options['setProp']) {
                    this.control.val(this.domEl[0].datum[this.options['setProp']])
                }
            }
            else {
                if (!this.options['setProp']) {
                    this.control.val(value);
                } else {
                    this.control.val(this.domEl[0].datum[this.options['setProp']])
                }
            }
        }

        // be sure to call into base method
        if (!this.options['setProp']) {
            this.base(this.control.val());
            //        this.control.val(value);
        } else {
            this.base(this.domEl[0].datum[this.options['setProp']])
        }

        // if applicable, update the max length indicator
        this.updateMaxLengthIndicator();
    },
    getValue: function () {
        var self = this;

        return self.ensureProperType(this.data);
    },
    'onFocus': function (e) {
        $(this.domEl).on('typeahead:select',
            onTH
        );
    },
    'onBlur': function (e) {
        $(this.domEl).off('typeahead:select',
            onTH
        );
    }
});

Alpaca.registerFieldClass("textTH", Alpaca.Fields.CustomField);
