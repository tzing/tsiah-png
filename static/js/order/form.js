var form = $('form.form').each(function (idx, item) {
    if ($(item).data('registered')) {
        return;
    }

    $(item).data('registered', true);

    $(item).form({
        'on': 'blur',
        fields: {
            user: {
                identifier: 'user',
                rules: [{
                    type: 'empty',
                    prompt: gettext('Please specific a user')
                }]
            },
            tickets: {
                identifier: 'tickets',
                rules: [{
                    type: 'empty',
                    prompt: gettext('At least one item should be selected')
                }]
            }
        },
        onSuccess: function (e) {
            $('.submit.button').addClass('disable');
        }
    });

    $(item).find('.user.selection').dropdown({
        apiSettings: {
            url: $(this).data('url'),
            data: {
                sui: true,
            }
        },

        filterRemoteData: true,
        fullTextSearch: true,
        match: 'text',
    });

    $(item).find('.product.selection').dropdown({
        fullTextSearch: true,
        match: 'text',

        // on add: create row to order food
        onAdd: function (add_id, _, add_obj) {
            var id = add_id;
            var name = add_obj.data('name');
            var price = add_obj.data('price');

            // remove 'no ticket' row
            $(this).parents('form').find('tr.hint').remove();

            // add row
            var row = $('<tr></tr>').data('id', id);
            $(this).parents('form').find('tbody').append(row);

            // item name
            row.append($('<td></td>').append(name));

            // quantity
            row.append($('<td></td>').append(
                $('<input>')
                    .attr('type', 'number')
                    .attr('name', 'quantity-' + id)
                    .attr('value', 1)
                    .attr('min', 0)
                    .change(function () {
                        $('input[name="price-' + id + '"]').val($(this).val() * price);
                    })
            ));

            // price
            row.append($('<td></td>').append(
                $('<input>')
                    .attr('type', 'number')
                    .attr('name', 'price-' + id)
                    .attr('min', 0)
                    .attr('step', 5)
                    .attr('value', price)
            ));

            // note
            var allow_user_change = add_obj.data('allow-change');
            if (allow_user_change) {
                row.append($('<td></td>').append(
                    $('<input>')
                        .attr('name', 'note-' + id)
                        .attr('type', 'text')
                        .attr('placeholder', gettext('Add something to ') + name)
                ));
            } else {
                row.append($('<td></td>'));
            }

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
        }

    }); // ./$('.product.selection').dropdown()

});
