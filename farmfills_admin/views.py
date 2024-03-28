from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from users.models import Staff, User, Route, UserType, Purchase, Extra, Refund, Payment, Product, Subscription, Vacation, ExtraLess, RouteAssign, FollowUp, Message, MessageRecord, Manager
import json
from datetime import time, timedelta, datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core import serializers
from django.forms.models import model_to_dict
from .forms import UserForm, PaymentForm, RefundForm, ExtraForm, SubscriptionForm, ExtraLessForm, VacationForm, FollowUpForm, MessageForm, StaffForm, ManagerForm
import pytz
from django.utils import timezone
import urllib
from users.views import getEndBalanceOfMonth, last_day_of_month, getPurchaseOfMonth, getPaymentOfMonth, checkDateOverlaps, getNextDelivery, getPaymentDetails


# Create your views here.
def dashboard(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        return render(request, 'admin/index.html', {'user':user})
    else:
        return redirect('admin_login')


# login
def login(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        return redirect('admin_dashboard')
    return render(request, 'admin/login.html', {'error':error})


# validate login
def validate_admin_login(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        password = request.POST.get('password')
        if Staff.objects.filter(uname=uname, password=password, admin=True).exists():
            user = Staff.objects.get(uname=uname, password=password, admin=True)
            request.session['farmfills_staff_id'] = user.id
            return redirect('admin_dashboard')
        else:
            return redirect('/admin/login?error=1')
    return redirect('admin_login')


# delete customer
def customer_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        customer = User.objects.get(id=id)
        customer.delete()
        return redirect('/admin/customers/list?success=1')
    else:
        return redirect('admin_login')


# remove customer followup
def remove_customer_followup(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        followup = FollowUp.objects.get(id=id)
        followup.delete()
        return redirect('/admin/followup?success=2')
    else:
        return redirect('admin_login')


# delete message
def delete_message(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        message = Message.objects.get(id=id)
        message.delete()
        return redirect('/admin/message?success=2')
    else:
        return redirect('admin_login')


# remove all customer followup
def remove_all_customer_followup(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        FollowUp.objects.all().delete()
        return redirect('/admin/followup?success=2')
    else:
        return redirect('admin_login')


# delete extraless
def extraless_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        extraless = ExtraLess.objects.get(id=id)
        extraless.delete()
        return redirect('/admin/customers/extraless?success=2')
    else:
        return redirect('admin_login')


# delete vacation
def vacation_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        vacation = Vacation.objects.get(id=id)
        vacation.delete()
        return redirect('/admin/customers/vacations?success=2')
    else:
        return redirect('admin_login')


# delete payment
def payment_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        payment = Payment.objects.get(id=id)
        payment.delete()
        update_balance_of_customer(payment.user)
        return redirect('/admin/customers/transactions/payments?success=2')
    else:
        return redirect('admin_login')


# delete refund
def refund_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        refund = Refund.objects.get(id=id)
        refund.delete()
        update_balance_of_customer(refund.user)
        return redirect('/admin/customers/transactions/refunds?success=2')
    else:
        return redirect('admin_login')


# delete extra
def extra_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        extra = Extra.objects.get(id=id)
        extra.delete()
        update_balance_of_customer(extra.user)
        return redirect('/admin/customers/transactions/extras?success=2')
    else:
        return redirect('admin_login')


# delete subscription
def subscription_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        subscription = Subscription.objects.get(id=id)
        subscription.delete()
        return redirect('/admin/customers/subscriptions?success=2')
    else:
        return redirect('admin_login')


# end subscription
def subscription_end(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        subscription = Subscription.objects.get(id=id)
        if subscription.end_date is not None:
            if subscription.end_date <= timezone.localtime(timezone.now()).date():
                return redirect('/admin/customers/subscriptions?error=5')
        if subscription.start_date > timezone.localtime(timezone.now()).date():
            return redirect('/admin/customers/subscriptions?error=4')
        subscription.end_date = timezone.localtime(timezone.now()).date()
        subscription.save()
        return redirect('/admin/customers/subscriptions?success=3')
    else:
        return redirect('admin_login')


# end vacation
def vacation_end(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        vacation = Vacation.objects.get(id=id)
        if vacation.end_date is not None:
            if vacation.end_date <= timezone.localtime(timezone.now()).date():
                return redirect('/admin/customers/vacations?error=5')
        if vacation.start_date > timezone.localtime(timezone.now()).date():
            return redirect('/admin/customers/vacations?error=4')
        vacation.end_date = timezone.localtime(timezone.now()).date()
        vacation.save()
        return redirect('/admin/customers/vacations?success=3')
    else:
        return redirect('admin_login')

# end extraless
def extraless_end(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        eless = ExtraLess.objects.get(id=id)
        if eless.end_date is not None:
            if eless.end_date <= timezone.localtime(timezone.now()).date():
                return redirect('/admin/customers/extraless?error=5')
        if eless.start_date > timezone.localtime(timezone.now()).date():
            return redirect('/admin/customers/extraless?error=4')
        eless.end_date = timezone.localtime(timezone.now()).date()
        eless.save()
        return redirect('/admin/customers/extraless?success=3')
    else:
        return redirect('admin_login')


# logout
def logout(request):
    request.session['farmfills_staff_id'] = None
    return redirect('admin_login')

# customers list
def customers_list(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        user_types = UserType.objects.all()
        routes = Route.objects.all()
        return render(request, 'admin/customers-list.html', {'user':user, 'success':success, 'user_types':user_types, 'routes':routes})
    else:
        return redirect('admin_login')


# customers purchases
def customers_purchases(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        customers = User.objects.all()
        return render(request, 'admin/customers-purchase.html', {'user':user, 'success':success, 'customers':customers})
    else:
        return redirect('admin_login')


# route ordering
def route_ordering(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        routes = Route.objects.all()
        return render(request, 'admin/route-order.html', {'user':user, 'success':success, 'routes':routes})
    else:
        return redirect('admin_login')


# get customers of route ajax
def get_customers_of_route(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
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
        return redirect('admin_login')


# get customers of route ajax
def get_message_date_of_customer(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
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
        return redirect('admin_login')


# save route order ajax
def save_route_order(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        data = request.POST.get('data', None)
        data = json.loads(data)
        for d in data:
            user = User.objects.get(id=d['user_id'])
            user.route_order = int(d['route_order'])
            user.save()
        return JsonResponse({'success':True})
    else:
        return redirect('admin_login')


# assign customers to another route ajax
def assign_customers_route(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
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
        return redirect('admin_login')


# clear route assignation of customers ajax
def clear_customers_route_assignation(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
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
        return redirect('admin_login')


# clear all assignations of a route ajax
def clear_all_route_assignation(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        route_id = request.GET.get('route_id', None)
        route = Route.objects.get(id=int(route_id))
        assigns = RouteAssign.objects.filter(from_route=route)
        for a in assigns:
            a.delete()
        return JsonResponse({'success':True})
    else:
        return redirect('admin_login')


# change customers route
def change_customers_route(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
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
        return redirect('admin_login')


# customers payments
def customers_payments(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        customers = User.objects.all()
        return render(request, 'admin/customers-payment.html', {'user':user, 'success':success, 'customers':customers})
    else:
        return redirect('admin_login')


# customers refunds
def customers_refunds(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        customers = User.objects.all()
        return render(request, 'admin/customers-refund.html', {'user':user, 'success':success, 'customers':customers})
    else:
        return redirect('admin_login')


# customers subscriptions
def customer_subscriptions(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        customers = User.objects.all()
        return render(request, 'admin/customers-subscription.html', {'user':user, 'error':error, 'success':success, 'customers':customers})
    else:
        return redirect('admin_login')


# customers extraless
def customer_extraless(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        customers = User.objects.all()
        return render(request, 'admin/customers-extraless.html', {'user':user, 'error':error, 'success':success, 'customers':customers})
    else:
        return redirect('admin_login')


# customers vacation
def customer_vacations(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        customers = User.objects.all()
        return render(request, 'admin/customers-vacation.html', {'user':user, 'error':error, 'success':success, 'customers':customers})
    else:
        return redirect('admin_login')


# customers extras
def customers_extras(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        customers = User.objects.all()
        return render(request, 'admin/customers-extra.html', {'user':user, 'success':success, 'customers':customers})
    else:
        return redirect('admin_login')


# transaction list
def customer_transactions(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
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

        return render(request, 'admin/customer-transactions.html', {'user':user, 'success':success, 'customer':customer, 'transaction_data':transaction_data})
    else:
        return redirect('admin_login')


# managers list
def manager_list(request):
    success = request.GET.get('success', None)
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        routes = Route.objects.all()
        return render(request, 'admin/manager-list.html', {'user':user, 'routes':routes, 'success':success})
    else:
        return redirect('admin_login')


# staffs list
def staff_list(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        routes = Route.objects.all()
        return render(request, 'admin/staff-list.html', {'user':user, 'routes':routes})
    else:
        return redirect('admin_login')


# customers followup
def customers_followup(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        user_types = UserType.objects.all()
        routes = Route.objects.all()
        day = timezone.localtime(timezone.now()).replace(day=1)
        thismonth = day.strftime('%b')
        day -= timedelta(days=1)
        before1month = day.strftime('%b')
        day = day.replace(day=1) - timedelta(days=1)
        before2month = day.strftime('%b')
        return render(request, 'admin/customers-followup.html', {'user':user, 'thismonth':thismonth, 'before1month':before1month, 'before2month':before2month, 'user_types':user_types, 'routes':routes})
    else:
        return redirect('admin_login')


# followup
def followup(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        return render(request, 'admin/followup.html', {'user':user, 'success':success, 'error':error})
    else:
        return redirect('admin_login')


# message
def message(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        return render(request, 'admin/message.html', {'user':user, 'success':success, 'error':error})
    else:
        return redirect('admin_login')


# message customers
def message_customers(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        routes = Route.objects.all()
        user_types = UserType.objects.all()
        message = Message.objects.get(id=id)
        return render(request, 'admin/message-customers.html', {'user':user, 'message':message, 'routes': routes, 'user_types':user_types, 'success':success, 'error':error})
    else:
        return redirect('admin_login')


# send message customers
def send_message_customers(request, id, uid):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
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
        return redirect('admin_login')


# edit customer
def customers_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        customer = User.objects.get(id=id)
        form = UserForm(instance=customer)
        if request.method == 'POST':
            formset = UserForm(request.POST, request.FILES, instance=customer)
            if formset.is_valid():
                formset.save()
                return redirect('/admin/customers/edit/'+str(customer.id)+'?success=1')
        return render(request, 'admin/customers-edit.html', {'user':user, 'customer':customer, 'success':success, 'form':form})
    else:
        return redirect('admin_login')

        
# edit followup
def followup_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        followup = FollowUp.objects.get(id=id)
        form = FollowUpForm(instance=followup)
        if request.method == 'POST':
            formset = FollowUpForm(request.POST, request.FILES, instance=followup)
            if formset.is_valid():
                formset.save()
                return redirect('/admin/followup/edit/'+str(followup.id)+'?success=1')
        return render(request, 'admin/followup-edit.html', {'user':user, 'followup':followup, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# edit payment
def payments_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        payment = Payment.objects.get(id=id)
        form = PaymentForm(instance=payment)
        if request.method == 'POST':
            formset = PaymentForm(request.POST, request.FILES, instance=payment)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.paid = True
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/admin/payments/edit/'+str(payment.id)+'?success=1')
        return render(request, 'admin/payments-edit.html', {'user':user, 'payment':payment, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# edit refund
def refunds_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        refund = Refund.objects.get(id=id)
        form = RefundForm(instance=refund)
        if request.method == 'POST':
            formset = RefundForm(request.POST, request.FILES, instance=refund)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.amount = (formset.product.price + formset.user.user_type.price_variation) * formset.quantity
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/admin/refunds/edit/'+str(refund.id)+'?success=1')
        return render(request, 'admin/refunds-edit.html', {'user':user, 'refund':refund, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# edit extra
def extras_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        extra = Extra.objects.get(id=id)
        form = ExtraForm(instance=extra)
        if request.method == 'POST':
            formset = ExtraForm(request.POST, request.FILES, instance=extra)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.amount = (formset.product.price + formset.user.user_type.price_variation) * formset.quantity
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/admin/extras/edit/'+str(extra.id)+'?success=1')
        return render(request, 'admin/extras-edit.html', {'user':user, 'extra':extra, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# create customer
def customers_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = UserForm()
        if request.method == 'POST':
            formset = UserForm(request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save()
                if request.POST.get('continue-edit') == 'true':
                    id = formset.id
                    return redirect('/admin/customers/edit/'+str(id)+'?success=1')
                else:
                    return redirect('/admin/customers/create?success=1')
        return render(request, 'admin/customers-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# update balance
def update_balance_of_customer(user):

    transaction_data = []

    purchases = Purchase.objects.filter(user=user).order_by('-date', '-id')

    payments = Payment.objects.filter(user=user, paid=True).order_by('-date', '-id')

    refunds = Refund.objects.filter(user=user).order_by('-date', '-id')

    extras = Extra.objects.filter(user=user).order_by('-date', '-id')

    transaction_data = list(purchases) 

    transaction_data += list(payments)
    transaction_data += list(refunds)
    transaction_data += list(extras)

    transaction_data = sorted(transaction_data, key=lambda k: k.date, reverse=False)

    balance = 0

    for t in transaction_data:
        if t.get_transaction_type() == 'payment' or t.get_transaction_type() == 'refund':
            t.balance = balance + t.amount
            balance += t.amount
            t.save()
        elif t.get_transaction_type() == 'purchase' or t.get_transaction_type() == 'extra':
            t.balance = balance - t.amount
            balance -= t.amount
            t.save()


# edit subscription
def subscriptions_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        sub = Subscription.objects.get(id=id)

        status = get_status(sub)

        form = SubscriptionForm(instance=sub)
        if request.method == 'POST':
            formset = SubscriptionForm(request.POST, request.FILES, instance=sub)
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
                    return redirect(f'/admin/subscriptions/{id}?error=1')

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect(f'/admin/subscriptions/{id}?error=2')
                
                subs = Subscription.objects.filter(user=formset.user).exclude(id=id)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, subs):
                    return redirect(f'/admin/subscriptions/{id}?error=3')
                
                formset.edited_by = 'admin'

                formset.save()
                return redirect(f'/admin/subscriptions/{id}?success=1')
            return redirect(f'/admin/subscriptions/{id}')
        return render(request, 'admin/subscriptions-edit.html', {'user':user, 'status':status, 'success':success, 'form':form, 'error':error, 'subscription':sub})
    else:
        return redirect('admin_login')


# create subscription
def subscriptions_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = SubscriptionForm()
        if request.method == 'POST':
            formset = SubscriptionForm(request.POST, request.FILES)
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
                    return redirect('/admin/customers/subscriptions?error=1')

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect('/admin/customers/subscriptions?error=2')
                
                subs = Subscription.objects.filter(user=formset.user)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, subs):
                    return redirect('/admin/customers/subscriptions?error=3')

                formset.created_by = 'admin'
                formset.edited_by = 'admin'

                formset.save()
                return redirect('/admin/customers/subscriptions?success=1')
        return render(request, 'admin/subscriptions-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# create payment
def payments_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = PaymentForm()
        if request.method == 'POST':
            formset = PaymentForm(request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.balance = 0
                formset.paid = True
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/admin/customers/transactions/payments?success=1')
        return render(request, 'admin/payments-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# create message
def message_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = MessageForm()
        if request.method == 'POST':
            formset = MessageForm(request.POST, request.FILES)
            if formset.is_valid():
                formset.save()
                return redirect('/admin/message?success=1')
        return render(request, 'admin/message-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# create refund
def refunds_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = RefundForm()
        if request.method == 'POST':
            formset = RefundForm(request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.balance = 0
                formset.amount = (formset.product.price + formset.user.user_type.price_variation) * formset.quantity
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/admin/customers/transactions/refunds?success=1')
        return render(request, 'admin/refunds-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# create extra
def extras_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = ExtraForm()
        if request.method == 'POST':
            formset = ExtraForm(request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)
                formset.balance = 0
                formset.amount = (formset.product.price + formset.user.user_type.price_variation) * formset.quantity
                formset.save()
                update_balance_of_customer(formset.user)
                return redirect('/admin/customers/transactions/extras?success=1')
        return render(request, 'admin/extras-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# add followup customer
def add_followup_customer(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = FollowUpForm()
        if request.method == 'POST':
            formset = FollowUpForm(request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)
                if FollowUp.objects.filter(user=formset.user).exists():
                    return redirect('/admin/followup?error=1')
                formset.save()
                return redirect('/admin/followup?success=1')
        return render(request, 'admin/followup-add.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# create managers
def managers_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = ManagerForm()
        if request.method == 'POST':
            formset = ManagerForm(request.POST, request.FILES)
            if formset.is_valid():
                formset.save()

                return redirect('/admin/managers/create?success=1')
        return render(request, 'admin/managers-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# create staffs
def staffs_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = StaffForm()
        if request.method == 'POST':
            formset = StaffForm(request.POST, request.FILES)
            if formset.is_valid():
                formset.save()

                return redirect('/admin/staffs/create?success=1')
        return render(request, 'admin/staffs-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# edit managers
def managers_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        manager = Manager.objects.get(id=id)
        form = ManagerForm(instance=manager)
        if request.method == 'POST':
            formset = ManagerForm(request.POST, request.FILES, instance=manager)
            if formset.is_valid():
                formset.save()

                return redirect(f'/admin/managers/edit/{id}?success=1')
        return render(request, 'admin/managers-create.html', {'manager':manager, 'user':user, 'success':success, 'form':form, 'edit':True})
    else:
        return redirect('admin_login')


# edit staffs
def staffs_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        staff = Staff.objects.get(id=id)
        form = StaffForm(instance=staff)
        if request.method == 'POST':
            formset = StaffForm(request.POST, request.FILES, instance=staff)
            if formset.is_valid():
                formset.save()

                return redirect(f'/admin/staffs/edit/{id}?success=1')
        return render(request, 'admin/staffs-create.html', {'staff':staff, 'user':user, 'success':success, 'form':form, 'edit':True})
    else:
        return redirect('admin_login')


# delete manager
def manager_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        manager = Manager.objects.get(id=id)
        manager.delete()
        return redirect('/admin/managers/list?success=1')
    else:
        return redirect('admin_login')


# delete staff
def staff_delete(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        staff = Staff.objects.get(id=id)
        staff.delete()
        return redirect('/admin/staffs/list?success=1')
    else:
        return redirect('admin_login')


# create extraless
def extraless_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = ExtraLessForm()
        if request.method == 'POST':
            formset = ExtraLessForm(request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect('/admin/customers/extraless?error=2')
                
                extralesses = ExtraLess.objects.filter(user=formset.user)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, extralesses):
                    return redirect('/admin/customers/extraless?error=3')

                formset.created_by = 'admin'
                formset.edited_by = 'admin'

                formset.save()

                return redirect('/admin/customers/extraless?success=1')
        return render(request, 'admin/extraless-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# edit extraless
def extraless_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        eless = ExtraLess.objects.get(id=id)

        status = get_status(eless)

        form = ExtraLessForm(instance=eless)
        if request.method == 'POST':
            formset = ExtraLessForm(request.POST, request.FILES, instance=eless)
            if formset.is_valid():
                formset = formset.save(commit=False)

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect(f'/admin/extraless/{id}?error=2')
                
                extralesses = ExtraLess.objects.filter(user=formset.user).exclude(id=id)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, extralesses):
                    return redirect(f'/admin/extraless/{id}?error=3')
                
                formset.edited_by = 'admin'

                formset.save()

                return redirect(f'/admin/extraless/{id}?success=1')
        return render(request, 'admin/extraless-edit.html', {'user':user, 'error':error, 'success':success, 'status':status, 'extraless':eless, 'form':form})
    else:
        return redirect('admin_login')


# create vacation
def vacations_create(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        form = VacationForm()
        if request.method == 'POST':
            formset = VacationForm(request.POST, request.FILES)
            if formset.is_valid():
                formset = formset.save(commit=False)

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect('/admin/customers/vacations?error=2')
                
                vacations = Vacation.objects.filter(user=formset.user)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, vacations):
                    return redirect('/admin/customers/vacations?error=3')
                
                formset.created_by = 'admin'
                formset.edited_by = 'admin'

                formset.save()

                return redirect('/admin/customers/vacations?success=1')
        return render(request, 'admin/vacations-create.html', {'user':user, 'success':success, 'form':form})
    else:
        return redirect('admin_login')


# edit vacation
def vacations_edit(request, id):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        vac = Vacation.objects.get(id=id)

        status = get_status(vac)

        form = VacationForm(instance=vac)
        if request.method == 'POST':
            formset = VacationForm(request.POST, request.FILES, instance=vac)
            if formset.is_valid():
                formset = formset.save(commit=False)

                if formset.end_date is not None:
                    if formset.end_date < formset.start_date:
                        return redirect(f'/admin/vacations/{id}?error=2')
                
                vacations = Vacation.objects.filter(user=formset.user).exclude(id=id)
                end_date = formset.end_date
                if end_date is not None:
                    end_date = end_date.strftime('%d/%m/%Y')
                if checkDateOverlaps(formset.start_date.strftime('%d/%m/%Y'), end_date, vacations):
                    return redirect(f'/admin/vacations/{id}?error=3')
                
                formset.edited_by = 'admin'

                formset.save()

                return redirect(f'/admin/vacations/{id}?success=1')
        return render(request, 'admin/vacations-edit.html', {'user':user, 'error':error, 'success':success, 'status':status, 'form':form, 'vacation':vac})
    else:
        return redirect('admin_login')



# payments report
def payments_report(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    success = request.GET.get('success', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        user = Staff.objects.get(id=user_id, admin=True)
        routes = Route.objects.all()
        return render(request, 'admin/payments-report.html', {'user':user, 'routes': routes, 'success':success})
    else:
        return redirect('admin_login')



# data table ajax for customers list
@ csrf_exempt
def admin_datatable_ajax_customers_list(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
        if filterByUserType == 'none' or filterByRoute == '':
            query += " and (user_type_id IS NULL)"
        elif filterByUserType != 'all':
            query += " and (user_type_id=" + filterByUserType + ")"
        
        # payment mode filter
        filterByPaymentMode = request.POST.get('filterByPaymentMode')
        if filterByPaymentMode == 'none' or filterByPaymentMode == '':
            query += " and (payment_mode IS NULL)"
        elif filterByPaymentMode != 'all':
            query += " and (payment_mode='" + filterByPaymentMode + "')"
            
        # total of filtered record
        totalRecordwithFilter = User.objects.raw('SELECT * FROM users_user WHERE true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = User.objects.all().count()

        # filtered records
        if columnName is not None:
            query_data = User.objects.raw('SELECT * FROM users_user WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = User.objects.raw('SELECT * FROM users_user WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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


# data table ajax for customers subscriptions
@ csrf_exempt
def admin_datatable_ajax_customers_subscriptions(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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

        # subscription type filter
        filterBySubType = request.POST.get('filterBySubType')
        if filterBySubType != 'all':
            query += " and (sub_type='" + filterBySubType + "')"
            
        # total of filtered record
        totalRecordwithFilter = Subscription.objects.raw('SELECT * FROM users_subscription WHERE true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Subscription.objects.all().count()

        # filtered records
        if columnName is not None:
            query_data = Subscription.objects.raw('SELECT * FROM users_subscription WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Subscription.objects.raw('SELECT * FROM users_subscription WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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
        return redirect('admin_login')


# data table ajax for customers extraless
@ csrf_exempt
def admin_datatable_ajax_customers_extraless(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
        totalRecordwithFilter = ExtraLess.objects.raw('SELECT * FROM users_extraless WHERE true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = ExtraLess.objects.all().count()

        # filtered records
        if columnName is not None:
            query_data = ExtraLess.objects.raw('SELECT * FROM users_extraless WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = ExtraLess.objects.raw('SELECT * FROM users_extraless WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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
        return redirect('admin_login')


# data table ajax for customers vacations
@ csrf_exempt
def admin_datatable_ajax_customers_vacations(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
        totalRecordwithFilter = Vacation.objects.raw('SELECT * FROM users_vacation WHERE true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Vacation.objects.all().count()

        # filtered records
        if columnName is not None:
            query_data = Vacation.objects.raw('SELECT * FROM users_vacation WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Vacation.objects.raw('SELECT * FROM users_vacation WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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
        return redirect('admin_login')



# data table ajax for customers purchases
@ csrf_exempt
def admin_datatable_ajax_customers_purchases(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
        totalRecordwithFilter = Purchase.objects.raw('SELECT * FROM users_purchase WHERE true' + query)
        totalRecordwithFilter = len(list(totalRecordwithFilter))

        # total records
        totalRecords = Purchase.objects.all().count()

        # filtered records
        if columnName is not None:
            query_data = Purchase.objects.raw('SELECT * FROM users_purchase WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Purchase.objects.raw('SELECT * FROM users_purchase WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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
        return redirect('admin_login')


# data table ajax for customers extras
@ csrf_exempt
def admin_datatable_ajax_customers_extras(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
        totalRecordwithFilter = Extra.objects.raw('SELECT * FROM users_extra WHERE true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Extra.objects.all().count()

        # filtered records
        if columnName is not None:
            query_data = Extra.objects.raw('SELECT * FROM users_extra WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Extra.objects.raw('SELECT * FROM users_extra WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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
        return redirect('admin_login')



# data table ajax for customers refunds
@ csrf_exempt
def admin_datatable_ajax_customers_refunds(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
        totalRecordwithFilter = Refund.objects.raw('SELECT * FROM users_refund WHERE true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Refund.objects.all().count()

        # filtered records
        if columnName is not None:
            query_data = Refund.objects.raw('SELECT * FROM users_refund WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Refund.objects.raw('SELECT * FROM users_refund WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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
        return redirect('admin_login')



# data table ajax for customers payments
@ csrf_exempt
def admin_datatable_ajax_customers_payments(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
        totalRecordwithFilter = Payment.objects.raw('SELECT * FROM users_payment WHERE paid=true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Payment.objects.filter(paid=True).count()

        # filtered records
        if columnName is not None:
            query_data = Payment.objects.raw('SELECT * FROM users_payment WHERE paid=true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Payment.objects.raw('SELECT * FROM users_payment WHERE paid=true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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
        return redirect('admin_login')


# data table ajax for payments report
@ csrf_exempt
def admin_datatable_ajax_payments_report(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
        # datatable variables
        draw = request.POST.get('draw')
        row = request.POST.get('start')
        rowperpage = request.POST.get('length')
        columnIndex = request.POST.get('order[0][column]', None)
        columnName = request.POST.get('columns[' + columnIndex + '][data]', None)
        columnSortOrder = request.POST.get('order[0][dir]', None)

        query = ""
        
        # mode filter
        filterByMode = request.POST.get('filterByMode')
        if filterByMode != 'all':
            query += " and (mode='" + filterByMode + "')"

        # route filter
        filterByRoute = request.POST.get('filterByRoute')
        if filterByRoute != 'all':
            query += " and (u.route_id='" + filterByRoute + "')"


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
        totalRecordwithFilter = Payment.objects.raw('SELECT * FROM users_payment p INNER JOIN users_user u ON p.user_id = u.id WHERE p.paid=true' + query)        
        totalAmount = 0
        totalFees = 0
        for q in totalRecordwithFilter:
            totalAmount += q.amount
            if q.payment_id:
                fees = getPaymentDetails(q.payment_id)['fee'] / 100
                totalFees += fees
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Payment.objects.filter(paid=True).count()

        # filtered records
        if columnName is not None:
            query_data = Payment.objects.raw('SELECT * FROM users_payment p INNER JOIN users_user u ON p.user_id = u.id WHERE p.paid=true' + query + ' ORDER BY p.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Payment.objects.raw('SELECT * FROM users_payment p INNER JOIN users_user u ON p.user_id = u.id WHERE p.paid=true' + query + ' ORDER BY p.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')

        data = []
        for q in query_data:
            user = User.objects.get(id=q.user_id)
            data.append({'id':q.id, 'name':user.name + ' ' + user.delivery_name, 'date':timezone.localtime(q.date).strftime('%d %b, %Y'), 'amount':str(q.amount), 'mode':q.mode, 'description':q.description})

        # response
        response = {
            "draw" : int(draw),
            "iTotalRecords" : totalRecords,
            "iTotalDisplayRecords" : totalRecordwithFilter,
            "aaData" : data,
            "totalAmount" : totalAmount,
            "totalFees" : totalFees,
            "netIncome" : float(totalAmount) - totalFees,
        }
        return JsonResponse(response)
    else:
        return redirect('admin_login')



# data table ajax for followup
@ csrf_exempt
def admin_datatable_ajax_followup(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
            query += " INNER JOIN users_user b ON (a.user_id = b.id) WHERE (LOWER(b.name) like '%%" + searchValue + "%%' or LOWER(b.delivery_name) like '%%" + searchValue + "%%' or b.mobile like '%%" + searchValue + "%%' )"

        # next follow up date filter
        filterByNextDate = request.POST.get('filterByNextDate')
        if filterByNextDate != '' and filterByNextDate is not None:
            filterByNextDate = timezone.make_aware(datetime.strptime(filterByNextDate, '%Y-%m-%d')).date()
            if query == "":
                query += "WHERE (next_date >= '" + str(filterByNextDate) + "')"
            else:
                query += " and (next_date >= '" + str(filterByNextDate) + "')"

            
        # total of filtered record
        totalRecordwithFilter = 0
        if searchValue is None and searchValue == '':
            totalRecordwithFilter = FollowUp.objects.raw('SELECT * FROM users_followup WHERE true' + query)
        else:
            totalRecordwithFilter = FollowUp.objects.raw('SELECT * FROM users_followup a ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = FollowUp.objects.all().count()

        # filtered records
        if columnName is not None:
            if searchValue is None and searchValue == '':
                query_data = FollowUp.objects.raw('SELECT * FROM users_followup WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
            else:
                query_data = FollowUp.objects.raw('SELECT * FROM users_followup a ' + query + ' ORDER BY a.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            if searchValue is None and searchValue == '':
                query_data = FollowUp.objects.raw('SELECT * FROM users_followup WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
            else:
                query_data = FollowUp.objects.raw('SELECT * FROM users_followup a ' + query + ' ORDER BY a.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            user = User.objects.get(id=q.user_id)
            next_date = '-'
            if q.next_date is not None:
                next_date = q.next_date.strftime('%d %b, %Y')
            data.append({'id':q.id, 'name':user.name + ' ' + user.delivery_name, 'next_date':next_date, 'note':q.note, 'admin_note':q.admin_note})

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

    
# data table ajax for messages
@ csrf_exempt
def admin_datatable_ajax_message(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
        return redirect('admin_login')



# data table ajax for managers
@ csrf_exempt
def admin_datatable_ajax_managers(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
            query += " and (LOWER(m.name) like '%%" + searchValue + "%%' or LOWER(m.uname) like '%%" + searchValue + "%%' )"
        
        # route filter
        filterByRoute = request.POST.get('filterByRoute')
        if filterByRoute != 'all':
            query += " and (r.id=" + filterByRoute + ")"


        # total of filtered record
        totalRecordwithFilter = Manager.objects.raw('SELECT DISTINCT m.id, m.name, m.uname, m.password FROM users_manager m INNER JOIN users_manager_routes mr ON m.id = mr.manager_id INNER JOIN users_route r ON mr.route_id = r.id WHERE true ' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = Manager.objects.all().count()

        # filtered records
        if columnName is not None:
            query_data = Manager.objects.raw('SELECT DISTINCT m.id, m.name, m.uname, m.password FROM users_manager m INNER JOIN users_manager_routes mr ON m.id = mr.manager_id INNER JOIN users_route r ON mr.route_id = r.id WHERE true ' + query + ' ORDER BY m.' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Manager.objects.raw('SELECT DISTINCT m.id, m.name, m.uname, m.password FROM users_manager m INNER JOIN users_manager_routes mr ON m.id = mr.manager_id INNER JOIN users_route r ON mr.route_id = r.id WHERE true ' + query + ' ORDER BY m.id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            routes = ", ".join(val.name for val in q.routes.all())


            data.append({
                'id':q.id,
                'name':q.name,
                'uname':q.uname, 
                'password':q.password, 
                'routes':routes,
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



# data table ajax for staffs
@ csrf_exempt
def admin_datatable_ajax_staffs(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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
            query += " and (LOWER(name) like '%%" + searchValue + "%%' or LOWER(uname) like '%%" + searchValue + "%%' )"
        
        # route filter
        filterByRoute = request.POST.get('filterByRoute')
        if filterByRoute == 'none' or filterByRoute == '':
            query += " and (route_id IS NULL)"
        elif filterByRoute != 'all':
            query += " and (route_id=" + filterByRoute + ")"

        # user position filter
        filterByPosition = request.POST.get('filterByPosition')
        if filterByPosition == 'none' or filterByPosition == '':
            pass
        elif filterByPosition != 'all':
            query += " and (" + filterByPosition + "=TRUE)"


        # total of filtered record
        totalRecordwithFilter = Staff.objects.raw('SELECT * FROM users_staff WHERE true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = len(Staff.objects.all())

        # filtered records
        if columnName is not None:
            query_data = Staff.objects.raw('SELECT * FROM users_staff WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = Staff.objects.raw('SELECT * FROM users_staff WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
        data = []
        for q in query_data:
            route = "-"
            if q.route is not None:
                route = q.route.name
            km = "-"
            if q.km is not None:
                km = q.km
            vehicle = "-"
            if q.vehicle is not None:
                vehicle = q.vehicle
            position = ""
            if q.delivery == True: position += 'delivery, '
            if q.dispatch == True: position += 'dispatch, '
            if q.cash_collection == True: position += 'cash collection, '
            if q.follow_up == True: position += 'follow up, '
            if q.billing == True: position += 'billing, '
            if q.admin == True: position += 'admin, '
            if q.vendor == True: position += 'vendor, '
            position = position[:-2]

            data.append({
                'id':q.id,
                'name':q.name,
                'uname':q.uname, 
                'password':q.password, 
                'position':position, 
                'route':route, 
                'km':km, 
                'vehicle':vehicle,
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


# data table ajax for customers followup
@ csrf_exempt
def admin_datatable_ajax_customers_followup(request):
    user_id = None
    try:
        user_id = request.session['farmfills_staff_id']
    except:
        pass
    error = request.GET.get('error', None)
    if Staff.objects.filter(id=user_id, admin=True).exists():
        
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

        # payment mode filter
        filterByPaymentMode = request.POST.get('filterByPaymentMode')
        if filterByPaymentMode == 'none' or filterByPaymentMode == '':
            query += " and (payment_mode IS NULL)"
        elif filterByPaymentMode != 'all':
            query += " and (payment_mode='" + filterByPaymentMode + "')"

        # bill notification filter
        filterByBillNotification = request.POST.get('filterByBillNotification')
        if filterByBillNotification == 'sent':
            query += " and (EXTRACT(MONTH FROM bill_send_date)=" + timezone.localtime(timezone.now()).strftime('%m') + " and EXTRACT(YEAR FROM bill_send_date)=" + timezone.localtime(timezone.now()).strftime('%Y') + ")"
        elif filterByBillNotification == 'not sent':
            query += " and (EXTRACT(MONTH FROM bill_send_date) !=" + timezone.localtime(timezone.now()).strftime('%m') + " or EXTRACT(YEAR FROM bill_send_date) !=" + timezone.localtime(timezone.now()).strftime('%Y') + " or bill_send_date IS NULL)"

        filterCustomers = []

        customers = User.objects.all()
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
        totalRecordwithFilter = User.objects.raw('SELECT * FROM users_user WHERE true' + query)
        totalRecordwithFilter = sum(1 for result in totalRecordwithFilter)

        # total records
        totalRecords = len(customers)

        # filtered records
        if columnName is not None:
            query_data = User.objects.raw('SELECT * FROM users_user WHERE true' + query + ' ORDER BY ' + columnName + ' ' + columnSortOrder + ' LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        else:
            query_data = User.objects.raw('SELECT * FROM users_user WHERE true' + query + ' ORDER BY id LIMIT ' + rowperpage + ' OFFSET ' + row + ';')
        
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


# get customer delivery info
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


# get customer purchase info
def get_purchase_info(request):
    uid = request.GET.get('uid', None)
    date = request.GET.get('date', None)
    user = User.objects.get(id=uid)
    date = timezone.make_aware(datetime.strptime(date, '%Y-%m-%d')).date()

    data = []

    purchases = Purchase.objects.filter(user=user, date__contains=date)
    extras = Extra.objects.filter(user=user, date__contains=date)
    
    for p in purchases:
        exist = False

        for d in data:
            if d['product'] == p.product:
                d['amount'] += p.amount
                d['quantity'] += p.quantity
                exist = True
                break
        
        if not exist:
            data.append({'product':p.product, 'amount':p.amount, 'quantity':p.quantity, 'date':date.strftime('%d %b, %Y')})
    
    for e in extras:
        exist = False

        for d in data:
            if d['product'] == p.product:
                d['amount'] += p.amount
                d['quantity'] += p.quantity
                exist = True
                break
        
        if not exist:
            data.append({'product':p.product, 'amount':p.amount, 'quantity':p.quantity, 'date':timezone.localtime(date).strftime('%d %b, %Y')})

    for i in range(len(data)):
        data[i]['product'] = model_to_dict(data[i]['product'])

    return JsonResponse(data, safe=False)


# get string data from subscription
def getDataOfSub(sub):
    output = ''
    if sub.sub_type == 'daily':
        output = 'Daily ' + str(sub.daily_day1)
        if sub.daily_day2 is not None and sub.sub_type == 0:
            output += ' and ' + str(sub.daily_day2)
        output += ' ltr'
    elif sub.sub_type == 'alternate':
        output = 'Alternate ' + str(sub.alternate_quantity )+ ' ltr'
    elif sub.sub_type == 'custom':
        output = str(sub.custom_quantity) + ' ltr in every ' + str(sub.custom_interval) + ' days'
    elif sub.sub_type == 'weekly':
        output = 'Weekly Mon: ' + str(sub.weekly_mon) + ' Tue: ' + str(sub.weekly_tue) + ' Wed: ' + str(sub.weekly_wed) + ' Thu: ' + str(sub.weekly_thu) + ' Fri: ' + str(sub.weekly_fri) + ' Sat: ' + str(sub.weekly_sat) + ' Sun: ' + str(sub.weekly_sun)
    
    output += ' From ' + sub.start_date.strftime('%d %b, %Y')
    if sub.end_date is not None:
        output += ' To ' + sub.end_date.strftime('%d %b, %Y')
    
    return output


# get status as upcoming or active or completed
def get_status(item):
    status = ''
    if item.start_date > timezone.localtime(timezone.now()).date():

        status = 'upcoming'

    elif (item.start_date <= timezone.localtime(timezone.now()).date() and item.end_date is None ) or (item.start_date <= timezone.localtime(timezone.now()).date() and item.end_date > timezone.localtime(timezone.now()).date()):

        status = 'active'

    elif item.start_date <= timezone.localtime(timezone.now()).date() and item.end_date <= timezone.localtime(timezone.now()).date():

        status = 'completed'
    
    return status
