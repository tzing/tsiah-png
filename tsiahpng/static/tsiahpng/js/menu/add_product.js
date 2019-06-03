$('#id_category').dropdown();

$('.form').form({
    on: 'blur',
    fields: {
        dropdown: {
            identifier: 'category',
            rules: [
                {
                    type: 'empty',
                    prompt: gettext('Please select a category.')
                },
            ]
        },
        empty: {
            identifier: 'name',
            rules: [
                {
                    type: 'empty',
                    prompt: gettext('Please enter product name.')
                }
            ]
        },
        integer: {
            identifier: 'price',
            rules: [
                {
                    type: 'integer[1..]',
                    prompt: gettext('Please enter a positive integer price.')
                }
            ]
        },
    }
});
