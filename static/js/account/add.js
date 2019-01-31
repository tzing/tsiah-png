function refresh_balance() {
    var sum_balances = 0;
    $(this).parents('form').find('input[type="number"]').each(function () {
        sum_balances += parseInt($(this).val());
    });
    $('#total-balance').text(sum_balances.toLocaleString('en'));
}

$(document).ready(function () {
    $('form.form').form({
        'on': 'blur',
        fields: {
            event: {
                identifier: 'title',
                rules: [{
                    type: 'empty',
                    prompt: gettext('Please name the event')
                }]
            },
            user: {
                identifier: 'user',
                rules: [{
                    type: 'empty',
                    prompt: gettext('Please specific a user')
                }]
            }
        },
        onSuccess: function (e) {
            $('.submit.button').addClass('disable');
        }
    });

    $('#select-user').dropdown({
        apiSettings: {
            url: user_api_url,
            data: {
                sui: true
            }
        },

        filterRemoteData: true,
        fullTextSearch: true,
        match: 'text',

        // on add: create row to order food
        onAdd: function (add_id, _, add_obj) {
            var id = add_id;
            var name = add_obj.text();

            // remove 'no user' row
            $(this).parents('form').find('tr.hint').hide();

            // add row
            var row = $('<tr></tr>').data('id', id);
            $(this).parents('form').find('tbody').append(row);

            // item name
            row.append($('<td></td>').append(name));

            // change in balance
            row.append($('<td></td>').append(
                $('<input>')
                    .attr('type', 'number')
                    .attr('name', 'balance-' + id)
                    .attr('value', 0)
                    .attr('step', 10)
                    .change(refresh_balance)
            ));

        },

        // on remove: remove row
        onRemove: function (rm_id, _, _) {
            var ticket_row = $(this).parents('form').find('tbody tr').filter(function () {
                if ($(this).data('id') === rm_id) { return this; }
            });
            if (ticket_row.length === 0) {
                return;
            }
            ticket_row.get(-1).remove();
            refresh_balance();
        }
    });

});
