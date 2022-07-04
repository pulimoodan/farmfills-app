from datetime import datetime, timedelta
from django.utils import timezone
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from requests.api import patch
from users.models import Staff, User, ExtraLess, Vacation, Subscription, Delivery, RouteAssign, Route, Product, UserType, Purchase, Payment, Refund, Extra, Message, MessageRecord, Manager
from django.db.models import Q
import pytz
import json
from django.views.decorators.csrf import csrf_exempt
from farmfills_admin.forms import UserForm, ManagerSubscriptionForm, ManagerExtraLessForm, ManagerVacationForm, ManagerPaymentForm, ManagerRefundForm, ManagerExtraForm, MessageForm, ManagerUserForm
from farmfills_admin.views import getDataOfSub, get_status, update_balance_of_customer
from users.views import format_number, get_client_ip, getEndBalanceOfMonth, last_day_of_month, getPurchaseOfMonth, getPaymentOfMonth, checkDateOverlaps, getNextDelivery

# login page
def login(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        return redirect('manager_dashboard')
    return render(request, 'manager_login.html', {'error':error})


def login_validation(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            manager = Manager.objects.get(uname=username, password=password)
            request.session['farmfills_manager_id'] = manager.id
            return redirect('manager_dashoard')
        except:
            return redirect('/manager/login?error=Username or password is invalid')


def logout(request):
    request.session['farmfills_manager_id'] = None
    return redirect('manager_login')


def dashboard(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        return render(request, 'manager/index.html', {'user':user})
    else:
        return redirect('manager_login')


def customers_list(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        user_types = UserType.objects.all()
        routes = user.routes.all()
        return render(request, 'manager/customers-list.html', {'user':user, 'success':success, 'user_types':user_types, 'routes':routes})
    else:
        return redirect('manager_login')


def customers_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        form = ManagerUserForm(user.routes.all())
        if request.method == 'POST':
            formset = ManagerUserForm(user.routes.all(), request.POST, request.FILES)
            if formset.is_valid():
                formset.save()
                if request.POST.get('continue-edit') == 'true':
                    id = formset.id
                    return redirect('/manager/customers/edit/'+str(id)+'?success=1')
                else:
                    return redirect('/manager/customers/create?success=1')
        return render(request, 'manager/customers-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def customers_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customer = User.objects.get(id=id)
        form = ManagerUserForm(user.routes.all(), instance=customer)
        if request.method == 'POST':
            formset = ManagerUserForm(user.routes.all(), request.POST, request.FILES, instance=customer)
            if formset.is_valid():
                formset.save()
                return redirect('/manager/customers/edit/'+str(customer.id)+'?success=1')
        return render(request, 'manager/customers-edit.html', {'user':user, 'customer':customer, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def customer_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        customer = User.objects.get(id=id)
        customer.delete()
        return redirect('/manager/customers/list?success=1')
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_list(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():

        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))
        
        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # sorting columns of foreign key
        if columnName == 'route':
            columnName = 'route_id'
        elif columnName == 'user_type':
            columnName =  'user_type_id'

        # search filter
        searchValue = request.POST.get('search[value]', None)
        if searchValue is not None and searchValue != '': 
            searchValue = searchValue.lower()
            query += " and (LOWER(name) like '%%" + searchValue + "%%' or LOWER(delivery_name) like '%%" + searchValue + "%%' or mobile like '%%" + searchValue + "%%' )"
        

        # user type filter
        filterByUserType = request.POST.get('filterByUserType')
        if filterByUserType == 'none' or filterByUserType == '':
            query += " and (user_type_id IS NULL)"
        elif filterByUserType != 'all':
            query += " and (user_type_id=" + filterByUserType + ")"

        # route filter
        filterByRoute = request.POST.get('filterByRoute')
        if filterByRoute == 'none' or filterByRoute == '':
            query += " and (route_id IS NULL)"
        elif filterByRoute != 'all':
            query += " and (route_id=" + filterByRoute + ")"
            
        # total of filtered record
        totalRecordwithFilter = User.objects.raw('SELECT * FROM users_user WHERE route_id IN (' + str(staff_routes_ids) + ') ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = User.objects.filter(route__in=staff_routes).count()

        # filtered records
        if columnName is not None:
            query_data = User.objects.raw('SELECT * FROM users_user WHERE route_id IN (' + str(staff_routes_ids) + ') ' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = User.objects.raw('SELECT * FROM users_user WHERE route_id IN (' + str(staff_routes_ids) + ') ' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            if q.route is not None:
                data.append({'id':q.id, 'name':q.name + ' ' + q.delivery_name, 'mobile':q.mobile, 'route':q.route.name, 'user_type':q.user_type.name})
            else:
                data.append({'id':q.id, 'name':q.name + ' ' + q.delivery_name, 'mobile':q.mobile, 'route':None, 'user_type':q.user_type.name})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('admin_login')



def customers_followup(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        user_types = UserType.objects.all()
        day = timezone.localtime(timezone.now()).replace(day=1)
        thismonth = day.strftime('%b')
        day -= timedelta(days=1)
        before1month = day.strftime('%b')
        day = day.replace(day=1) - timedelta(days=1)
        before2month = day.strftime('%b')
        return render(request, 'manager/customers-followup.html', {'user':user, 'routes':user.routes.all(), 'thismonth':thismonth, 'before1month':before1month, 'before2month':before2month, 'user_types':user_types})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_followup(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        
        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))

        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # sorting columns of foreign key
        if columnName == 'route':
            columnName = 'route_id'
        elif columnName == 'user_type':
            columnName =  'user_type_id'

        # search filter
        searchValue = request.POST.get('search[value]', None)
        if searchValue is not None and searchValue != '': 
            searchValue = searchValue.lower()
            query += " and (LOWER(name) like '%%" + searchValue + "%%' or LOWER(delivery_name) like '%%" + searchValue + "%%' or mobile like '%%" + searchValue + "%%' )"

        # route filter
        filterByRoute = request.POST.get('filterByRoute')
        if filterByRoute == 'none' or filterByRoute == '':
            query += " and (route_id IS NULL)"
        elif filterByRoute != 'all':
            query += " and (route_id=" + filterByRoute + ")"

        # user type filter
        filterByUserType = request.POST.get('filterByUserType')
        if filterByUserType == 'none' or filterByUserType == '':
            query += " and (user_type_id IS NULL)"
        elif filterByUserType != 'all':
            query += " and (user_type_id=" + filterByUserType + ")"

        # user status filter
        filterByStatus = request.POST.get('filterByStatus')
        if filterByStatus == 'none' or filterByStatus == '':
            query += " and (status IS NULL)"
        elif filterByStatus != 'all':
            query += " and (status='" + filterByStatus + "')"

        # bill notification filter
        filterByBillNotification = request.POST.get('filterByBillNotification')
        if filterByBillNotification == 'sent':
            query += " and (EXTRACT(MONTH FROM bill_send_date)=" + timezone.localtime(timezone.now()).strftime('%m') + " and EXTRACT(YEAR FROM bill_send_date)=" + timezone.localtime(timezone.now()).strftime('%Y') + ")"
        elif filterByBillNotification == 'not sent':
            query += " and (EXTRACT(MONTH FROM bill_send_date) !=" + timezone.localtime(timezone.now()).strftime('%m') + " or EXTRACT(YEAR FROM bill_send_date) !=" + timezone.localtime(timezone.now()).strftime('%Y') + " or bill_send_date IS NULL)"

        filterCustomers = []

        customers = User.objects.filter(route__in=staff_routes)
        # user bill paid filter
        filterByBillPaid = request.POST.get('filterByBillPaid')
        if filterByBillPaid != 'all':
            for c in customers:

                def balance2Updated(obj):
                    last_day = last_day_of_month(timezone.localtime(timezone.now()))
                    last_day = last_day.replace(day=1)
                    last_day = last_day - timedelta(days=1)
                    balance2 =  getEndBalanceOfMonth(last_day, obj)
                    last_day = last_day_of_month(timezone.localtime(timezone.now()))
                    payment1 =  getPaymentOfMonth(last_day, obj)
                    return balance2 + payment1
                
                if filterByBillPaid == 'not paid':
                    if balance2Updated(c) < 0:
                        filterCustomers.append(c.id)
                        continue
                elif filterByBillPaid == 'paid':
                    if balance2Updated(c) >= 0:
                        filterCustomers.append(c.id)
                        continue
        
        if filterCustomers:
            filterCustomers = ', '.join(str(i) for i in filterCustomers)
            query += " and (id IN (" + filterCustomers + "))"
            
        # total of filtered record
        totalRecordwithFilter = User.objects.raw('SELECT * FROM users_user WHERE route_id IN (' + str(staff_routes_ids) + ') ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = len(customers)

        # filtered records
        if columnName is not None:
            query_data = User.objects.raw('SELECT * FROM users_user WHERE route_id IN (' + str(staff_routes_ids) + ') ' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = User.objects.raw('SELECT * FROM users_user WHERE route_id IN (' + str(staff_routes_ids) + ') ' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            bill_send_date = None
            if q.bill_send_date is not None:
                bill_send_date = timezone.localtime(q.bill_send_date).strftime('%d %B, %Y')

            def balance1(obj):
                last_day = last_day_of_month(timezone.localtime(timezone.now()))
                return getEndBalanceOfMonth(last_day, obj)

            def payment1(obj):
                last_day = last_day_of_month(timezone.localtime(timezone.now()))
                return getPaymentOfMonth(last_day, obj)
            
            def balance2(obj):
                last_day = last_day_of_month(timezone.localtime(timezone.now()))
                last_day = last_day.replace(day=1)
                last_day = last_day - timedelta(days=1)
                return getEndBalanceOfMonth(last_day, obj)

            def balance2Updated(obj):
                last_day = last_day_of_month(timezone.localtime(timezone.now()))
                last_day = last_day.replace(day=1)
                last_day = last_day - timedelta(days=1)
                balance2 =  getEndBalanceOfMonth(last_day, obj)
                last_day = last_day_of_month(timezone.localtime(timezone.now()))
                payment1 =  getPaymentOfMonth(last_day, obj)
                return balance2 + payment1

            def purchase2(obj):
                last_day = last_day_of_month(timezone.localtime(timezone.now()))
                last_day = last_day.replace(day=1)
                last_day = last_day - timedelta(days=1)
                return getPurchaseOfMonth(last_day, obj)

            def payment2(obj):
                last_day = last_day_of_month(timezone.localtime(timezone.now()))
                last_day = last_day.replace(day=1)
                last_day = last_day - timedelta(days=1)
                return getPaymentOfMonth(last_day, obj)

            def balance3(obj):
                last_day = last_day_of_month(timezone.localtime(timezone.now()))
                last_day = last_day.replace(day=1)
                last_day = last_day - timedelta(days=1)
                last_day = last_day.replace(day=1)
                last_day = last_day - timedelta(days=1)
                return getEndBalanceOfMonth(last_day, obj)

            data.append({
                'id':q.id, 'name':q.name + ' ' + q.delivery_name, 
                'mobile':q.mobile, 
                'bill_send_date':bill_send_date, 
                'balance3':balance3(q), 
                'balance2':balance2(q), 
                'balance2Updated':balance2Updated(q), 
                'balance1':balance1(q), 
                'payment2':payment2(q), 
                'payment1':payment1(q), 
                'purchase2':purchase2(q), 
            })

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('admin_login')



def customer_transactions(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customer = User.objects.get(id=id)

        transaction_data = []

        purchases = Purchase.objects.filter(user=customer).order_by('-date', '-id')

        payments = Payment.objects.filter(user=customer, paid=True).order_by('-date', '-id')

        refunds = Refund.objects.filter(user=customer).order_by('-date', '-id')

        extras = Extra.objects.filter(user=customer).order_by('-date', '-id')

        transaction_data = list(purchases) 

        transaction_data += list(payments)
        transaction_data += list(refunds)
        transaction_data += list(extras)

        transaction_data = sorted(transaction_data, key=lambda k: k.date, reverse=True) 

        return render(request, 'manager/customer-transactions.html', {'user':user, 'success':success, 'customer':customer, 'transaction_data':transaction_data})
    else:
        return redirect('manager_login')



def customer_subscriptions(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customers = User.objects.filter(route__in=user.routes.all())
        return render(request, 'manager/customers-subscription.html', {'user':user, 'error':error, 'success':success, 'customers':customers})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_subscriptions(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        
        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))

        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # customer filter
        filterByCustomer = request.POST.get('filterByCustomer')
        if filterByCustomer != 'all':
            query += " and (s.user_id=" + filterByCustomer + ")"

        # subscription type filter
        filterBySubType = request.POST.get('filterBySubType')
        if filterBySubType != 'all':
            query += " and (s.sub_type='" + filterBySubType + "')"
            
        # total of filtered record
        totalRecordwithFilter = Subscription.objects.raw('SELECT * FROM users_subscription s INNER JOIN users_user u ON (u.id = s.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Subscription.objects.filter(user__route__in=staff_routes).count()

        # filtered records
        if columnName is not None:
            query_data = Subscription.objects.raw('SELECT * FROM users_subscription s INNER JOIN users_user u ON (u.id = s.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY s.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Subscription.objects.raw('SELECT * FROM users_subscription s INNER JOIN users_user u ON (u.id = s.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY s.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            details = ''
            
            if q.sub_type == 'daily':
                details = str(q.daily_day1) + ' ltr'
                if q.daily_day2 != 0 and q.daily_day2 is not None:
                    details += ' and ' + str(q.daily_day2) + ' ltr'
            elif q.sub_type == 'alternate':
                details = str(q.alternate_quantity) + ' ltr'
            elif q.sub_type == 'custom':
                details = str(q.custom_quantity) + ' ltr in every ' + str(q.custom_interval) + ' days'
            elif q.sub_type == 'weekly':
                details = 'Mon: ' + str(q.weekly_mon) + ' Tue: ' + str(q.weekly_tue) + ' Wed: ' + str(q.weekly_wed) + ' Thu: ' + str(q.weekly_thu) + ' Fri: ' + str(q.weekly_fri) + ' Sat: ' + str(q.weekly_sat) + ' Sun: ' + str(q.weekly_sun)

            end_date = q.end_date
            if end_date is not None:
                end_date = q.end_date.strftime('%b %d, %Y')
            
            data.append({'id':q.id, 'name':q.user.name + ' ' + q.user.delivery_name, 'sub_type':q.sub_type, 'start_date':q.start_date.strftime('%b %d, %Y'), 'end_date':end_date, 'details':details, 'created_by':q.created_by, 'edited_by':q.edited_by})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('manager_login')


def subscriptions_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        form = ManagerSubscriptionForm(user.routes.all())
        if request.method == 'POST':
            formset = ManagerSubscriptionForm(user.routes.all(), request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)
                
                # validate form
                valid = True

                if formset.sub_type == 'daily':
                    if formset.daily_day1 == '' or formset.daily_day1 is None or formset.daily_day1 <= 0:
                        valid = False
                    elif formset.daily_day2 == '' or formset.daily_day2 is None or formset.daily_day2 < 0:
                        formset.daily_day2 = 0
                elif formset.sub_type == 'custom':
                    if formset.custom_quantity == '' or formset.custom_quantity is None or formset.custom_interval == '' or formset.custom_interval is None or formset.custom_interval < 3:
                        valid = False
                elif formset.sub_type == 'alternate':
                    if formset.alternate_quantity == '' or formset.alternate_quantity is None or formset.alternate_quantity <= 0:
                        valid = False
                elif formset.sub_type == 'weekly':
                    hasValue = False
                    if formset.weekly_mon == '' or formset.weekly_mon is None or formset.weekly_mon < 0: formset.weekly_mon = 0 
                    elif formset.weekly_mon > 0: hasValue = True
                    if formset.weekly_tue == '' or formset.weekly_tue is None or formset.weekly_tue < 0: formset.weekly_tue = 0 
                    elif formset.weekly_tue > 0: hasValue = True
                    if formset.weekly_wed == '' or formset.weekly_wed is None or formset.weekly_wed < 0: formset.weekly_wed = 0 
                    elif formset.weekly_wed > 0: hasValue = True
                    if formset.weekly_thu == '' or formset.weekly_thu is None or formset.weekly_thu < 0: formset.weekly_thu = 0 
                    elif formset.weekly_thu > 0: hasValue = True
                    if formset.weekly_fri == '' or formset.weekly_fri is None or formset.weekly_fri < 0: formset.weekly_fri = 0 
                    elif formset.weekly_fri > 0: hasValue = True
                    if formset.weekly_sat == '' or formset.weekly_sat is None or formset.weekly_sat < 0: formset.weekly_sat = 0 
                    elif formset.weekly_sat > 0: hasValue = True
                    if formset.weekly_sun == '' or formset.weekly_sun is None or formset.weekly_sun < 0: formset.weekly_sun = 0 
                    elif formset.weekly_sun > 0: hasValue = True

                    if not hasValue:
                        valid = False
                
                if not valid:
                    return redirect('/manager/customers/subscriptions?error=1')

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect('/manager/customers/subscriptions?error=2')
                
                subs = Subscription.objects.filter(user=formset.user)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, subs):
                    return redirect('/manager/customers/subscriptions?error=3')

                formset.created_by = 'manager'
                formset.edited_by = 'manager'

                formset.save()
                return redirect('/manager/customers/subscriptions?success=1')
        return render(request, 'manager/subscriptions-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def subscriptions_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        sub = Subscription.objects.get(id=id)

        status = get_status(sub)

        form = ManagerSubscriptionForm(user.routes.all(), instance=sub)
        if request.method == 'POST':
            formset = ManagerSubscriptionForm(user.routes.all(), request.POST, request.FILES, instance=sub)
            if formset.is_valid():
                formset = formset.save(commit=False)
                
                # validate form
                valid = True

                if formset.sub_type == 'daily':
                    if formset.daily_day1 == '' or formset.daily_day1 is None or formset.daily_day1 <= 0:
                        valid = False
                    elif formset.daily_day2 == '' or formset.daily_day2 is None or formset.daily_day2 < 0:
                        formset.daily_day2 = 0
                elif formset.sub_type == 'custom':
                    if formset.custom_quantity == '' or formset.custom_quantity is None or formset.custom_interval == '' or formset.custom_interval is None or formset.custom_interval < 3:
                        valid = False
                elif formset.sub_type == 'alternate':
                    if formset.alternate_quantity == '' or formset.alternate_quantity is None or formset.alternate_quantity <= 0:
                        valid = False
                elif formset.sub_type == 'weekly':
                    hasValue = False
                    if formset.weekly_mon == '' or formset.weekly_mon is None or formset.weekly_mon < 0: formset.weekly_mon = 0 
                    elif formset.weekly_mon > 0: hasValue = True
                    if formset.weekly_tue == '' or formset.weekly_tue is None or formset.weekly_tue < 0: formset.weekly_tue = 0 
                    elif formset.weekly_tue > 0: hasValue = True
                    if formset.weekly_wed == '' or formset.weekly_wed is None or formset.weekly_wed < 0: formset.weekly_wed = 0 
                    elif formset.weekly_wed > 0: hasValue = True
                    if formset.weekly_thu == '' or formset.weekly_thu is None or formset.weekly_thu < 0: formset.weekly_thu = 0 
                    elif formset.weekly_thu > 0: hasValue = True
                    if formset.weekly_fri == '' or formset.weekly_fri is None or formset.weekly_fri < 0: formset.weekly_fri = 0 
                    elif formset.weekly_fri > 0: hasValue = True
                    if formset.weekly_sat == '' or formset.weekly_sat is None or formset.weekly_sat < 0: formset.weekly_sat = 0 
                    elif formset.weekly_sat > 0: hasValue = True
                    if formset.weekly_sun == '' or formset.weekly_sun is None or formset.weekly_sun < 0: formset.weekly_sun = 0 
                    elif formset.weekly_sun > 0: hasValue = True

                    if not hasValue:
                        valid = False
                
                if not valid:
                    return redirect(f'/manager/subscriptions/{id}?error=1')

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect(f'/manager/subscriptions/{id}?error=2')
                
                subs = Subscription.objects.filter(user=formset.user).exclude(id=id)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, subs):
                    return redirect(f'/manager/subscriptions/{id}?error=3')

                formset.edited_by = 'manager'
                
                formset.save()
                return redirect(f'/manager/subscriptions/{id}?success=1')
            return redirect(f'/manager/subscriptions/{id}')
        return render(request, 'manager/subscriptions-edit.html', {'user':user, 'status':status, 'success':success, 'form':form, 'error':error, 'subscription':sub})
    else:
        return redirect('manager_login')


def subscription_end(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        subscription = Subscription.objects.get(id=id)
        if subscription.end_date is not None:
            if subscription.end_date <= timezone.localtime(timezone.now()).date():
                return redirect('/manager/customers/subscriptions?error=5')
        if subscription.start_date > timezone.localtime(timezone.now()).date():
            return redirect('/manager/customers/subscriptions?error=4')
        subscription.end_date = timezone.localtime(timezone.now()).date()
        subscription.save()
        return redirect('/manager/customers/subscriptions?success=3')
    else:
        return redirect('manager_login')


def subscription_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        subscription = Subscription.objects.get(id=id)
        subscription.delete()
        return redirect('/manager/customers/subscriptions?success=2')
    else:
        return redirect('manager_login')




def customer_extraless(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customers = User.objects.filter(route__in=user.routes.all())
        return render(request, 'manager/customers-extraless.html', {'user':user, 'error':error, 'success':success, 'customers':customers})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_extraless(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        
        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))

        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # customer filter
        filterByCustomer = request.POST.get('filterByCustomer')
        if filterByCustomer != 'all':
            query += " and (user_id=" + filterByCustomer + ")"

        # start date filter
        filterByStartDate = request.POST.get('filterByStartDate')
        if filterByStartDate != '' and filterByStartDate is not None:
            filterByStartDate = timezone.make_aware(datetime.strptime(filterByStartDate, '%Y-%m-%d')).date()
            query += " and (start_date = '" + str(filterByStartDate) + "')"

        # end date filter
        filterByEndDate = request.POST.get('filterByEndDate')
        if filterByEndDate != '' and filterByEndDate is not None:
            filterByEndDate = timezone.make_aware(datetime.strptime(filterByEndDate, '%Y-%m-%d')).date()
            query += " and (end_date = '" + str(filterByEndDate) + "' )"

        # total of filtered record
        totalRecordwithFilter = ExtraLess.objects.raw('SELECT * FROM users_extraless e INNER JOIN users_user u ON (u.id = e.user_id) WHERE (u.route_id IN(' + str(staff_routes_ids) + ')) ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = ExtraLess.objects.filter(user__route__in=staff_routes).count()

        # filtered records
        if columnName is not None:
            query_data = ExtraLess.objects.raw('SELECT * FROM users_extraless e INNER JOIN users_user u ON (u.id = e.user_id) WHERE (u.route_id IN(' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY e.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = ExtraLess.objects.raw('SELECT * FROM users_extraless e INNER JOIN users_user u ON (u.id = e.user_id) WHERE (u.route_id IN(' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY e.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:

            end_date = q.end_date
            if end_date is not None:
                end_date = q.end_date.strftime('%b %d, %Y')
            
            data.append({'id':q.id, 'name':q.user.name + ' ' + q.user.delivery_name, 'start_date':q.start_date.strftime('%b %d, %Y'), 'end_date':end_date, 'quantity':q.quantity, 'created_by':q.created_by, 'edited_by':q.edited_by})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('manager_login')


def extraless_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        form = ManagerExtraLessForm(user.routes.all())
        if request.method == 'POST':
            formset = ManagerExtraLessForm(user.routes.all(), request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect('/manager/customers/extraless?error=2')
                
                extralesses = ExtraLess.objects.filter(user=formset.user)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, extralesses):
                    return redirect('/manager/customers/extraless?error=3')

                formset.created_by = 'manager'
                formset.edited_by = 'manager'

                formset.save()

                return redirect('/manager/customers/extraless?success=1')
        return render(request, 'manager/extraless-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def extraless_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        eless = ExtraLess.objects.get(id=id)

        status = get_status(eless)

        form = ManagerExtraLessForm(user.routes.all(), instance=eless)
        if request.method == 'POST':
            formset = ManagerExtraLessForm(user.routes.all(), request.POST, request.FILES, instance=eless)
            if formset.is_valid():
                formset = formset.save(commit=False)

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect(f'/manager/extraless/{id}?error=2')
                
                extralesses = ExtraLess.objects.filter(user=formset.user).exclude(id=id)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, extralesses):
                    return redirect(f'/manager/extraless/{id}?error=3')
                
                formset.edited_by = 'manager'

                formset.save()

                return redirect(f'/manager/extraless/{id}?success=1')
        return render(request, 'manager/extraless-edit.html', {'user':user, 'error':error, 'success':success, 'status':status, 'extraless':eless, 'form':form})
    else:
        return redirect('manager_login')


def extraless_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        extraless = ExtraLess.objects.get(id=id)
        extraless.delete()
        return redirect('/manager/customers/extraless?success=2')
    else:
        return redirect('manager_login')


def extraless_end(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        eless = ExtraLess.objects.get(id=id)
        if eless.end_date is not None:
            if eless.end_date <= timezone.localtime(timezone.now()).date():
                return redirect('/manager/customers/extraless?error=5')
        if eless.start_date > timezone.localtime(timezone.now()).date():
            return redirect('/manager/customers/extraless?error=4')
        eless.end_date = timezone.localtime(timezone.now()).date()
        eless.save()
        return redirect('/manager/customers/extraless?success=3')
    else:
        return redirect('manager_login')




def customer_vacations(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customers = User.objects.filter(route__in=user.routes.all())
        return render(request, 'manager/customers-vacation.html', {'user':user, 'error':error, 'success':success, 'customers':customers})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_vacations(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        
        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))

        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # customer filter
        filterByCustomer = request.POST.get('filterByCustomer')
        if filterByCustomer != 'all':
            query += " and (user_id=" + filterByCustomer + ")"

        # start date filter
        filterByStartDate = request.POST.get('filterByStartDate')
        if filterByStartDate != '' and filterByStartDate is not None:
            filterByStartDate = timezone.make_aware(datetime.strptime(filterByStartDate, '%Y-%m-%d')).date()
            query += " and (start_date = '" + str(filterByStartDate) + "')"

        # end date filter
        filterByEndDate = request.POST.get('filterByEndDate')
        if filterByEndDate != '' and filterByEndDate is not None:
            filterByEndDate = timezone.make_aware(datetime.strptime(filterByEndDate, '%Y-%m-%d')).date()
            query += " and (end_date = '" + str(filterByEndDate) + "' )"

        # total of filtered record
        totalRecordwithFilter = Vacation.objects.raw('SELECT * FROM users_vacation v INNER JOIN users_user u ON (u.id = v.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Vacation.objects.filter(user__route__in=staff_routes).count()

        # filtered records
        if columnName is not None:
            query_data = Vacation.objects.raw('SELECT * FROM users_vacation v INNER JOIN users_user u ON (u.id = v.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY v.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Vacation.objects.raw('SELECT * FROM users_vacation v INNER JOIN users_user u ON (u.id = v.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY v.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:

            end_date = q.end_date
            if end_date is not None:
                end_date = q.end_date.strftime('%b %d, %Y')
            
            data.append({'id':q.id, 'name':q.user.name + ' ' + q.user.delivery_name, 'start_date':q.start_date.strftime('%b %d, %Y'), 'end_date':end_date, 'created_by':q.created_by, 'edited_by':q.edited_by})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('manager_login')


def vacations_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        form = ManagerVacationForm(user.routes.all())
        if request.method == 'POST':
            formset = ManagerVacationForm(user.routes.all(), request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect('/manager/customers/vacations?error=2')
                
                vacations = Vacation.objects.filter(user=formset.user)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, vacations):
                    return redirect('/manager/customers/vacations?error=3')
                
                formset.created_by = 'manager'
                formset.edited_by = 'manager'

                formset.save()

                return redirect('/manager/customers/vacations?success=1')
        return render(request, 'manager/vacations-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def vacations_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        vac = Vacation.objects.get(id=id)

        status = get_status(vac)

        form = ManagerVacationForm(user.routes.all(), instance=vac)
        if request.method == 'POST':
            formset = ManagerVacationForm(user.routes.all(), request.POST, request.FILES, instance=vac)
            if formset.is_valid():
                formset = formset.save(commit=False)

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect(f'/manager/vacations/{id}?error=2')
                
                vacations = Vacation.objects.filter(user=formset.user).exclude(id=id)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, vacations):
                    return redirect(f'/manager/vacations/{id}?error=3')
                
                formset.edited_by = 'manager'

                formset.save()

                return redirect(f'/manager/vacations/{id}?success=1')
        return render(request, 'manager/vacations-edit.html', {'user':user, 'error':error, 'success':success, 'status':status, 'form':form, 'vacation':vac})
    else:
        return redirect('manager_login')


def vacation_end(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        vacation = Vacation.objects.get(id=id)
        if vacation.end_date is not None:
            if vacation.end_date <= timezone.localtime(timezone.now()).date():
                return redirect('/manager/customers/vacations?error=5')
        if vacation.start_date > timezone.localtime(timezone.now()).date():
            return redirect('/manager/customers/vacations?error=4')
        vacation.end_date = timezone.localtime(timezone.now()).date()
        vacation.save()
        return redirect('/manager/customers/vacations?success=3')
    else:
        return redirect('manager_login')


def vacation_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        vacation = Vacation.objects.get(id=id)
        vacation.delete()
        return redirect('/manager/customers/vacations?success=2')
    else:
        return redirect('manager_login')




def customers_purchases(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customers = User.objects.filter(route__in=user.routes.all())
        return render(request, 'manager/customers-purchase.html', {'user':user, 'success':success, 'customers':customers})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_purchases(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        
        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))

        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # sorting columns of foreign key
        if columnName == 'product':
            columnName = 'p.product_id'
        
        # customer filter
        filterByCustomer = request.POST.get('filterByCustomer')
        if filterByCustomer != 'all':
            query += " and (p.user_id=" + filterByCustomer + ")"

        # from date filter
        filterByFromDate = request.POST.get('filterByFromDate')
        if filterByFromDate != '' and filterByFromDate is not None:
            filterByFromDate = timezone.make_aware(datetime.strptime(filterByFromDate, '%Y-%m-%d')).date()
            query += " and (date(p.date) >= '" + str(filterByFromDate) + "')"

        # to date filter
        filterByToDate = request.POST.get('filterByToDate')
        if filterByToDate != '' and filterByToDate is not None:
            filterByToDate = timezone.make_aware(datetime.strptime(filterByToDate, '%Y-%m-%d')).date()
            query += " and (date(p.date) <= '" + str(filterByToDate) + "')"
            
        # total of filtered record
        totalRecordwithFilter = Purchase.objects.raw('SELECT p.user_id, p.id, p.date FROM users_purchase p INNER JOIN users_user u ON (u.id = p.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ';')
        totalRecordwithFilter = len(list(totalRecordwithFilter))

        # total records
        totalRecords = Purchase.objects.filter(user__route__in=staff_routes).count()

        # filtered records
        if columnName is not None:
            query_data = Purchase.objects.raw('SELECT * FROM users_purchase p INNER JOIN users_user u ON (u.id = p.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY p.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Purchase.objects.raw('SELECT * FROM users_purchase p INNER JOIN users_user u ON (u.id = p.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY p.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            user = User.objects.get(id=q.user_id)
            product = Product.objects.get(id=q.product_id)
            data.append({'id':q.id, 'name':user.name + ' ' + user.delivery_name, 'date':timezone.localtime(q.date).strftime('%d %b, %Y'), 'product':product.name, 'quantity':str(q.quantity), 'amount':str(q.amount), 'balance':q.balance})
        
        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('manager_login')


def customers_payments(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customers = User.objects.filter(route__in=user.routes.all())
        return render(request, 'manager/customers-payment.html', {'user':user, 'success':success, 'customers':customers})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_payments(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        
        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))

        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # sorting columns of foreign key
        if columnName == 'route':
            columnName = 'route_id'
        elif columnName == 'user_type':
            columnName =  'user_type_id'
        
        # customer filter
        filterByCustomer = request.POST.get('filterByCustomer')
        if filterByCustomer != 'all':
            query += " and (user_id=" + filterByCustomer + ")"


        # from date filter
        filterByFromDate = request.POST.get('filterByFromDate')
        if filterByFromDate != '' and filterByFromDate is not None:
            filterByFromDate = timezone.make_aware(datetime.strptime(filterByFromDate, '%Y-%m-%d')).date()
            query += " and (date(date) >= '" + str(filterByFromDate) + "')"


        # to date filter
        filterByToDate = request.POST.get('filterByToDate')
        if filterByToDate != '' and filterByToDate is not None:
            filterByToDate = timezone.make_aware(datetime.strptime(filterByToDate, '%Y-%m-%d')).date()
            query += " and (date(date) <= '" + str(filterByToDate) + "')"

            
        # total of filtered record
        totalRecordwithFilter = Payment.objects.raw('SELECT * FROM users_payment p INNER JOIN users_user u ON (u.id = p.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) AND p.paid=true ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Payment.objects.filter(paid=True, user__route__in=staff_routes).count()

        # filtered records
        if columnName is not None:
            query_data = Payment.objects.raw('SELECT * FROM users_payment p INNER JOIN users_user u ON (u.id = p.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) AND p.paid=true ' + query + ' ORDER BY p.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Payment.objects.raw('SELECT * FROM users_payment p INNER JOIN users_user u ON (u.id = p.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) AND p.paid=true ' + query + ' ORDER BY p.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            user = User.objects.get(id=q.user_id)
            data.append({'id':q.id, 'name':user.name + ' ' + user.delivery_name, 'date':timezone.localtime(q.date).strftime('%d %b, %Y'), 'amount':str(q.amount), 'mode':q.mode, 'description':q.description, 'balance':q.balance})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('manager_login')


def payments_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        form = ManagerPaymentForm(user.routes.all())
        if request.method == 'POST':
            formset = ManagerPaymentForm(user.routes.all(), request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.balance = 0
                formset.paid = True
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/manager/customers/transactions/payments?success=1')
        return render(request, 'manager/payments-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def payments_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        payment = Payment.objects.get(id=id)
        form = ManagerPaymentForm(user.routes.all(), instance=payment)
        if request.method == 'POST':
            formset = ManagerPaymentForm(user.routes.all(), request.POST, request.FILES, instance=payment)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.paid = True
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/manager/payments/edit/'+str(payment.id)+'?success=1')
        return render(request, 'manager/payments-edit.html', {'user':user, 'payment':payment, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def payment_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        payment = Payment.objects.get(id=id)
        payment.delete()
        update_balance_of_customer(payment.user)
        return redirect('/manager/customers/transactions/payments?success=2')
    else:
        return redirect('manager_login')




def customers_refunds(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customers = User.objects.filter(route__in=user.routes.all())
        return render(request, 'manager/customers-refund.html', {'user':user, 'success':success, 'customers':customers})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_refunds(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():

        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))
        
        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # sorting columns of foreign key
        if columnName == 'product':
            columnName = 'product_id'
        
        # customer filter
        filterByCustomer = request.POST.get('filterByCustomer')
        if filterByCustomer != 'all':
            query += " and (user_id=" + filterByCustomer + ")"


        # from date filter
        filterByFromDate = request.POST.get('filterByFromDate')
        if filterByFromDate != '' and filterByFromDate is not None:
            filterByFromDate = timezone.make_aware(datetime.strptime(filterByFromDate, '%Y-%m-%d')).date()
            query += " and (date(date) >= '" + str(filterByFromDate) + "')"


        # to date filter
        filterByToDate = request.POST.get('filterByToDate')
        if filterByToDate != '' and filterByToDate is not None:
            filterByToDate = timezone.make_aware(datetime.strptime(filterByToDate, '%Y-%m-%d')).date()
            query += " and (date(date) <= '" + str(filterByToDate) + "')"

            
        # total of filtered record
        totalRecordwithFilter = Refund.objects.raw('SELECT * FROM users_refund r INNER JOIN users_user u ON (u.id = r.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Refund.objects.filter(user__route__in=staff_routes).count()

        # filtered records
        if columnName is not None:
            query_data = Refund.objects.raw('SELECT * FROM users_refund r INNER JOIN users_user u ON (u.id = r.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY r.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Refund.objects.raw('SELECT * FROM users_refund r INNER JOIN users_user u ON (u.id = r.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY r.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            user = User.objects.get(id=q.user_id)
            product = Product.objects.get(id=q.product_id)
            data.append({'id':q.id, 'name':user.name + ' ' + user.delivery_name, 'date':timezone.localtime(q.date).strftime('%d %b, %Y'), 'product':product.name, 'quantity':str(q.quantity), 'amount':str(q.amount), 'balance':q.balance, 'reason':q.reason})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('manager_login')


def refunds_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        form = ManagerRefundForm(user.routes.all())
        if request.method == 'POST':
            formset = ManagerRefundForm(user.routes.all(), request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.balance = 0
                formset.amount = (formset.product.price + formset.user.user_type.price_variation) * formset.quantity
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/manager/customers/transactions/refunds?success=1')
        return render(request, 'manager/refunds-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def refunds_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        refund = Refund.objects.get(id=id)
        form = ManagerRefundForm(user.routes.all(), instance=refund)
        if request.method == 'POST':
            formset = ManagerRefundForm(user.routes.all(), request.POST, request.FILES, instance=refund)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.amount = (formset.product.price + formset.user.user_type.price_variation) * formset.quantity
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/manager/refunds/edit/'+str(refund.id)+'?success=1')
        return render(request, 'manager/refunds-edit.html', {'user':user, 'refund':refund, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def refund_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        refund = Refund.objects.get(id=id)
        refund.delete()
        update_balance_of_customer(refund.user)
        return redirect('/manager/customers/transactions/refunds?success=2')
    else:
        return redirect('manager_login')




def customers_extras(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        customers = User.objects.filter(route__in=user.routes.all())
        return render(request, 'manager/customers-extra.html', {'user':user, 'success':success, 'customers':customers})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_customers_extras(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():

        staff = Manager.objects.get(id= user_id)
        staff_routes = staff.routes.all()
        staff_routes_ids = ', '.join(list(str(staff_route.id) for staff_route in staff_routes))
        
        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # sorting columns of foreign key
        if columnName == 'product':
            columnName = 'product_id'
        
        # customer filter
        filterByCustomer = request.POST.get('filterByCustomer')
        if filterByCustomer != 'all':
            query += " and (user_id=" + filterByCustomer + ")"


        # from date filter
        filterByFromDate = request.POST.get('filterByFromDate')
        if filterByFromDate != '' and filterByFromDate is not None:
            filterByFromDate = timezone.make_aware(datetime.strptime(filterByFromDate, '%Y-%m-%d')).date()
            query += " and (date(date) >= '" + str(filterByFromDate) + "')"


        # to date filter
        filterByToDate = request.POST.get('filterByToDate')
        if filterByToDate != '' and filterByToDate is not None:
            filterByToDate = timezone.make_aware(datetime.strptime(filterByToDate, '%Y-%m-%d')).date()
            query += " and (date(date) <= '" + str(filterByToDate) + "')"

            
        # total of filtered record
        totalRecordwithFilter = Extra.objects.raw('SELECT * FROM users_extra e INNER JOIN users_user u ON (u.id = e.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Extra.objects.filter(user__route__in=staff_routes).count()

        # filtered records
        if columnName is not None:
            query_data = Extra.objects.raw('SELECT * FROM users_extra e INNER JOIN users_user u ON (u.id = e.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY e.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Extra.objects.raw('SELECT * FROM users_extra e INNER JOIN users_user u ON (u.id = e.user_id) WHERE (u.route_id IN (' + str(staff_routes_ids) + ')) ' + query + ' ORDER BY e.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            user = User.objects.get(id=q.user_id)
            product = Product.objects.get(id=q.product_id)
            data.append({'id':q.id, 'name':user.name + ' ' + user.delivery_name, 'date':timezone.localtime(q.date).strftime('%d %b, %Y'), 'product':product.name, 'quantity':str(q.quantity), 'amount':str(q.amount), 'balance':q.balance})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('manager_login')


def extras_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        form = ManagerExtraForm(user.routes.all())
        if request.method == 'POST':
            formset = ManagerExtraForm(user.routes.all(), request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.balance = 0
                formset.amount = (formset.product.price + formset.user.user_type.price_variation) * formset.quantity
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/manager/customers/transactions/extras?success=1')
        return render(request, 'manager/extras-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def extras_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        extra = Extra.objects.get(id=id)
        form = ManagerExtraForm(user.routes.all(), instance=extra)
        if request.method == 'POST':
            formset = ManagerExtraForm(user.routes.all(), request.POST, request.FILES, instance=extra)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.amount = (formset.product.price + formset.user.user_type.price_variation) * formset.quantity
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/manager/extras/edit/'+str(extra.id)+'?success=1')
        return render(request, 'manager/extras-edit.html', {'user':user, 'extra':extra, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def extra_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        extra = Extra.objects.get(id=id)
        extra.delete()
        update_balance_of_customer(extra.user)
        return redirect('/manager/customers/transactions/extras?success=2')
    else:
        return redirect('manager_login')




def message(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        return render(request, 'manager/message.html', {'user':user, 'success':success, 'error':error})
    else:
        return redirect('manager_login')


@ csrf_exempt
def manager_datatable_ajax_message(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        
        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""

        # search filter
        searchValue = request.POST.get('search[value]', None)
        if searchValue is not None and searchValue != '': 
            searchValue = searchValue.lower()
            query += " AND (LOWER(title) like '%%" + searchValue + "%%' or LOWER(content) like '%%" + searchValue + "%%')"

        
        # total records
        totalRecords = Message.objects.all().count()

        # total of filtered record
        totalRecordwithFilter = 0
        if searchValue is None and searchValue == '':
            totalRecordwithFilter = Message.objects.raw('SELECT * FROM users_message WHERE true' + query)
            totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)
        else:
            totalRecordwithFilter = totalRecords

        # filtered records
        if columnName is not None:
            query_data = Message.objects.raw('SELECT * FROM users_message WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Message.objects.raw('SELECT * FROM users_message WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            created_date = '-'
            if q.created_date is not None:
                created_date = q.created_date.strftime('%d %b, %Y')
            data.append({'id':q.id, 'title': q.title, 'created_date':created_date, 'content':q.content[:50] + '..'})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data
        }
        return JsonResponse(response)
    else:
        return redirect('manager_login')


def delete_message(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Manager.objects.filter(id= user_id).exists():
        message = Message.objects.get(id=id)
        message.delete()
        return redirect('/manager/message?success=2')
    else:
        return redirect('manager_login')


def message_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        form = MessageForm()
        if request.method == 'POST':
            formset = MessageForm(request.POST, request.FILES)
            if formset.is_valid():
                formset.save()
                return redirect('/manager/message?success=1')
        return render(request, 'manager/message-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('manager_login')


def get_message_date_of_customer(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        message_id = request.GET.get('message_id', None)
        user_id = request.GET.get('user_id', None)
        user = User.objects.get(id=user_id)
        message = Message.objects.get(id=message_id)
        data = {}
        try:
            message_record = MessageRecord.objects.get(message=message, user=user)
            data = {
                'date': message_record.send_date.strftime('%b %d, %Y'),
            }
        except:
            data = {
                'date': "-",
            }
        return JsonResponse(data, safe=False)
    else:
        return redirect('manager_login')


def message_customers(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        routes = user.routes.all()
        user_types = UserType.objects.all()
        message = Message.objects.get(id=id)
        return render(request, 'manager/message-customers.html', {'user':user, 'message':message, 'routes': routes, 'user_types':user_types, 'success':success, 'error':error})
    else:
        return redirect('manager_login')


def send_message_customers(request, id, uid):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        message = Message.objects.get(id=id)
        message_content = urllib.parse.quote_plus(message.content, safe='')

        user = User.objects.get(id=uid)
        try:
            message_record = MessageRecord.objects.get(message=message,user=user)
            message_record.send_date = timezone.localtime(timezone.now())
            message_record.save()
        except:
            message_record = MessageRecord(message=message, user=user)
            message_record.save()

        return redirect("https://api.whatsapp.com/send?phone=91" + user.mobile + "&text=" + message_content)
    else:
        return redirect('manager_login')




def route_ordering(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        user_routes = user.routes.all()
        routes = Route.objects.all()
        return render(request, 'manager/route-order.html', {'user':user, 'success':success, 'user_routes':user_routes, 'routes':routes})
    else:
        return redirect('manager_login')


def save_route_order(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        data = request.POST.get('data', None)
        data = json.loads(data)
        for d in data:
            user = User.objects.get(id=d['user_id'])
            user.route_order = int(d['route_order'])
            user.save()
        return JsonResponse({'success':True})
    else:
        return redirect('manager_login')


def get_customers_of_route(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        user = Manager.objects.get(id= user_id)
        route_id = request.GET.get('route', None)
        route = Route.objects.get(id=route_id)
        customers = User.objects.filter(route=route).order_by('route_order')
        customers = list(customers.values())
        for i in range(len(customers)):
            customer = User.objects.get(id=customers[i]['id'])
            customers[i]['assigned_to'] = ""
            if RouteAssign.objects.filter(user=customer).exists():
                assign = RouteAssign.objects.get(user=customer)
                customers[i]['assigned_to'] = assign.to_route.name
        return JsonResponse(customers, safe=False)
    else:
        return redirect('manager_login')


def change_customers_route(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        data = request.GET.get('data', None)
        data = json.loads(data)
        for d in data:
            user = User.objects.get(id=d['user_id'])
            route = Route.objects.get(id=d['route_id'])
            last_user_of_route = 0
            try:
                last_user_of_route = User.objects.filter(route=route).order_by('-route_order').first()
            except:
                pass
            user.route = route
            user.route_order = last_user_of_route.route_order + 1
            user.save()
        return JsonResponse({'success':True})
    else:
        return redirect('manager_login')


def assign_customers_route(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        data = request.GET.get('data', None)
        data = json.loads(data)
        for d in data:
            user = User.objects.get(id=d['user_id'])
            to_route = Route.objects.get(id=d['route_id'])
            try:
                assign = RouteAssign.objects.get(user=user)
                assign.to_route = to_route
                assign.save()
            except:
                assign = RouteAssign(from_route=user.route, to_route=to_route, user=user)
                assign.save()
        return JsonResponse({'success':True})
    else:
        return redirect('manager_login')


def clear_customers_route_assignation(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        data = request.GET.get('data', None)
        data = json.loads(data)
        for d in data:
            user = User.objects.get(id=d)
            try:
                assign = RouteAssign.objects.get(user=user)
                assign.delete()
            except:
                pass
        return JsonResponse({'success':True})
    else:
        return redirect('manager_login')


def clear_all_route_assignation(request):
    user_id = None
    try:
        user_id = request.session['farmfills_manager_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Manager.objects.filter(id= user_id).exists():
        route_id = request.GET.get('route_id', None)
        route = Route.objects.get(id=int(route_id))
        assigns = RouteAssign.objects.filter(from_route=route)
        for a in assigns:
            a.delete()
        return JsonResponse({'success':True})
    else:
        return redirect('manager_login')




def get_delivery_info(request):
    uid = request.GET.get('uid', None)
    user = User.objects.get(id=uid)

    subs = Subscription.objects.filter(user=user)
    vacations = Vacation.objects.filter(user=user)
    extras = ExtraLess.objects.filter(user=user)

    data = {
        'vacation': '',
        'subscription': '',
        'extraless': '',
        'next_delivery': '',
    }

    for s in subs:
        if s.end_date is None and s.start_date <= timezone.localtime(timezone.now()).date():
            data['subscription'] = getDataOfSub(s)
            break
        elif s.end_date is not None:
            if s.end_date > timezone.localtime(timezone.now()).date() and s.start_date <= timezone.localtime(timezone.now()).date():
                data['subscription'] = getDataOfSub(s)
                break
        elif s.start_date > timezone.localtime(timezone.now()).date():
            data['subscription'] = getDataOfSub(s)

    for v in vacations:
        if v.end_date is None and v.start_date <= timezone.localtime(timezone.now()).date():
            data['vacation'] = ' From ' + v.start_date.strftime('%d %b, %Y')
            break
        elif v.end_date is not None:
            if v.end_date > timezone.localtime(timezone.now()).date() and v.start_date <= timezone.localtime(timezone.now()).date():
                data['vacation'] = ' From ' + v.start_date.strftime('%d %b, %Y') + ' To ' + v.end_date.strftime('%d %b, %Y')
                break
        elif v.start_date > timezone.localtime(timezone.now()).date():
            data['vacation'] = ' From ' + v.start_date.strftime('%d %b, %Y')
            if v.end_date is not None:
                data['vacation'] += ' To ' + v.end_date.strftime('%d %b, %Y')
                
    for e in extras:
        if e.end_date is None and e.start_date <= timezone.localtime(timezone.now()).date():
            data['vacation'] = ' From ' + e.start_date.strftime('%d %b, %Y')
            break
        elif e.end_date is not None:
            if e.end_date > timezone.localtime(timezone.now()).date() and e.start_date <= timezone.localtime(timezone.now()).date():
                data['vacation'] = ' From ' + e.start_date.strftime('%d %b, %Y') + ' To ' + e.end_date.strftime('%d %b, %Y')
                break
        elif e.start_date > timezone.localtime(timezone.now()).date():
            data['vacation'] = ' From ' + e.start_date.strftime('%d %b, %Y')
            if e.end_date is not None:
                data['vacation'] += ' To ' + e.end_date.strftime('%d %b, %Y')
    
    next_delivery = getNextDelivery(subs, vacations, extras)
    if next_delivery is not None:
        data['next_delivery'] = next_delivery['date'] + ' ' + str(next_delivery['quantity']) + ' ltr'

    if data['vacation'] == '':
        data['vacation'] = 'Not Active'
    if data['subscription'] == '':
        data['subscription'] = 'Not Active'
    if data['extraless'] == '':
        data['extraless'] = 'Not Active'
    if data['next_delivery'] == '':
        data['next_delivery'] = 'NIL'

    return JsonResponse(data)