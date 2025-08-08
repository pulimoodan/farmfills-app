from django.utils import timezone
from users.views import get_client_ip
from users.models import Staff, Dispatch
from django.shortcuts import render, redirect
from farmfills_admin.business import daily_delivery_query


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
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        
        dispatchData = getDispatchData()
        
        data = None
        try:
            data = Dispatch.objects.get(date=timezone.localdate())
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
def getDispatchData(date = None):
    output = {'total':0, 'list':[], 'variation':0, 'net':0}
    result = daily_delivery_query(date)

    routes = {}
    for row in result:
        (_, delivery_name, user_type_id, delivery_boy, route_name, _, _, _, total_quantity, _) = row
        key = f"{delivery_boy} ({route_name})"
        if user_type_id == 8:
            key = f"{delivery_name} (Bulk)"
        routes[key] = routes.get(key, 0) + int(total_quantity)
        output['total'] += int(total_quantity)

    output['list'] = [{'delivery_boy': key, 'total': value} for key, value in routes.items()]

    return output

# start dispatch
def start_dispatch(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id= user_id, dispatch=True).exists():
        if request.method == 'POST':
            packets = request.POST.get('packets')
            try:
                dispatch = Dispatch.objects.get(date=timezone.localdate())
                dispatch.start_time = timezone.localtime().time()
                dispatch.save()
                return redirect('dispatch_home')
            except:
                dispatch = Dispatch(date=timezone.localdate(), start_time=timezone.localtime().time(), packets=packets, packets_variation=0)
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
        if request.method == 'POST':
            packets_variation = request.POST.get('packets_variation')
            dispatch = Dispatch.objects.get(date=timezone.localdate())
            dispatch.end_time = timezone.localtime().time()
            dispatch.packets_variation = int(packets_variation)
            dispatch.save()
            return redirect('dispatch_home')
        else:
            return redirect('dispatch_home')
    else:
        return redirect('dispatch_login')

