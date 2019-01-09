/**
 * load data from server and fill the table
 */
function load_account_data() {
    // prevent duplicated query
    var table = $('#user-balance');
    if (table.data('loaded')) {
        return;
    }

    // set dimmer
    table.parents('form').addClass('loading');

    // fire query
    $.when(
        $.get(user_query_url, { all: true }),
        $.get(order_query_url, { subtotal: true })
    ).done(function (d1, d2) {
        var username = d1[0];
        var order = d2[0];

        var tbody = $('#user-balance tbody');

        // check if any value returned
        if (Object.keys(order.subtotal).length > 0) {
            tbody.find('tr.hint').remove();
        }

        // hidden field
        $('input[name="user"]').val(Object.keys(order.subtotal).join(','));

        // create rows
        for (var id in order.subtotal) {
            var row = $('<tr></tr>');
            tbody.append(row);

            // username
            row.append($('<td></td>').text(username[id]));

            // change in balance
            row.append($('<td></td>').append(
                $('<input>')
                    .attr('type', 'number')
                    .attr('name', 'balance-' + id)
                    .attr('value', -order.subtotal[id])
                    .attr('step', 5)
                    .change(refresh_balance)
            ));
        }

        // refresh total balance
        table.find('input[type="number"]').change();

        // finalize
        table.data('loaded', true);
        table.parents('form').removeClass('loading');
    });

} // ./load_account_data

/**
 * refresh total balance number
 */
function refresh_balance() {
    var sum_balances = 0;
    $(this).parents('table').find('input[type="number"]').each(function () {
        sum_balances += parseInt($(this).val());
    });
    $('#total-balance').text(sum_balances.toLocaleString('en'));
}

$(document).ready(function () {
    /**
     *  query passbook data from server
     */
    $('#select-passbook').dropdown({
        apiSettings: {
            url: passbook_query_url,
            data: {
                sui: true,
            },
        },

        filterRemoteData: true,
        fullTextSearch: true,
        match: 'text',
    });

    /**
     *  load data when the 'put it on bill' option is checked
     */
    $('#switch-account').checkbox({
        onChecked: function () {
            load_account_data()
            $('#account-panel').slideDown();
        },

        onUnchecked: function () {
            $('#account-panel').slideUp();
        },
    });

    /**
     *  form validation
     */
    $('form.form').form({
        on: 'blur',
        fields: {
            passbook: {
                identifier: 'passbook',
                rules: [{
                    type: 'empty',
                    prompt: gettext('Please specify the accounting book')
                }]
            },
        },
    });

});
