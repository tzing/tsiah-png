'use strict';

(function ($) {

    // Prepend header text on table cell since sometime it is stacked or too
    // far from the header.
    $.fn.prependHeader = function (options) {
        // assert type
        if (this.length === 0) {
            console.log('No element is specific.');
            return;
        } else if (this.prop("tagName") !== 'TABLE') {
            console.log('Except table, got ' + this.prop("tagName"));
            return;
        }

        // extend options
        var options = $.extend({
            numSkip: 0,
            boxClass: ''
        }, options);

        options.numSkip += 1;

        // get header text
        var headerText = this
            .find('thead th:nth-child(1n+' + options.numSkip + ')')
            .map(function (idx, elem) {
                return $(elem).text();
            });

        if (headerText.length === 0) {
            return;
        }

        // prepend
        var tbody = this.children('tbody');
        $.each(headerText, function (idx, text) {
            tbody
                .find('tr td:nth-child(' + (idx + options.numSkip) + ')')
                .filter(function () {
                    if ($(this).text()) {
                        return this;
                    }
                })
                .prependText({
                    text: text,
                    class: options.boxClass
                });
        });
    }

    $.fn.prependText = function (options) {
        var options = $.extend({
            text: 'TEXT',
            class: ''
        }, options);

        var textBox = $('<div></div>')
            .addClass(options.class)
            .text(options.text);
        this.prepend(textBox);
    }

}(jQuery));

$('table.sortable')
    .tablesort();

$('table.transaction')
    .prependHeader({
        numSkip: 3,
        boxClass: 'mobile only'
    });
