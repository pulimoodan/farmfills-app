from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from users.models import Staff, Dispatch, Delivery, User, Subscription, ExtraLess, Vacation, UserType
from datetime import datetime, timedelta
from django.utils import timezone
from users.views import get_client_ip, getQuantityOfDate
from delivery.views import getDeliveryList, getGeneratedDeliveryListOfRoute
from delivery.models import DeliveryData
import pytz


# login page
def login(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        return redirect('dispatch_home')
    return render(request, 'dispatch_login.html', {'error':error})


# dispatch page
def dispatch(request):
    error = request.GET.get('error', None)
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        staff = Staff.objects.get(id= user_id, dispatch=True)

        # check if the dispatch boy is early
        early = False
        right_time = timezone.localtime(timezone.now()).replace(hour=2, minute=1, second=0, microsecond=0)
        if right_time > timezone.localtime(timezone.now()):  # early if it's < 2:01 am
            early = True
        
        dispatchData = {}
        if early:
            dispatchData = getDispatchData()
        else:
            dispatchData = getGeneratedDispatchData()
        
        data = None
        try:
            data = Dispatch.objects.get(date=timezone.localtime(timezone.now()).date())
            data.net = int(data.packets + data.packets_variation)
        except:
            pass
        
        return render(request, 'dispatch_home.html', {
            'data':data,
            'dispatchData':dispatchData
            })
    else:
        return redirect('dispatch_login')


# login validation
def login_validation(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            staff = Staff.objects.get(uname=username, password=password, dispatch=True)
            ip = get_client_ip(request)
            Staff.objects.filter(ip=ip).update(ip='')
            staff.ip = ip
            staff.save()
            request.session['farmfills_staff_id'] = staff.id
            return redirect('dispatch_home')
        except:
            return redirect('/dispatch/login?error=Username or password is invalid')


# get dispatch data
def getDispatchData():

    output = {'total':0, 'list':[], 'variation':0, 'net':0}

    delivery_boys = Staff.objects.filter(delivery=True)

    for db in delivery_boys:

        delivery = getDeliveryList(db.route)

        packets_variation = 0
        dispatch_start_time= None 
        dispatch_end_time = None
        try:
            packets_variation = Delivery.objects.get(date=timezone.localtime(timezone.now()).date(), delivery_boy=db).packets_variation
        except:
            pass
        try:
            dispatch_start_time = Delivery.objects.get(date=timezone.localtime(timezone.now()).date(), delivery_boy=db).dispatch_start_time
        except:
            pass
        try:
            dispatch_end_time = Delivery.objects.get(date=timezone.localtime(timezone.now()).date(), delivery_boy=db).dispatch_end_time
        except:
            pass

        if packets_variation is None:
            packets_variation = 0
        else:
            output['variation'] += packets_variation
        
        if not delivery['total']:
            delivery['total'] = 0

        output['list'].append({'delivery_boy':db, 'total': delivery['total'], 'packets_variation':packets_variation, 'dispatch_start_time':dispatch_start_time, 'dispatch_end_time':dispatch_end_time})

        output['total'] += delivery['total']
    
    bulkType = UserType.objects.get(id=8)
    bulkCustomers = User.objects.filter(user_type = bulkType)

    for b in bulkCustomers:

        extraless = ExtraLess.objects.filter(user=b)
        vacations = Vacation.objects.filter(user=b)
        subs = Subscription.objects.filter(user=b)

        in_vacation = False

        thisdate = timezone.localtime(timezone.now()).date()

        for e in extraless:
            if e.start_date <= thisdate and e.end_date >= thisdate :
                output['total'] += int(e.quantity * 2)
                output['list'].append({'type':'bulk', 'user':b, 'total': int(e.quantity * 2)})
                in_vacation = True
        
        if not in_vacation:
            for v in vacations:

                if v.start_date <= thisdate and v.end_date is None :
                    in_vacation = True
                elif v.end_date is not None:
                    if v.start_date <= thisdate and v.end_date >= thisdate:
                        in_vacation = True
        
        if not in_vacation:
            for s in subs:

                if s.start_date <= thisdate and s.end_date is None :
                    packet =  0
                    try:
                        packet = int(getQuantityOfDate(s, timezone.localtime(timezone.now()).date()) * 2)
                    except:
                        pass
                    output['total'] += packet
                    output['list'].append({'type':'bulk', 'user':b, 'total': packet})
                elif s.end_date is not None:
                    if s.start_date <= thisdate and s.end_date >= thisdate:
                        packet =  0
                        try:
                            packet = int(getQuantityOfDate(s, timezone.localtime(timezone.now()).date()) * 2)
                        except:
                            pass
                        output['total'] += packet
                        output['list'].append({'type':'bulk', 'user':b, 'total': packet})

    output['net'] = output['total'] + output['variation']
    return output


# get generated dispatch data
def getGeneratedDispatchData():

    output = {'total':0, 'list':[], 'variation':0, 'net':0}

    delivery_boys = Staff.objects.filter(delivery=True)

    for db in delivery_boys:

        delivery = getGeneratedDeliveryListOfRoute(db.route)

        packets_variation = 0
        dispatch_start_time= None 
        dispatch_end_time = None
        try:
            packets_variation = Delivery.objects.get(date=timezone.localtime(timezone.now()).date(), delivery_boy=db).packets_variation
        except:
            pass
        try:
            dispatch_start_time = Delivery.objects.get(date=timezone.localtime(timezone.now()).date(), delivery_boy=db).dispatch_start_time
        except:
            pass
        try:
            dispatch_end_time = Delivery.objects.get(date=timezone.localtime(timezone.now()).date(), delivery_boy=db).dispatch_end_time
        except:
            pass

        if packets_variation is None:
            packets_variation = 0
        else:
            output['variation'] += packets_variation
        
        if not delivery['total']:
            delivery['total'] = 0

        output['list'].append({'delivery_boy':db, 'total': delivery['total'], 'packets_variation':packets_variation, 'dispatch_start_time':dispatch_start_time, 'dispatch_end_time':dispatch_end_time})

        output['total'] += delivery['total']
    
    bulkType = UserType.objects.get(id=8)
    bulkCustomers = User.objects.filter(user_type = bulkType)

    for b in bulkCustomers:

        try:
            data = DeliveryData.objects.get(date=timezone.localtime(timezone.now()).date(), user=b)
            output['total'] += data.packet
            output['list'].append({'type':'bulk', 'user':b, 'total': data.packet})
        except:
            pass

    output['net'] = output['total'] + output['variation']
    return output


# get bulk customers order by date
def getBulkCusomersOrder(date):
    thisdate = date
    output = {'date': thisdate.strftime("%b %d, %Y"), 'total':0, 'list':[]}

    bulkType = UserType.objects.get(id=8)
    bulkCustomers = User.objects.filter(user_type = bulkType)

    for b in bulkCustomers:

        extraless = ExtraLess.objects.filter(user=b)
        vacations = Vacation.objects.filter(user=b)
        subs = Subscription.objects.filter(user=b)

        in_vacation = False

        for e in extraless:
            if e.start_date <= thisdate and e.end_date >= thisdate :
                output['total'] += int(e.quantity * 2)
                output['list'].append({'type':'bulk', 'user':b, 'total': int(e.quantity * 2)})
                in_vacation = True
        
        if not in_vacation:
            for v in vacations:

                if v.start_date <= thisdate and v.end_date is None :
                    in_vacation = True
                elif v.end_date is not None:
                    if v.start_date <= thisdate and v.end_date >= thisdate:
                        in_vacation = True
        
        if not in_vacation:
            for s in subs:
                
                if s.start_date <= thisdate and s.end_date is None :
                    packet =  0
                    try:
                        packet = int(getQuantityOfDate(s, thisdate) * 2)
                    except:
                        pass
    
                    output['total'] += packet
                    output['list'].append({'type':'bulk', 'user':b, 'total': packet})
                elif s.end_date is not None:
                    if s.start_date <= thisdate and s.end_date >= thisdate:
                        packet =  0
                        try:
                            packet = int(getQuantityOfDate(s, thisdate) * 2)
                        except:
                            pass
                        output['total'] += packet
                        output['list'].append({'type':'bulk', 'user':b, 'total': packet})
    
    return output



# start dispatch
def start_dispatch(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        staff = Staff.objects.get(id= user_id, dispatch=True)
        if request.method == 'POST':
            packets = request.POST.get('packets')
            try:
                dispatch = Dispatch.objects.get(date=timezone.localtime(timezone.now()).date())
                dispatch.start_time = timezone.localtime(timezone.now()).time()
                dispatch.save()
                return redirect('dispatch_home')
            except:
                dispatch = Dispatch(date=timezone.localtime(timezone.now()).date(), start_time=timezone.localtime(timezone.now()).time(), packets=packets, packets_variation=0)
                dispatch.save()
                return redirect('dispatch_home')
        else:
            return redirect('dispatch_home')
    else:
        return redirect('dispatch_login')


# end dispatch
def end_dispatch(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        staff = Staff.objects.get(id= user_id, dispatch=True)
        if request.method == 'POST':
            packets_variation = request.POST.get('packets_variation')
            dispatch = Dispatch.objects.get(date=timezone.localtime(timezone.now()).date())
            dispatch.end_time = timezone.localtime(timezone.now()).time()
            dispatch.packets_variation = int(packets_variation)
            dispatch.save()
            return redirect('dispatch_home')
        else:
            return redirect('dispatch_home')
    else:
        return redirect('dispatch_login')


# update packets variation in delivery
def update_delivery_variation(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        if request.method == 'GET':
            staff_id = request.GET.get('staff_id')
            packets = request.GET.get('packets')
            delivery_boy = Staff.objects.get(id=staff_id)
            packets_variation = request.GET.get('packets_variation')
            try:
                delivery = Delivery.objects.get(delivery_boy=delivery_boy, date=timezone.localtime(timezone.now()).date())
                delivery.packets_variation = packets_variation
                delivery.save()
            except:
                delivery = Delivery(date=timezone.localtime(timezone.now()).date(), delivery_boy=delivery_boy, route=delivery_boy.route, packets=int(packets), packets_variation=int(packets_variation), km=delivery_boy.km)
                delivery.save()
            data = {
                'success': True
            }
            return JsonResponse(data)
        else:
            return redirect('dispatch_home')
    else:
        return redirect('dispatch_login')


# update dispatch start time in delivery
def start_delivery_dispatch(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        if request.method == 'GET':
            staff_id = request.GET.get('staff_id')
            packets = request.GET.get('packets')
            delivery_boy = Staff.objects.get(id=staff_id)
            try:
                delivery = Delivery.objects.get(delivery_boy=delivery_boy, date=timezone.localtime(timezone.now()).date())
                delivery.dispatch_start_time = timezone.localtime(timezone.now()).time()
                delivery.save()
            except:
                delivery = Delivery(date=timezone.localtime(timezone.now()).date(), delivery_boy=delivery_boy, route=delivery_boy.route, packets=int(packets), dispatch_start_time=timezone.localtime(timezone.now()).time(), km=delivery_boy.km)
                delivery.save()
            data = {
                'success': True
            }
            return JsonResponse(data)
        else:
            return redirect('dispatch_home')
    else:
        return redirect('dispatch_login')


# update dispatch end time in delivery
def end_delivery_dispatch(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        if request.method == 'GET':
            staff_id = request.GET.get('staff_id')
            delivery_boy = Staff.objects.get(id=staff_id)
            try:
                delivery = Delivery.objects.get(delivery_boy=delivery_boy, date=timezone.localtime(timezone.now()).date())
                delivery.dispatch_end_time = timezone.localtime(timezone.now()).time()
                delivery.save()
            except:
                delivery = Delivery(date=timezone.localtime(timezone.now()).date(), delivery_boy=delivery_boy, route=delivery_boy.route, packets=int(packets), dispatch_end_time=timezone.localtime(timezone.now()).time(), km=delivery_boy.km)
                delivery.save()
            data = {
                'success': True
            }
            return JsonResponse(data)
        else:
            return redirect('dispatch_home')
    else:
        return redirect('dispatch_login')