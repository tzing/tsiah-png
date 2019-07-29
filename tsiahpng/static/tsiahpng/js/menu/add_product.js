$('#id_category').dropdown();

// https://github.com/Semantic-Org/Semantic-UI/issues/4300
$.fn.form.settings.rules.greaterThan = function (inputValue, validationValue) {
    return inputValue >= validationValue;
}

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
        decimal: {
            identifier: 'price',
            rules: [
                {
                    type: 'decimal',
                    prompt: gettext('Please enter a number.')
                },
                {
                    type: 'greaterThan[0]',
                    prompt: gettext('Please enter a positive price.')
                }
            ]
        },
    }
});
