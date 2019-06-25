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
        url: $('.account .dropdown').data('api')
    },
});

$('input.price').change(function () { $(this).refreshSubtotal(); });

$('form .account').refreshSubtotal();
