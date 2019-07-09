$('.ui.toggle.checkbox').checkbox({
    onChecked: function () {
        var form = $(this).parents('form');
        var pane = form.find('.account');
        pane.slideDown();

        form.form('add rule', 'passbook', {
            rules: [{
                type: 'empty',
                prompt: gettext('Please select a passbook.')
            }]
        });
    },
    onUnchecked: function () {
        var form = $(this).parents('form');
        var pane = form.find('.account');
        pane.slideUp();

        form.form('remove rule', 'passbook');
    }
});

$('.account .dropdown').dropdown({
    apiSettings: {
        url: $('.account .dropdown').data('api'),

        onResponse: function (response) {
            if (typeof twemoji === 'undefined') {
                return response;
            }

            var revised_response = { success: response.success, results: [] }
            response.results.forEach(function (element) {
                revised_response.results.push({
                    name: twemoji.parse(element.name),
                    value: element.value
                })
            });

            return revised_response;
        }
    },
});

$('input.price').change(function () { $(this).refreshSubtotal(); });

$('form .account').refreshSubtotal();
