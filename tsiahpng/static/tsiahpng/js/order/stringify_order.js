$('#build_text').click(function () {
    $('.summary.text.segment').slideToggle();
});

$('#template_select').dropdown({
    onChange: function (id) {
        // disable form
        var dropdown = $(this);
        var form = $(this).parents('.form');
        form.find('.loader').addClass('active');
        form.find('textarea').attr('disabled', 1);

        dropdown.addClass('disabled');

        //- submit query
        $.get(form.data('url'), {
            template: id
        }).always(function () {
            form.find('.loader').removeClass('active');
            form.find('textarea').removeAttr('disabled');
            dropdown.removeClass('disabled');

        }).done(function (data) {
            form.find('textarea').val(data.text);
        }).fail(function (resp) {
            console.log('Failed to fetch summary.')
            console.log('response status code: ' + resp.status);
            if (resp.status !== 0) {
                console.log('response context:')
                console.log(resp);
            }
        });
    }
});

$('#cpy_summary').click(function () {
    var el = $(this).parents('.form').find('textarea').get(0);
    console.log(el);

    var range = document.createRange();
    range.selectNodeContents(el);

    var selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);

    el.setSelectionRange(0, 999999);
    document.execCommand('copy');

    $(this).text(gettext('Copied!')).addClass('active');
    setTimeout(function () {
        $('#cpy_summary').text(gettext('Copy')).removeClass('active')
    }, 1500);
});
