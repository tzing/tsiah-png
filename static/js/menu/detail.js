$(document).ready(function () {

    $('#category-menu').sticky({
        offset: 40,
    });

    $('.second.menu a.item').click(function () {
        $('html, body').animate({
            scrollTop: $($(this).attr('href')).offset().top - 88
        }, 400);
        return false;
    });

});
