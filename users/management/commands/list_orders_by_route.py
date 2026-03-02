from datetime import datetime, time, timezone as dt_timezone
from django.core.management.base import BaseCommand
from farmfills_admin.business import daily_delivery_query

class Command(BaseCommand):
    help = 'Creates daily transacion for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('date', type=str, nargs='?', default=datetime.today().strftime('%Y-%m-%d'))
        parser.add_argument(
            '--route_name',
            type=str,
            required=True,
            help='Filter by route name'
        )

    def handle(self, *args, **options):
        result = daily_delivery_query(options['date'])
        route_filter = options.get('route_name')

        for row in result:
            (_, delivery_name, mobile, _, _, route_name, _, _, _, packets, _) = row
            if route_name == route_filter:
                print(delivery_name, " (", mobile, "): ", packets, " packets")

        
