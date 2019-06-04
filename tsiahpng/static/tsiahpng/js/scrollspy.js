'use strict';

$('.spy.segment').visibility({
    once: false,
    onOnScreen: function () {
        var id = $(this).children('h4').attr('id');
        $('.ui.menu').find('a.item[href="#' + id + '"]').addClass('active');
    },
    onOffScreen: function () {
        var id = $(this).children('h4').attr('id');
        $('.ui.menu').find('a.item[href="#' + id + '"]').removeClass('active');
    }
});
