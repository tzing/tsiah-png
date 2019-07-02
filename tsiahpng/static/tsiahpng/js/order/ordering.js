'use strict';

(function ($) {
    $.fn.addTicket = function (options) {
        // extend options
        var options = $.extend({
            id: -1,
            name: 'untitled',
            price: 0,
            changeable: false
        }, options);

        // item name
        var cell_name = $('<td></td>').append(options.name);

        // quantity
        var input_qty = $('<input>')
            .attr('type', 'number')
            .attr('name', 'quantity_' + options.id)
            .attr('value', 1)
            .attr('min', 0)
            .change(function () {
                $('input[name="price_' + options.id + '"]').val($(this).val() * options.price);
                $(this).refreshSubtotal();
            })
        var cell_qty = $('<td></td>').append(input_qty);

        // price
        var input_price = $('<input>')
            .addClass('price')
            .attr('type', 'number')
            .attr('name', 'price_' + options.id)
            .attr('min', 0)
            .attr('step', 5)
            .attr('value', options.price)
            .change(this.refreshSubtotal);
        var cell_price = $('<td></td>').append(input_price);

        // note
        var cell_note = $('<td></td>');
        if (options.changeable) {
            var input_note = $('<input>')
                .attr('name', 'note_' + options.id)
                .attr('type', 'text')
                .attr('placeholder', gettext('Note for %s').replace('%s', options.name));
            cell_note.append(input_note);
        }

        // create row
        var row = $('<tr></tr>');
        row.data('id', options.id)
            .append(cell_name)
            .append(cell_qty)
            .append(cell_price)
            .append(cell_note);

        this.children('tbody').append(row);

        // refresh subtotal
        $(this).refreshSubtotal();
    }

}(jQuery));

$('.user.selection').dropdown({
    fullTextSearch: true,
    match: 'text',
});

$('.product.selection').dropdown({
    fullTextSearch: true,
    match: 'text',

    onAdd: function (id, dom, jObj) {
        var table = $(this).parents('form').find('table.table');
        table.addTicket({
            id: id,
            price: jObj.data('price'),
            name: jObj.data('name'),
            changeable: jObj.data('changeable')
        })

        // hide hint
        table.find('tr.hint').hide();
        table.find('tfoot').show();
    },

    onRemove: function (id, dom, jObj) {
        var table = $(this).parents('form').find('table.table');
        var tbody = table.children('tbody');

        // remove related rows
        tbody.find('tr').filter(function () {
            if ($(this).data('id') === id) { return this; }
        }).remove();

        // refresh subtotal
        $(this).refreshSubtotal();

        // restore hint
        if (tbody.find('tr:not(.hint)').length === 0) {
            tbody.find('tr.hint').show();
            table.find('tfoot').hide();
        }

    }
});

$('.ui.ordering.form').form({
    on: 'blur',
    fields: {
        user: {
            identifier: 'user',
            rules: [{
                type: 'empty',
                prompt: gettext('Please tell me who you are.')
            }]
        },
        product: {
            identifier: 'items',
            rules: [{
                type: 'empty',
                prompt: gettext('Cart is empty.')
            }]
        },
    }
});
