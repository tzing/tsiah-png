$('.ui.closing.order.modal').modal({
    onApprove: function () {
        $('.closing.order.form').form('submit');
    }
});

$('#close_btn').click(function () {
    $('.ui.modal').modal('show');
});
