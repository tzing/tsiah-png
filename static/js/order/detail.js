$(document).ready(function () {
    $('#build-summary-templates').click(function () {
        $('#summary-templates').slideToggle();
    });

    $('#select-template').dropdown({
        onChange: function (id) {
            // disable form
            $('#select-template').addClass('disabled');
            $('#summary-string').attr('disabled', 1);

            $('#summary-templates-loader').addClass('active');

            // submit query
            $.get(template_query_url + '?template=' + id, function (data) {
                $('#summary-string').val(data);

                $('#select-template').removeClass('disabled');
                $('#summary-string').removeAttr('disabled');
                $('#summary-templates-loader').removeClass('active');
            });
        }
    });

    $('#copy-button').click(function () {
        var el = $('#summary-string')[0];

        var range = document.createRange();
        range.selectNodeContents(el);

        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);

        el.setSelectionRange(0, 999999);
        document.execCommand('copy');

        $(this).text(gettext('Copied!')).addClass('active');
        setTimeout(function () {
            $('#copy-button').text(gettext('Copy')).removeClass('active')
        }, 1500);
    });
});
