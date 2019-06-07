$('.ui.selection.dropdown').dropdown();

$('.ui.calendar').calendar({
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

$('.form').form({
    on: 'blur',
    fields: {
        dropdown: {
            identifier: 'shop',
            rules: [
                {
                    type: 'empty',
                    prompt: gettext('Please select ordered shop.')
                },
            ]
        },
        date: {
            identifier: 'date',
            rules: [
                {
                    type: 'regExp',
                    value: /\d{4}\/[01]?\d\/[0-3]?\d/,
                    prompt: gettext('Please pick a valid date.')
                }
            ]
        },
    }
});
