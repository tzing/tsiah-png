'use strict';

(function ($) {

    $.fn.addUser = function (options) {
        // extend options
        var options = $.extend({
            id: -1,
            user: 'untitled',
            balance: 0
        }, options);

        // user
        var cell_user = $('<td></td>').append(options.user);

        // balance
        var input_balance = $('<input>')
            .addClass('balance')
            .attr('type', 'number')
            .attr('name', 'balance_' + options.id)
            .attr('value', options.balance)
            .change(this.refreshSubtotal);
        var cell_balance = $('<td></td>').append(input_balance);

        // create row
        var row = $('<tr></tr>');
        row.data('id', options.id)
            .append(cell_user)
            .append(cell_balance);

        this.children('tbody').append(row);

        // refresh subtotal
        $(this).refreshSubtotal();
    }

    function numberWithCommas(x) {
        // https://stackoverflow.com/a/2901298/6107902
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    $.fn.refreshSubtotal = function () {
        var table = $(this).parents('form').find('table.table');
        var prices = table.find('input.balance').map(function () {
            return parseFloat($(this).val());
        });

        if (prices.length === 0) {
            return;
        }

        var subtotal = prices.toArray().reduce(function (a, b) {
            return a + b;
        });
        table.find('tfoot .subtotal').text('$' + numberWithCommas(subtotal));
    }

}(jQuery));

$('.user.dropdown').dropdown({
    fullTextSearch: true,
    match: 'text',

    onAdd: function (id, dom, jObj) {
        var table = $(this).parents('form').find('table.table');
        table.addUser({
            id: id,
            user: jObj.clone()
                .children()
                .remove()
                .end()
                .text()
                .trim()
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

$('form.form').form({
    on: 'blur',
    fields: {
        user: {
            identifier: 'users',
            rules: [{
                type: 'empty',
                prompt: gettext('No user selected.')
            }]
        },
    }
});
