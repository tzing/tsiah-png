/**
 *  Add hint text for mobile, since table is not reshaped on mobile view and
 *  is hard to read the header
 */
function create_mobile_hint() {
    var table = $('table.sortable');
    var idx_leading = 3; //NOTE add one more count to the real index

    // get header text
    var creditors = table
        .find('thead th:nth-child(1n+' + idx_leading + ')')
        .map(function (idx, elem) {
            return $(elem).text();
        });

    // function to append hint text for each cell
    function prepend_creditor(idx, _) {
        if ($(this).text() === "") {
            return;
        }
        var hint_box = $('<div></div>')
            .addClass('hint')
            .text(creditors[idx]);
        $(this).prepend(hint_box);
    }

    // add hint text to table body
    table.find('tbody tr').each(function () {
        $(this).children(':nth-child(1n+' + idx_leading + ')')
            .each(prepend_creditor);
    });

    // add hint text in footer, except total
    table.find('tfoot tr')
        .first()
        .children(':nth-child(1n+' + (idx_leading - 1) + ')')
        .not('.total')
        .each(prepend_creditor);

    // add 'total' hint text in footer
    table.find('tfoot th.total').prepend(
        $('<div></div>').addClass('hint').text(gettext('Total'))
    )

}

$(document).ready(function () {
    // sortable table
    $('table.sortable').tablesort({
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
    create_mobile_hint();
});
