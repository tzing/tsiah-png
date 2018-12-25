$(document).ready(function () {
    $(window).resize(function () {
        if ($(window).width() < 768) {
            $('#navbar .right.menu').hide();
        } else {
            $('#navbar .right.menu').css('display', 'flex');
        }
    });

    $('#navbar .right.dropdown.item').click(function () {
        $('#navbar .right.menu').slideToggle();
    });
});
