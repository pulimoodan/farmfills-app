from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from users.models import Staff, Route, User, Payment
from .models import Collection, HandOver, Expenses
from django.utils import timezone
from datetime import time, timedelta, datetime
from users.views import getEndBalanceOfMonth, last_day_of_month, getPurchaseOfMonth, getPaymentOfMonth
from django.db.models import Q
from django.core import serializers
from farmfills_admin.views import update_balance_of_customer

# get the collection of a month with last day of month
def getCollectionOfMonth(last_day, user):

    output = 0

    first_day = last_day.replace(day=1)
    
    collection = Collection.objects.filter(Q(user=user), Q(date__lt = last_day) | Q(date__contains = last_day.date()), Q(date__gt = first_day) | Q(date__contains = first_day.date())).order_by('-date', '-id')

    for p in collection:

        output += p.amount

    return output

# check if collection of a month exist for a customer with last day of month
def checkCollectionOfMonth(last_day, user):

    output = None

    first_day = last_day.replace(day=1)
    
    collection = Collection.objects.filter(Q(user=user), Q(verified=False), Q(date__lt = last_day) | Q(date__contains = last_day.date()), Q(date__gt = first_day) | Q(date__contains = first_day.date())).order_by('-date', '-id')

    for p in collection:

        output = p

    return output

def login(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        return redirect('cash_collection_home')
    return render(request, 'collection_login.html', {'error':error})


def collection(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        routes = Route.objects.all()
        customers = []
        if route is not None and route != 'all':
            route = Route.objects.get(id=route)
            customers = User.objects.filter(payment_mode='cash', route=route)
        else:
            customers = User.objects.filter(payment_mode='cash')
        data = {'before2month':None, 'before1month':None, 'list':[]}

        last_day1month = timezone.localtime(timezone.now()).replace(day=1)
        last_day1month = last_day1month - timedelta(days=1)
        data['before1month'] = last_day1month.strftime('%B')
        last_day2month = last_day1month.replace(day=1)
        last_day2month = last_day2month - timedelta(days=1)
        data['before2month'] = last_day2month.strftime('%B')

        for c in customers:
            payment2month = getPaymentOfMonth(last_day_of_month(last_day2month), c)
            purchase1month = getPurchaseOfMonth(last_day_of_month(last_day1month), c)
            purchase2month = getPurchaseOfMonth(last_day_of_month(last_day2month), c)
            balance1month = getEndBalanceOfMonth(last_day_of_month(last_day1month), c)
            balance2month = getEndBalanceOfMonth(last_day_of_month(last_day2month), c)

            payment1month = getPaymentOfMonth(last_day_of_month(timezone.localtime(timezone.now())), c)

            balance = float(payment1month) + int(balance1month)
            data['list'].append({'user':c, 'payment1month':payment1month, 'payment2month':payment2month, 'purchase1month':purchase1month, 'purchase2month':purchase2month, 'balance1month':balance1month, 'balance2month':balance2month, 'balance':balance})
        return render(request, 'collection_list.html', {'routes':routes, 'route':route, 'data':data})
    else:
        return redirect('collection_login')


def collection_report(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        routes = Route.objects.all()
        return render(request, 'collection_report.html', {'routes':routes})
    else:
        return redirect('collection_login')


def get_collected_payments(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        uid = request.GET.get('uid', None)
        user = User.objects.get(id=uid)
        start_date = timezone.localtime(timezone.now()).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = last_day_of_month(start_date)
        collections = Collection.objects.filter(user=user, date__range=(start_date, end_date)).order_by('-date', '-id')
        output = {'customer': user.delivery_name, 'list': []}
        for c in collections:
            output['list'].append({'id': c.id, 'amount': c.amount, 'date': timezone.localtime(c.date).strftime('%b %d, %Y')})
        return JsonResponse(output, safe=False)
    else:
        return redirect('collection_login')


def collection_hand_over(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        staffs = Staff.objects.all()
        return render(request, 'collection_hand_over.html', {'staffs':staffs})
    else:
        return redirect('collection_login')


def collection_expenses(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        return render(request, 'collection_expenses.html')
    else:
        return redirect('collection_login')


def collection_report_generator(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        report = []

        from_date = request.GET.get('from_date')
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
        first_day = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = request.GET.get('to_date')
        if to_date != '':
            to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
            last_day = to_date.replace(hour=0, minute=0, second=0, microsecond=0)
            report = Collection.objects.filter(date__range=(first_day, last_day)).order_by('-date', '-id')
        else:
            report = Collection.objects.filter(Q(date__gt = first_day) | Q(date = first_day)).order_by('-date', '-id')

        route = request.GET.get('route')
        if route != 'all':
            route = Route.objects.get(id=route)
            report = report.filter(user__route=route)
        
        verified = request.GET.get('verified')
        if verified != 'all':
            report = report.filter(verified=verified)

        output = {'list': [], 'total': 0}

        for r in report:
            output['list'].append({'customer': r.user.delivery_name, 'amount': r.amount, 'date': timezone.localtime(r.date).strftime('%b %d, %Y')})
            output['total'] += r.amount

        # report = serializers.serialize('json', report)
        return JsonResponse(output, safe=False)
    else:
        return redirect('collection_login')


def handover_report_generator(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        report = []

        month = request.GET.get('month')
        first_day = timezone.make_aware(datetime.strptime((month + '-1'), '%Y-%m-1')).replace(hour=0, minute=0, second=0, microsecond=0)
        last_day = last_day_of_month(first_day).replace(hour=0, minute=0, second=0, microsecond=0)
        report = HandOver.objects.filter(date__range=(first_day, last_day)).order_by('-date', '-id')

        to = request.GET.get('to')
        if to != 'all':
            to = Staff.objects.get(id=to)
            report = report.filter(to=to)

        output = {'list': [], 'handover_total': 0, 'collection_total':0, 'balance':0}

        for r in report:
            output['list'].append({'id':r.id, 'date': timezone.localtime(r.date).strftime('%b %d, %Y'), 'to': r.to.name, 'amount': r.amount})
            output['handover_total'] += r.amount
        
        collection = Collection.objects.filter(date__range=(first_day, last_day)).order_by('-date', '-id')
        for c in collection:
            output['collection_total'] += c.amount
        
        output['balance'] += output['collection_total'] - output['handover_total']

        # report = serializers.serialize('json', report)
        return JsonResponse(output, safe=False)
    else:
        return redirect('collection_login')


def expenses_report_generator(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    route = request.GET.get('route', None)
    if Staff.objects.filter(id=user_id, cash_collection=True).exists():
        report = []

        month = request.GET.get('month')
        first_day = timezone.make_aware(datetime.strptime((month + '-1'), '%Y-%m-1')).replace(hour=0, minute=0, second=0, microsecond=0)
        last_day = last_day_of_month(first_day).replace(hour=0, minute=0, second=0, microsecond=0)
        report = Expenses.objects.filter(date__range=(first_day, last_day)).order_by('-date', '-id')

        output = {'list': [], 'expenses_total':0, 'handover_total': 0, 'collection_total':0, 'balance':0}

        for r in report:
            output['list'].append({'id':r.id, 'date': timezone.localtime(r.date).strftime('%b %d, %Y'), 'note': r.note, 'amount': r.amount})
            output['expenses_total'] += r.amount
        
        collection = Collection.objects.filter(date__range=(first_day, last_day)).order_by('-date', '-id')
        for c in collection:
            output['collection_total'] += c.amount

        handover = HandOver.objects.filter(date__range=(first_day, last_day)).order_by('-date', '-id')
        for h in handover:
            output['handover_total'] += h.amount
        
        output['balance'] += output['collection_total'] - output['handover_total'] - output['expenses_total']

        # report = serializers.serialize('json', report)
        return JsonResponse(output, safe=False)
    else:
        return redirect('collection_login')


# validate login
def login_validation(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        password = request.POST.get('password')
        if Staff.objects.filter(uname=uname, password=password, cash_collection=True).exists():
            user = Staff.objects.get(uname=uname, password=password, cash_collection=True)
            request.session['farmfills_staff_id'] = user.id
            return redirect('cash_collection_home')
        else:
            return redirect('/collection/login?error=1')
    return redirect('collection_login')


def add_collection(request):
    if request.method == 'GET':
        uid = request.GET['uid']
        amount = request.GET['amount']
        date = request.GET['date']
        date = timezone.make_aware(datetime.strptime(date, '%Y-%m-%d'))
        user = User.objects.get(id=uid)

        payment = Payment(user=user, date=date, amount=amount, mode="cash", description="Collected by Hafeel", paid=True, balance=0)
        payment.save()
        update_balance_of_customer(payment.user)

        collection = Collection(user=user, amount= amount, date=date, payment=payment)
        collection.save()

        last_day1month = timezone.localtime(timezone.now()).replace(day=1)
        last_day1month = last_day1month - timedelta(days=1)
        balance1month = getEndBalanceOfMonth(last_day_of_month(last_day1month), user)
        payment1month = getPaymentOfMonth(last_day_of_month(timezone.localtime(timezone.now())), user)
        balance = float(payment1month) + int(balance1month)

        output = {'payment':payment1month, 'balance':balance}

        return JsonResponse(output, safe=False)
    else:
        return HttpResponse("Request method is not a GET")


def add_handover(request):
    if request.method == 'GET':
        to = request.GET['to']
        amount = request.GET['amount']
        date = request.GET['date']
        date = timezone.make_aware(datetime.strptime(date, '%Y-%m-%d'))
        to = Staff.objects.get(id=to)
        handover = HandOver(date=date, to=to, amount= amount)
        handover.save()
        return HttpResponse("Success!")
    else:
        return HttpResponse("Request method is not a GET")


def add_expenses(request):
    if request.method == 'GET':
        note = request.GET['note']
        amount = request.GET['amount']
        date = request.GET['date']
        date = timezone.make_aware(datetime.strptime(date, '%Y-%m-%d'))
        expenses = Expenses(date=date, note=note, amount= amount)
        expenses.save()
        return HttpResponse("Success!")
    else:
        return HttpResponse("Request method is not a GET")


def delete_handover(request):
    if request.method == 'GET':
        uid = request.GET['id']
        handover = HandOver.objects.get(id=uid)
        handover.delete()
        return HttpResponse("Success!")
    else:
        return HttpResponse("Request method is not a GET")


def delete_expenses(request):
    if request.method == 'GET':
        uid = request.GET['id']
        expenses = Expenses.objects.get(id=uid)
        expenses.delete()
        return HttpResponse("Success!")
    else:
        return HttpResponse("Request method is not a GET")


def delete_collection(request):
    if request.method == 'GET':
        uid = request.GET['id']
        collection = Collection.objects.get(id=uid)
        payment = Payment(id=collection.payment.id)
        payment.delete()

        last_day1month = timezone.localtime(timezone.now()).replace(day=1)
        last_day1month = last_day1month - timedelta(days=1)
        balance1month = getEndBalanceOfMonth(last_day_of_month(last_day1month), collection.user)
        payment1month = getPaymentOfMonth(last_day_of_month(timezone.localtime(timezone.now())), collection.user)
        balance = float(payment1month) + int(balance1month)

        output = {'payment':payment1month, 'balance':balance}

        return JsonResponse(output, safe=False)
    else:
        return HttpResponse("Request method is not a GET")