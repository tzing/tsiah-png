function smooth_scroll() {
    var target = $(this).attr('href');
    var top = $(target).offset().top - 80;
    window.scrollTo({
        top: top,
        behavior: "smooth"
    });
    return false;
}

$('.quick.secondary.vertical.menu .item').click(smooth_scroll);
$('a[href="#recent_order"]').click(smooth_scroll);
