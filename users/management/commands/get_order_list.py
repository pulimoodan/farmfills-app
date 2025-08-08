import pytz
from datetime import datetime
from dispatch.views import getDispatchData
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates daily transacion for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('date', type=str)

    def handle(self, *args, **options):

        data = []
        
        try:
            date = datetime.strptime(options['date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC).date()
            output = getDispatchData(date)

            data.append(['Date: ', date.strftime('%d %b, %Y')])
            data.append(['------------', '------------'])


            for item in output['list']:
                data.append([item['delivery_boy'], str(item['total'])])

            
            data.append(['------------', '------------'])
            data.append(['Total', str(output['total'])])

            for line in data:
                print(f"{line[0] : <50}{line[1] : ^50}")
        except Exception as e:
            print('==============     Error    ============')
            print(e)

        
