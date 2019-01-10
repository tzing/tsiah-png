$(document).ready(function () {
    // add scroll animate to quick start menu
    $('.quick.menu a.item').click(function () {
        $('html, body').animate({
            scrollTop: $($(this).attr('href')).offset().top - 88
        }, 400);
        return false;
    });
});
