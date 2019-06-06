'use strict';

$('.ui.right.rail .secondary.vertical.menu').sticky({
    context: '#full-list',
    offset: 80
});

$('.secondary.vertical.menu .item').click(function () {
    var target = $(this).attr('href');
    var top = $(target).offset().top - 80;
    window.scrollTo({
        top: top,
        behavior: "smooth"
    });
    return false;
});
