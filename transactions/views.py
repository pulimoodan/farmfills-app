from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import DPurchase, DPayment, DExtra, DRefund
from users.models import Staff, User
from django.utils import timezone
from datetime import time, timedelta, datetime
import pytz
from users.views import getEndBalanceOfMonth, last_day_of_month, getPurchaseOfMonth, getPaymentOfMonth

# Create your views here.
def home(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        data = User.objects.all().order_by('id')
        return render(request, 'transactions_home.html', {'data':data})
    else:
        return redirect('admin_login')


# get transactions bill of each customer
def get_transactions_bill(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user_id = request.GET.get('user_id')
        user = User.objects.get(id=user_id)
        payments = DPayment.objects.filter(user=user)
        purchases = DPurchase.objects.filter(user=user)
        refunds = DRefund.objects.filter(user=user)
        extras = DExtra.objects.filter(user=user)
        data = generateBillDataFollowUp(payments, purchases, refunds, extras, user)
        return JsonResponse(data, safe=False)
    else:
        return redirect('admin_login')

# generate bill data of last 12 month
def generateBillDataFollowUp(payments, purchases, refunds, extras, user):

    month = int(timezone.localtime(timezone.now()).date().strftime('%m'))
    year = int(timezone.localtime(timezone.now()).date().strftime('%Y'))

    output = []

    for i in range(20):
        
        # decreasing 1 month in each loop
        if i != 0:
            month -= 1
            if month == 0:
                year -= 1
                month = 12

        data = {
            'date': datetime(year, month, 1, tzinfo=pytz.UTC).strftime('%Y %b'), 
            'payment':0, 
            'purchase':0, 
            'balance':0, 
        }
        
        last_day = last_day_of_month(datetime(year, month, 1, tzinfo=pytz.UTC))

        data['balance'] = getEndBalanceOfMonth(last_day, user)

        exist = False

        for p in payments:
            if int(p.date.date().strftime('%Y')) == year and int(p.date.date().strftime('%m')) == month:
                data['payment'] += p.amount
                exist = True
        
        for p in purchases:
            if int(p.date.date().strftime('%Y')) == year and int(p.date.date().strftime('%m')) == month:
                data['purchase'] += p.amount
                exist = True

        for e in extras:
            if int(e.date.date().strftime('%Y')) == year and int(e.date.date().strftime('%m')) == month:
                exist = True
                data['purchase'] += e.amount
        
        for r in refunds:
            if int(r.date.date().strftime('%Y')) == year and int(r.date.date().strftime('%m')) == month:
                data['purchase'] -= r.amount
                exist = True

        if exist:
            output.append(data)

    return output
