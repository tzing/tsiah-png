'use strict';

(function ($) {

    function numberWithCommas(x) {
        // https://stackoverflow.com/a/2901298/6107902
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    $.fn.refreshSubtotal = function () {
        var table = $(this).parents('form').find('table.table');
        var prices = table.find('input.price').map(function () {
            return parseFloat($(this).val());
        });

        var subtotal = 0;
        if (prices.length !== 0) {
            subtotal = prices.toArray().reduce(function (a, b) {
                return a + b;
            });
        }

        var dollar_string = gettext('${dollar}')
            .replace(/\{\s*dollar\s*\}/, numberWithCommas(subtotal));
        table.find('th.subtotal').text(dollar_string);
    }

}(jQuery));
