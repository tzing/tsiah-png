$(document).ready(function () {
    $('#select-category').dropdown();

    $('form.form').form({
        'on': 'blur',
        fields: {
            category: {
                identifier: 'category',
                rules: [{
                    type: 'empty',
                    prompt: gettext('Please select a category')
                }]
            },
            name: {
                identifier: 'name',
                rules: [{
                    type: 'regExp[/\\S/]',
                    prompt: gettext('Item name could not be empty')
                }]
            }
        }
    });
});
