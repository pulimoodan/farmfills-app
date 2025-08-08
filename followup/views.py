from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from users.models import Staff, Route, User
from django.utils import timezone
from datetime import time, timedelta, datetime
from users.models import FollowUp, Payment, Purchase, Extra, Refund, User
from users.views import getEndBalanceOfMonth, last_day_of_month
import pytz


# login
def login(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, follow_up=True).exists():
        return redirect('followup_home')
    return render(request, 'followup_login.html', {'error':error})


# home
def followup(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, follow_up=True).exists():
        followup = FollowUp.objects.all().order_by('-id')
        followup = list(followup.values())
        for i in range(len(followup)):
            last_day = timezone.localtime(timezone.now()).replace(day=1)
            last_day = last_day - timedelta(days=1)
            user = User.objects.get(id=followup[i]['user_id'])
            followup[i]['last_balance'] = getEndBalanceOfMonth(last_day, user)
            followup[i]['user_id'] = user.id
            followup[i]['user_name'] = user.name + ' ' + user.delivery_name
            followup[i]['user_mobile'] = user.mobile
            if followup[i]['note'] is None:
                followup[i]['note'] = ''  
            if followup[i]['last_date'] is None:
                followup[i]['last_date'] = ''
            else:
                followup[i]['last_date'] = followup[i]['last_date'].strftime('%d %b, %Y')  
        return render(request, 'followup_home.html', {'followup':followup})
    else:
        return redirect('followup_login')


# change next followup date
def change_next_followup_date(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, follow_up=True).exists():
        followup_id = request.GET.get('followup_id')
        date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').replace(tzinfo=pytz.UTC).date()
        followup = FollowUp.objects.get(id=followup_id)
        followup.next_date = date
        followup.save()
        return JsonResponse({'success': True})
    else:
        return redirect('followup_login')


# change last followup date
def change_last_followup_date(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, follow_up=True).exists():
        followup_id = request.GET.get('followup_id')
        date = timezone.localtime(timezone.now()).date()
        followup = FollowUp.objects.get(id=followup_id)
        followup.last_date = date
        date = date + timedelta(days=5)
        followup.next_date = date
        followup.save()
        return JsonResponse({'success': True})
    else:
        return redirect('followup_login')


# change followup note
def change_followup_note(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, follow_up=True).exists():
        followup_id = request.GET.get('followup_id')
        note = request.GET.get('note')
        followup = FollowUp.objects.get(id=followup_id)
        followup.note = note
        followup.save()
        return JsonResponse({'success': True})
    else:
        return redirect('followup_login')


# get followup bill of each customer
def get_followup_bill(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, follow_up=True).exists():
        user_id = request.GET.get('user_id')
        user = User.objects.get(id=user_id)
        payments = Payment.objects.filter(user=user)
        purchases = Purchase.objects.filter(user=user)
        refunds = Refund.objects.filter(user=user)
        extras = Extra.objects.filter(user=user)
        data = generateBillDataFollowUp(payments, purchases, refunds, extras, user)
        return JsonResponse(data, safe=False)
    else:
        return redirect('followup_login')


# validate login
def login_validation(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        password = request.POST.get('password')
        if Staff.objects.filter(uname=uname, password=password, follow_up=True).exists():
            user = Staff.objects.get(uname=uname, password=password, follow_up=True)
            request.session['farmfills_staff_id'] = user.id
            return redirect('followup_home')
        else:
            return redirect('/followup/login?error=1')
    return redirect('followup_login')


# generate bill data of last 12 month
def generateBillDataFollowUp(payments, purchases, refunds, extras, user):

    month = int(timezone.localtime(timezone.now()).date().strftime('%m'))
    year = int(timezone.localtime(timezone.now()).date().strftime('%Y'))

    output = []

    for i in range(13):
        
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
