from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from users.models import Staff, Route, User, Area
from django.utils import timezone
from datetime import time, timedelta
from delivery.views import getDeliveryListByDate, getDeliveryListOfAreaByDate, getDeliveryList, getGeneratedOrderOfAreaByDate
from users.views import getEndBalanceOfMonth, last_day_of_month, getPurchaseOfMonth, getPaymentOfMonth


# login
def login(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, vendor=True).exists():
        return redirect('vendor_today')
    return render(request, 'vendor_login.html', {'error':error})


# today
def today(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, vendor=True).exists():
        
        result = get_total_of_the_day(timezone.localtime(timezone.now()).date())
        return render(request, 'vendor_today.html', {'result': result})
    else:
        return redirect('vendor_login')


# tomorrow
def tomorrow(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, vendor=True).exists():
        result = get_total_of_the_day(timezone.localtime(timezone.now()).date() + timedelta(days=1))
        return render(request, 'vendor_tomorrow.html', {'result': result})
    else:
        return redirect('vendor_login')


# validate login
def login_validation(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        password = request.POST.get('password')
        if Staff.objects.filter(uname=uname, password=password, vendor=True).exists():
            user = Staff.objects.get(uname=uname, password=password, vendor=True)
            request.session['farmfills_staff_id'] = user.id
            return redirect('vendor_today')
        else:
            return redirect('/vendor/login?error=1')
    return redirect('vendor_login')


# get total packets of a day
def get_total_of_the_day(date):
    output = {'total':0, 'areas':[]}

    # check if the vendor is early
    early = False
    right_time = timezone.localtime(timezone.now()).replace(hour=2, minute=1, second=0, microsecond=0)
    if right_time > timezone.localtime(timezone.now()):  # early if it's < 2:01 am
        early = True

    areas = Area.objects.all().exclude(id=1)
    if date == timezone.localtime(timezone.now()).date() and not early:
        for a in areas:
            delivery = getGeneratedOrderOfAreaByDate(a, date.strftime('%Y-%m-%d'))
            output['areas'].append({'name': a.name, 'total': delivery})
            output['total'] += delivery
    else:
        for a in areas:
            delivery = getDeliveryListOfAreaByDate(a, date.strftime('%Y-%m-%d'))
            output['areas'].append({'name': a.name, 'total': delivery['total']})
            output['total'] += delivery['total']

    return output