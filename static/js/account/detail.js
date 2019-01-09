$(document).ready(function () {
    var main_table = $('table.sortable');
    var idx_leading = 3; //NOTE add one more count to the real index

    // sortable table
    main_table.tablesort({
        compare: function (a, b) {
            // skip empty cells
            if (a === '') {
                return -1;
            } else if (b === '') {
                return 1;
            }

            // compare
            if (a > b) {
                return 1;
            } else if (a < b) {
                return -1;
            } else {
                return 0;
            }
        }
    });

    // hint on mobile
    var creditors = main_table
        .find('thead th:nth-child(1n+' + idx_leading + ')')
        .map(function (idx, elem) {
            return $(elem).text();
        });

    function prepend_creditor(idx, _) {
        if ($(this).text() === "") {
            return;
        }
        var hint_box = $('<div></div>')
            .addClass('hint')
            .text(creditors[idx]);
        $(this).prepend(hint_box);
    }

    main_table.find('tbody tr').each(function () {
        $(this).children(':nth-child(1n+' + idx_leading + ')')
            .each(prepend_creditor);
    });

    main_table.find('tfoot tr').each(function () {
        $(this).children(':nth-child(1n+' + (idx_leading - 1) + ')')
            .each(prepend_creditor);
    });

});
