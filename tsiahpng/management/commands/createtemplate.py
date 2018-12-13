from django.core.management.base import BaseCommand, CommandError

from tsiahpng import models

TEMPLATE_DATE = "{{{{ order.order_date |date:'{date_format}' }}}}"
TEMPLATE_ITEMS = """{{% for ticket in tickets %}}{ticket_format}{{% if not forloop.last %}}{delimiter}{{% endif %}}{{% endfor %}}"""


class Command(BaseCommand):
    help = 'Create a template'

    def add_arguments(self, parser):
        parser.add_argument('name', help='A readable name to the template')

        # format
        group = parser.add_argument_group('format')
        group.add_argument(
            '--date-position',
            default='before',
            choices=['before', 'after', 'none'],
            help='Position to add the order date: before or after the items')
        group.add_argument(
            '--date-format',
            default='m/d',
            help=
            'The format for the order date, use django format (https://docs.djangoproject.com/en/2.1/ref/templates/builtins/#date)'
        )
        group.add_argument(
            '-d',
            '--delimiter',
            default='\n',
            help="The delimiter for the continued tickets (default '\\n')")
        group.add_argument(
            '--count-one',
            action='store_true',
            help='Show ordered quantity when it only takes one (default false)'
        )

    def handle(self, *args, **options):
        template = TEMPLATE_ITEMS.format(
            ticket_format='{{ ticket }}'
            if options['count_one'] else '{{ ticket | no_qty }}',
            delimiter=options['delimiter'],
        )

        date = TEMPLATE_DATE.format(date_format=options['date_format'])
        if options['date_position'] == 'before':
            template = date + template
        elif options['date_position'] == 'after':
            template += date

        try:
            models.SummaryTemplate.objects.create(
                alias=options['name'],
                template=template,
            )

            self.stdout.write(
                self.style.SUCCESS('Success create the template:'))
            self.stdout.write(template)

        except:
            self.stdout.write(self.style.ERROR('Fail to create the template'))
