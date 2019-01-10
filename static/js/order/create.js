$(document).ready(function () {

    $('#select-shop').dropdown();

    $('#select-date').calendar({
        type: 'date',
        today: true,
        formatter: {
            date: function (date) {
                var str = '';
                str += date.getFullYear();
                str += '/';
                str += date.getMonth() + 1;
                str += '/';
                str += date.getDate();
                return str;
            }
        }
    });

    $('form.form').form({
        'on': 'blur',
        fields: {
            shop: {
                identifier: 'shop',
                rules: [{
                    type: 'empty',
                    prompt: gettext('Please specific a shop')
                }]
            },
            date: {
                identifier: 'date',
                rules: [{
                    type: 'empty',
                    prompt: gettext('Date could not be empty')
                }]
            }
        }
    });

});
