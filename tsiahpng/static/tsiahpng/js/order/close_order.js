$('.ui.closing.order.modal').modal({
    onApprove: function () {
        var form = $('.closing.order.form');
        if (!form.form('is valid')) {
            form.form('validate form');
            return false;
        } else {
            form.form('submit');
        }
    }
});

$('#close_btn').click(function () {
    $('.ui.modal').modal('show');
});
