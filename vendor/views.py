from users.models import Staff
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from farmfills_admin.business import daily_delivery_query


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
    if Staff.objects.filter(id=user_id, vendor=True).exists():
        result = get_total_of_the_day()
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
    if Staff.objects.filter(id=user_id, vendor=True).exists():
        tomorrow = (timezone.localdate() + timedelta(days=1)).strftime('%Y-%m-%d')
        result = get_total_of_the_day(tomorrow)
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
def get_total_of_the_day(date = None):
    output = {'total':0, 'areas':[]}
    result = daily_delivery_query(date)

    areas = {}
    for row in result:
        (_, delivery_name, user_type_id, _, _, _, area_name, _, total_quantity, _) = row
        key = area_name
        if user_type_id == 8:
            key = delivery_name
        areas[key] = areas.get(key, 0) + int(total_quantity)
        output['total'] += int(total_quantity)

    output['areas'] = [{'name': key, 'total': value} for key, value in areas.items()]

    return output
