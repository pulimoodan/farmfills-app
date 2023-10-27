from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import http.client
import math as m
import random as r
from .models import Payment, Purchase, Refund, Extra, User, Otp, UserType, Route, Subscription, Vacation, ExtraLess, Product
import json
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from django.db.models import Q
import razorpay
from django.views.decorators.csrf import csrf_exempt
import requests
from decimal import Decimal
import re
from django.conf import settings


# login view
def login(request):

    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        return redirect('/')

    if request.method == 'POST':

        type = request.POST.get('type')

        if type == 'mobile':

            mobile = request.POST.get('mobile')

            mobile = mobile.replace(" ", "")

            if not User.objects.filter(mobile=mobile).exists():

                return render(request, 'login.html', {'type': 'mobile', 'mobile': mobile, 'error':1 })

            otp_num = generateOTP()

            conn = http.client.HTTPSConnection("api.msg91.com")
            payload = "{\"otp\":" + otp_num + "}"
            headers = { 'content-type': "application/json" }
            conn.request("GET", "/api/v5/otp?template_id=" + settings.ENV('MSG91_OTP_TEMPLATE_ID') + "&mobile=91" + mobile + "&authkey=" + settings.ENV('MSG91_AUTH_KEY'), payload, headers)
            res = conn.getresponse()
            data = res.read()
            print(data.decode("utf-8"))

            try:
                otp = Otp.objects.get(mobile= mobile)
                otp.otp = otp_num
                otp.save()
            except:
                otp = Otp(mobile= mobile, otp= otp_num)
                otp.save()

            return render(request, 'login.html', {'type': 'otp', 'mobile': mobile, 'error':0 })
        
        elif type == 'otp':

            mobile = request.POST.get('mobile')

            mobile = " ".join(mobile.split())

            input_otp = request.POST.get('digit-1') + request.POST.get('digit-2') + request.POST.get('digit-3') + request.POST.get('digit-4')

            if Otp.objects.filter(mobile= mobile, otp= input_otp).exists():

                Otp.objects.filter(mobile= mobile).update(ip=get_client_ip(request))

                request.session['farmfills_user_id'] = User.objects.get(mobile=mobile).id

                return redirect('/')
            
            else:

                return render(request, 'login.html', {'type': 'otp', 'mobile': mobile, 'error': 1})
        
        elif type == 'resend_otp':

            mobile = request.POST.get('mobile')

            mobile = " ".join(mobile.split())

            otp_num = generateOTP()

            conn = http.client.HTTPSConnection("api.msg91.com")
            payload = "{\"otp\":" + otp_num + "}"
            headers = { 'content-type': "application/json" }
            conn.request("GET", "/api/v5/otp?template_id=" + settings.ENV('MSG91_OTP_TEMPLATE_ID') + "&mobile=91" + str(mobile) + "&authkey=" + settings.ENV('MSG91_AUTH_KEY'), payload, headers)
            res = conn.getresponse()
            data = res.read()
            print(data.decode("utf-8"))

            try:
                otp = Otp.objects.get(mobile= mobile)
                otp.otp = otp_num
                otp.save()
            except:
                otp = Otp(mobile= mobile, otp= otp_num)
                otp.save()

            return render(request, 'login.html', {'type': 'otp', 'mobile': mobile, 'error':2 })

    return render(request, 'login.html', {'type': 'mobile'})


register_data = {'name': '', 'start_date': ''}

def register(request):

    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        return redirect('/')

    users = User.objects.all()

    if request.method == "POST":

        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        sub_type = request.POST.get('sub_type')
        daily_different_alternative = request.POST.get('daily_different_alternative')
        daily_day1 = 0
        daily_day2 = 0
        alternate_quantity = 0
        weekly_mon = 0
        weekly_tue = 0
        weekly_wed = 0
        weekly_thu = 0
        weekly_fri = 0
        weekly_sat = 0
        weekly_sun = 0
        custom_quantity = 0
        custom_interval = 0

        if sub_type == 'daily':
            daily_day1 = request.POST.get('daily_day1')
            if daily_different_alternative == 'true':
                daily_day2 = request.POST.get('daily_day2')
        elif sub_type == 'alternate':
            alternate_quantity = request.POST.get('alternate_quantity')
        elif sub_type == 'custom':
            custom_quantity = request.POST.get('custom_quantity')
            custom_interval = request.POST.get('custom_interval')
        elif sub_type == 'weekly':
            weekly_mon = request.POST.get('weekly_mon')
            weekly_tue = request.POST.get('weekly_tue')
            weekly_wed = request.POST.get('weekly_wed')
            weekly_thu = request.POST.get('weekly_thu')
            weekly_fri = request.POST.get('weekly_fri')
            weekly_sat = request.POST.get('weekly_sat')
            weekly_sun = request.POST.get('weekly_sun')
            
        address_type = request.POST.get('address_type')
        house_name = request.POST.get('house_name')
        house_no = request.POST.get('house_no')
        house_street = request.POST.get('house_street')
        house_landmark = request.POST.get('house_landmark')
        apartment_name = request.POST.get('apartment_name')
        apartment_tower = request.POST.get('apartment_tower')
        apartment_floor = request.POST.get('apartment_floor')
        apartment_door = request.POST.get('apartment_door')
        mobile = request.POST.get('mobile')
        otp = request.POST.get('digit-1') + request.POST.get('digit-2') + request.POST.get('digit-3') + request.POST.get('digit-4')

        delivery_name = [name, house_name, house_no, house_street, house_landmark, apartment_name, apartment_tower, apartment_floor, apartment_door]
        delivery_name = [i for i in delivery_name if i is not None]
        delivery_name = " ".join(delivery_name)

        if Otp.objects.filter(mobile= mobile, otp= otp).exists():
            user = User(
                name=name, 
                address_type=address_type, 
                house_name=house_name, 
                house_no=house_no, 
                street=house_street, 
                landmark=house_landmark,
                apartment_name=apartment_name,
                tower=apartment_tower,
                floor=apartment_floor,
                door=apartment_door,
                mobile=mobile,
                email="",
                route=Route.objects.get(id=1),
                route_order=0,
                user_type=UserType.objects.get(id=1),
                payment_mode='online',
                delivery_name = delivery_name
            )
            user.save()
            subscription = Subscription(
                user = user,
                start_date = convertToDateTime(start_date),
                sub_type = sub_type,
                daily_day1 = daily_day1,
                daily_day2 = daily_day2,
                custom_interval = custom_interval,
                custom_quantity = custom_quantity,
                alternate_quantity = alternate_quantity,
                weekly_mon = weekly_mon,
                weekly_tue = weekly_tue,
                weekly_wed = weekly_wed,
                weekly_thu = weekly_thu,
                weekly_fri = weekly_fri,
                weekly_sat = weekly_sat,
                weekly_sun = weekly_sun
            )
            subscription.save()
            Otp.objects.filter(mobile= mobile).update(ip=get_client_ip(request))
            request.session['farmfills_user_id'] = User.objects.get(mobile=mobile).id
            return redirect('/')
        else:
            return render(request, 'register.html', {'error': 1})

    return render(request, 'register.html', {'error': 0})


# convert date to datetime format
def convertToDateTime(date):
    if date is None:
        return None
    else:
        date = date.split('/')
        date = datetime(int(date[2]), int(date[1]), int(date[0]), tzinfo=pytz.UTC)
        return date


# home
def home(request):

    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        payments = Payment.objects.filter(user=user, paid=True)

        extras = Extra.objects.filter(user=user)

        purchases = Purchase.objects.filter(user=user)

        refunds = Refund.objects.filter(user=user)

        products = Product.objects.all()

        subscriptions = Subscription.objects.filter(user=user)
        vacations = Vacation.objects.filter(user=user)
        extraless = ExtraLess.objects.filter(user=user)

        active_sub = 'Not active'

        for i in subscriptions:
            if (i.start_date <= timezone.localtime(timezone.now()).date() and i.end_date is None ) or (i.start_date <= timezone.localtime(timezone.now()).date() and i.end_date > timezone.localtime(timezone.now()).date()):
                active_sub = i.sub_type
                if i.sub_type == 'alternate':
                    quantity = str(i.alternate_quantity).rstrip('0').rstrip('.') if '.' in str(i.alternate_quantity) else str(i.alternate_quantity)
                    active_sub += " "+ quantity + " ltr"
                elif i.sub_type == 'daily':
                    quantity1 = str(i.daily_day1).rstrip('0').rstrip('.') if '.' in str(i.daily_day1) else str(i.daily_day1)
                    quantity2 = str(i.daily_day2).rstrip('0').rstrip('.') if '.' in str(i.daily_day2) else str(i.daily_day2)
                    if i.daily_day2 == 0:
                        active_sub += " "+ quantity1 + " ltr"
                    else:
                        active_sub += " " + quantity1 + "/" + quantity2 + " ltr"
        
        active_vacation = 'Not active'
        for v in vacations:
            if v.end_date is None or v.end_date > timezone.localtime(timezone.now()).date():
                active_vacation = "From " + v.start_date.strftime("%b %d")
                break
        
        active_sub = active_sub.capitalize()

        next_delivery_date =  getNextDeliveryDate(subscriptions, vacations, extraless)

        last_day = last_day_of_month(timezone.localtime(timezone.now()))

        if user.user_type.payment_type == 'postpaid':

            last_day = timezone.localtime(timezone.now()).replace(day=1)
            last_day = last_day - timedelta(days=1)

        balance = getEndBalanceOfMonth(last_day, user)

        if user.user_type.payment_type == 'postpaid':

            balance += getPaymentOfMonth(timezone.localtime(timezone.now()), user)

        upcoming_days = getUpcomingDays(subscriptions, vacations, extraless)

        upcoming_days = json.dumps(upcoming_days)

        return render(request, 'home.html', {'user': user, 'balance': balance, 'next_delivery_date': next_delivery_date, 'active_sub': active_sub, 'active_vacation':active_vacation, 'upcoming_days':upcoming_days})

    else:

        return redirect('login')


# get the past 15 days history
def history(request):
    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        extras = Extra.objects.filter(user=user)

        purchases = Purchase.objects.filter(user=user)

        refunds = Refund.objects.filter(user=user)

        historyList = []

        for i in range(15):
            date = (timezone.localtime(timezone.now()) - timedelta(days=i)).date()

            added = False

            for p in purchases:
                if p.date.date() == date:
                    historyList.append({'date':date.strftime("%b %d"), 'amount':str(p.amount), 'quantity':str(p.quantity), 'status':'delivered'})
                    added = True
                    break

            for e in extras:
                if e.date.date() == date:
                    if added:
                        historyList[len(historyList)-1]['amount'] = str(Decimal(historyList[len(historyList)-1]['amount']) + e.amount)
                        historyList[len(historyList)-1]['quantity'] = str(Decimal(historyList[len(historyList)-1]['quantity']) + e.quantity)
                        added = True
                        break
                    else:
                        historyList.append({'date':date.strftime("%b %d"), 'amount':str(e.amount), 'quantity':str(e.quantity), 'status':'delivered'})
                        added = True
                        break

            for r in refunds:
                r.date = timezone.localtime(r.date)
                if r.date.date() == date:
                    historyList.append({'date':date.strftime("%b %d"), 'amount':str(r.amount), 'quantity':str(r.quantity), 'status':'refunded'})
                    added = True
                    break
            
            if not added:
                historyList.append({'date':date.strftime("%b %d"), 'amount':'0', 'quantity':'0', 'status':'vacation'})
        
        
        return render(request, 'history.html', {'user': user, 'historyList': historyList})

    else:

        return redirect('login')



# account
def account(request):

    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass

    error = request.GET.get('error')

    success = request.GET.get('success')
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        return render(request, 'account.html', {'user': user, 'error':error, 'success':success})

    else:

        return redirect('login')


# address
def address(request):

    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass

    error = request.GET.get('error')

    success = request.GET.get('success')
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        return render(request, 'address.html', {'user': user, 'error':error, 'success':success})

    else:

        return redirect('login')


# save address
def save_address(request):

    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        if request.method == 'POST':

            address_type = request.POST.get('address_type')
            house_name = request.POST.get('house_name')
            house_no = request.POST.get('house_no')
            house_street = request.POST.get('house_street')
            house_landmark = request.POST.get('house_landmark')
            apartment_name = request.POST.get('apartment_name')
            apartment_tower = request.POST.get('apartment_tower')
            apartment_floor = request.POST.get('apartment_floor')
            apartment_door = request.POST.get('apartment_door')

            if address_type == 'apartment':
                house_name = ''
                house_no = ''
                house_street = ''
                house_landmark = ''
            elif address_type == 'house':
                apartment_name = ''
                apartment_tower = ''
                apartment_floor = ''
                apartment_door = ''

            user.address_type = address_type
            user.house_name = house_name
            user.house_no = house_no
            user.street = house_street
            user.landmark = house_landmark
            user.apartment_name = apartment_name
            user.tower = apartment_tower
            user.floor = apartment_floor
            user.door = apartment_door

            user.save()

            return redirect('/account/?success=Address saved successfully')

        else:

            return redirect('address')
    else:

        return redirect('login')



# send otp
def send_otp(request):
    mobile = request.GET.get('mobile', None)
    otp_num = generateOTP()

    conn = http.client.HTTPSConnection("api.msg91.com")
    payload = "{\"otp\":" + otp_num + "}"
    headers = { 'content-type': "application/json" }
    conn.request("GET", "/api/v5/otp?template_id=" + settings.ENV('MSG91_OTP_TEMPLATE_ID') + "&mobile=91" + mobile + "&authkey=" + settings.ENV('MSG91_AUTH_KEY'), payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    try:
        otp = Otp.objects.get(mobile= mobile)
        otp.otp = otp_num
        otp.save()
    except:
        otp = Otp(mobile= mobile, otp= otp_num)
        otp.save()

    data = {
        'success': True
    }

    return JsonResponse(data)


# verify otp
def verify_otp(request):
    mobile = request.GET.get('mobile', None)
    otp = request.GET.get('otp', None)
    data = {
        'verified': Otp.objects.filter(mobile= mobile, otp= otp).exists()
    }
    return JsonResponse(data)


# check if phone number is registered
def check_registered(request):
    mobile = request.GET.get('mobile', None)
    data = {
        'is_registered': User.objects.filter(mobile=mobile).exists()
    }
    print(mobile)
    print(data)
    return JsonResponse(data)


# update personal details
def update_personal_details(request):
    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        if request.method == 'POST':
            name = request.POST.get('name')
            mobile_input = request.POST.get('mobile')
            email = request.POST.get('email')
            otp = request.POST.get('otp')

            if isValidPhoneNumber(mobile_input):
                if (not email == '' and isValidEmail(email)) or email == '':
                    if user.mobile != mobile_input:
                        if Otp.objects.filter(mobile= mobile_input, otp= otp).exists():

                            ip = get_client_ip(request)

                            otp_object = Otp.objects.get(mobile=mobile_input)
                            otp_object.ip = ip
                            otp_object.save()

                            user.mobile = mobile_input
                            user.name = name
                            user.email = email
                            user.save()
                            return redirect('account/?success=Updated successfully!')
                        else:
                            return redirect('account/?error=An error occured')
                    else:
                        user.name = name
                        user.email = email
                        user.save()
                        return redirect('account/?success=Updated successfully!')
                else:
                    return redirect('account/?error=Invalid email')
            else:
                return redirect('account/?error=Invalid mobile number')

        else:
            return redirect('account')
    else:
        return redirect('login')


# farmfills calculator get amount for deliveries up to date
def calculator_get_amount_uptodate(request):
    id = request.GET.get('id', None)
    date = convertToDateTime(request.GET.get('date', None)).date()

    user = User.objects.get(id=int(id))

    vacations = Vacation.objects.filter(user=user)
    extraless = ExtraLess.objects.filter(user=user)
    subs = Subscription.objects.filter(user=user)

    i = 0
    deliveries = 0
    amount = 0

    product = Product.objects.get(id=1)

    while True:
        i += 1
        thisdate = timezone.localtime(timezone.now()).date() + timedelta(days=i)

        in_vacation = False

        for e in extraless:
            if e.start_date <= thisdate and e.end_date >= thisdate :
                deliveries += 1
                amount += e.quantity * (product.price + user.user_type.price_variation)
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
                    quantity = getQuantityOfDate(s, (timezone.localtime(timezone.now()) + timedelta(days=i)).date())
                    if quantity > 0:
                        deliveries += 1
                    amount += quantity * (product.price + user.user_type.price_variation)
                elif s.end_date is not None:
                    if s.start_date <= thisdate and s.end_date >= thisdate:
                        quantity = getQuantityOfDate(s, (timezone.localtime(timezone.now()) + timedelta(days=i)).date())
                        if quantity > 0:
                            deliveries += 1
                        amount += quantity * (product.price + user.user_type.price_variation)


        if thisdate == date:
            break

    data = {
        'amount': amount,
        'deliveries': deliveries
    }
    return JsonResponse(data)


# farmfills calculator get amount for n deliveries
def calculator_get_deliveries_amount(request):
    id = request.GET.get('id', None)
    deliveries = int(request.GET.get('deliveries', None))

    user = User.objects.get(id=int(id))

    vacations = Vacation.objects.filter(user=user)
    extraless = ExtraLess.objects.filter(user=user)
    subs = Subscription.objects.filter(user=user)

    i = 0
    amount = 0
    thisdate = timezone.localtime(timezone.now()).date()

    product = Product.objects.get(id=1)

    while True:
        i += 1
        thisdate = timezone.localtime(timezone.now()).date() + timedelta(days=i)

        in_vacation = False

        for e in extraless:
            if e.start_date <= thisdate and e.end_date >= thisdate :
                deliveries -= 1
                amount += e.quantity * (product.price + user.user_type.price_variation)
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
                    quantity = getQuantityOfDate(s, (timezone.localtime(timezone.now()) + timedelta(days=i)).date())
                    if quantity > 0:
                        deliveries -= 1
                    amount += quantity * (product.price + user.user_type.price_variation)
                elif s.end_date is not None:
                    if s.start_date <= thisdate and s.end_date >= thisdate:
                        quantity = getQuantityOfDate(s, (timezone.localtime(timezone.now()) + timedelta(days=i)).date())
                        if quantity > 0:
                            deliveries -= 1
                        amount += quantity * (product.price + user.user_type.price_variation)


        if deliveries == 0:
            break

    data = {
        'amount': amount,
        'date': thisdate.strftime("%b %d, %Y")
    }
    return JsonResponse(data)


# check a phone number is valid
def isValidPhoneNumber(mobile):
    if re.match(r'^(\d{10})(?:\s|$)', mobile):
        return True
    else:
        return False


# check a email is valid
def isValidEmail(mobile):
    if re.match(r'\w+@\w+', mobile):
        return True
    else:
        return False


# logout user
def logout(request):

    if request.method == "POST":
        
        request.session['farmfills_user_id'] = None

        return redirect('login')
    
    return redirect('/')


# generating otp
def generateOTP() : 
    string = '0123456789'
    OTP = "" 
    varlen= len(string) 
    for i in range(4) : 
        OTP += string[m.floor(r.random() * varlen)] 
  
    return (OTP) 


# get client ip
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# razorpay initialization

# live
rp = razorpay.Client(auth=("rzp_live_6cJSrgm9Bmme4z", "d2MZqa7RgmDpSek5FTrJOtB4"))

# test
# rp = razorpay.Client(auth=("rzp_test_bfl0PpKTR5K0h3", "sAaLCOrqz8QMHRdhqlt7GPJI"))


# creating payment order
def create_payment_order(request):

    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        amount = request.GET.get('amount', None)

        email = user.email

        order = rp.order.create({'amount': float(amount)*100, 'currency': 'INR', 'receipt': user.mobile, 'payment_capture':0})

        last_day = last_day_of_month(timezone.localtime(timezone.now()))

        balance = getEndBalanceOfMonth(last_day, user)

        balance += int(amount)

        payment_db = Payment(date=timezone.localtime(timezone.now()), amount= amount, user=user, order_id= order['id'], mode='online', paid= False, balance=balance, description="-")

        payment_db.save()

        data = {
            'order': order,
            'mobile': user.mobile,
            'email': email
        }
        return JsonResponse(data)
    else:

        return redirect('login')


# get payment events request
@csrf_exempt
def payment_handle_request(request):
        
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            payment_db = Payment.objects.get(order_id=order_id)
            result = rp.utility.verify_payment_signature(params_dict)
            if result is None:
                payment = rp.payment.fetch(payment_id)
                amount = int(payment_db.amount) * 100
                try:
                    if payment_db.paid == True:
                        return redirect('/bill?success=Payment made successfully')
                    rp.payment.capture(payment_id, amount) 
                    payment_db.payment_id = payment_id
                    payment_db.paid = True
                    description = [payment['method'], payment['card_id'], payment['bank'], payment['wallet'], payment['vpa']]
                    description = [x for x in description if x is not None]
                    description = " ".join(description)
                    if payment['method'] == 'card':
                        description = getCardDetails(payment_id)
                    payment_db.description = description
                    payment_db.save()
                    return redirect('/bill?success=Payment made successfully')
                except Exception as e:
                    print(e)
                    return redirect('/bill?error=Payment failed. Ignore this message if your balance has updated')
            else:
                return redirect('/bill?error=Payment failed')
        except:
            return redirect('/bill?error=Something went wrong')


# get card details
def getCardDetails(payment_id):

    output = requests.get('https://api.razorpay.com/v1/payments/' + payment_id + '/card', auth=('rzp_live_6cJSrgm9Bmme4z', 'd2MZqa7RgmDpSek5FTrJOtB4'))

    output = output.json()
    output = [output['issuer'], output['network'], ' Ending ', output['last4']]
    output = [x for x in output if x is not None]
    return " ".join(output)


# get payment details
def getPaymentDetails(payment_id):

    payment = rp.payment.fetch(payment_id)
    return payment

# plan
def plan(request):
    
    error = request.GET.get('error')
    
    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        subscription = Subscription.objects.filter(user=user).order_by('-id')

        extraless = ExtraLess.objects.filter(user=user)

        vacations = Vacation.objects.filter(user=user)

        next_delivery_date =  getNextDeliveryDate(subscription, vacations, extraless)

        for i in range(len(subscription)):

            if subscription[i].start_date > timezone.localtime(timezone.now()).date():

                subscription[i].status = 'upcoming'

            elif (subscription[i].start_date <= timezone.localtime(timezone.now()).date() and subscription[i].end_date is None ) or (subscription[i].start_date <= timezone.localtime(timezone.now()).date() and subscription[i].end_date > timezone.localtime(timezone.now()).date()):

                subscription[i].status = 'active'

            elif subscription[i].start_date <= timezone.localtime(timezone.now()).date() and subscription[i].end_date <= timezone.localtime(timezone.now()).date():

                subscription[i].status = 'completed'

            subscription[i].start_date = subscription[i].start_date.strftime("%b %d, %Y")
            
            if subscription[i].end_date is not None:

                subscription[i].end_date = subscription[i].end_date.strftime("%b %d, %Y")

        return render(request, 'plan.html', {'user': user, 'subscription': subscription, 'next_delivery': next_delivery_date, 'error':error})

    else:

        return redirect('login')


# vacation
def vacation(request):
    
    error = request.GET.get('error')
    
    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        subscription = Subscription.objects.filter(user=user)

        extraless = ExtraLess.objects.filter(user=user)

        vacations = Vacation.objects.filter(user=user).order_by('-id')

        next_delivery_date =  getNextDeliveryDate(subscription, vacations, extraless)

        for i in range(len(vacations)):

            if vacations[i].start_date > timezone.localtime(timezone.now()).date():

                vacations[i].status = 'upcoming'

            elif (vacations[i].start_date <= timezone.localtime(timezone.now()).date() and vacations[i].end_date is None ) or (vacations[i].start_date <= timezone.localtime(timezone.now()).date() and vacations[i].end_date > timezone.localtime(timezone.now()).date()):

                vacations[i].status = 'active'

            elif vacations[i].start_date <= timezone.localtime(timezone.now()).date() and vacations[i].end_date <= timezone.localtime(timezone.now()).date():

                vacations[i].status = 'completed'

            vacations[i].start_date = vacations[i].start_date.strftime("%b %d, %Y")
            
            if vacations[i].end_date is not None:

                vacations[i].end_date = vacations[i].end_date.strftime("%b %d, %Y")

        return render(request, 'vacation.html', {'user': user, 'vacations': vacations, 'next_delivery': next_delivery_date, 'error':error})

    else:

        return redirect('login')


# extra/less
def extraLess(request):
    
    error = request.GET.get('error')
    
    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        subscription = Subscription.objects.filter(user=user)

        vacations = Vacation.objects.filter(user=user)

        extraless = ExtraLess.objects.filter(user=user).order_by('-id')

        next_delivery_date =  getNextDeliveryDate(subscription, vacations, extraless)

        for i in range(len(extraless)):

            if extraless[i].start_date > timezone.localtime(timezone.now()).date():

                extraless[i].status = 'upcoming'

            elif (extraless[i].start_date <= timezone.localtime(timezone.now()).date() and extraless[i].end_date is None ) or (extraless[i].start_date <= timezone.localtime(timezone.now()).date() and extraless[i].end_date > timezone.localtime(timezone.now()).date()):

                extraless[i].status = 'active'

            elif extraless[i].start_date <= timezone.localtime(timezone.now()).date() and extraless[i].end_date <= timezone.localtime(timezone.now()).date():

                extraless[i].status = 'completed'

            extraless[i].start_date = extraless[i].start_date.strftime("%b %d, %Y")
            
            if extraless[i].end_date is not None:

                extraless[i].end_date = extraless[i].end_date.strftime("%b %d, %Y")

        return render(request, 'extraless.html', {'user': user, 'extraless': extraless, 'next_delivery': next_delivery_date, 'error':error})

    else:

        return redirect('login')


# bill
def bill(request):
    
    error = request.GET.get('error')

    success = request.GET.get('success')
    
    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        user = User.objects.get(id=user_id)

        payments = Payment.objects.filter(user=user, paid=True)

        extras = Extra.objects.filter(user=user)

        purchases = Purchase.objects.filter(user=user)

        refunds = Refund.objects.filter(user=user)

        products = Product.objects.all()
        
        bill_data = generateBillData(payments, purchases, refunds, extras, products, user)

        balance = 0

        balance_date = timezone.localtime(timezone.now()).strftime("%b %d, %Y")
        
        if user.user_type.payment_type == 'postpaid':
            if len(bill_data) > 0:
                balance = bill_data[0]['end_balance']
                if bill_data[0]['month'] == timezone.localtime(timezone.now()).strftime('%Y %b'):
                    balance = bill_data[1]['end_balance'] + bill_data[0]['payment']
            balance_date = (timezone.localtime(timezone.now()).replace(day=1) - timedelta(days=1)).strftime("%b %d, %Y")
        elif user.user_type.payment_type == 'prepaid':
            if bill_data:
                balance = bill_data[0]['end_balance']

        return render(request, 'bill.html', {'user': user, 'error':error, 'success':success, 'bill_data': bill_data, 'products': products, 'balance_date': balance_date, 'balance':balance})

    else:

        return redirect('login')


# payment
def payment(request):
    
    error = request.GET.get('error')

    success = request.GET.get('success')
    
    user_id = None
    try:
        user_id = request.session['farmfills_user_id']
    except:
        pass
    
    if user_id is not None:

        product = Product.objects.get(id=1)

        user = User.objects.get(id=user_id)

        if not user.user_type.payment_type == 'prepaid':

            return redirect('bill')

        return render(request, 'payment.html', {'user':user, 'milk_price': product.price, 'error':error, 'success':success})
    
    return redirect('login')


# delete extra/less
def delete_extraless(request):

    if request.method == 'POST':

        id = request.POST.get('id')

        ExtraLess.objects.filter(id=id).delete()

    return redirect('extra-less')


# stop extra/less
def stop_extraless(request):

    if request.method == 'POST':

        id = request.POST.get('id')

        ExtraLess.objects.filter(id=id).update(end_date=timezone.localtime(timezone.now()))

    return redirect('extra-less')


# create extra/less
def create_extraless(request):

    if request.method == 'POST':
        user_id = request.session['farmfills_user_id']

        user = User.objects.get(id=user_id)

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        quantity = request.POST.get('quantity')

        if convertToDateTime(start_date) > convertToDateTime(end_date):

            return redirect('/extra-less?error=Start date should not be greater than end date')

        extraless = ExtraLess.objects.filter(user=user)

        error = checkDateOverlaps(start_date, end_date, extraless)

        if error:

            return  redirect('/extra-less?error=There is another custom delivery in the same time period')

        extraless = ExtraLess(
            user = user,
            start_date = convertToDateTime(start_date),
            end_date = convertToDateTime(end_date),
            quantity = quantity,
            created_by = 'customer',
            edited_by = 'customer'
        )
        extraless.save()

    return redirect('extra-less')


# delete subscription
def delete_subscription(request):

    if request.method == 'POST':

        id = request.POST.get('id')

        Subscription.objects.filter(id=id).delete()

    return redirect('plan')


# stop subscription
def stop_subscription(request):

    if request.method == 'POST':

        id = request.POST.get('id')

        Subscription.objects.filter(id=id).update(end_date=timezone.localtime(timezone.now()))

    return redirect('plan')


# create_subscription
def create_subscription(request):

    if request.method == 'POST':
        user_id = request.session['farmfills_user_id']

        user = User.objects.get(id=user_id)

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if end_date == '':
                end_date = None

        sub_type = request.POST.get('sub_type')
        daily_different_alternative = request.POST.get('daily_different_alternative')
        daily_day1 = 0
        daily_day2 = 0
        alternate_quantity = 0
        weekly_mon = 0
        weekly_tue = 0
        weekly_wed = 0
        weekly_thu = 0
        weekly_fri = 0
        weekly_sat = 0
        weekly_sun = 0
        custom_quantity = 0
        custom_interval = 0

        if sub_type == 'daily':
            daily_day1 = request.POST.get('daily_day1')
            if daily_different_alternative == 'true':
                daily_day2 = request.POST.get('daily_day2')
        elif sub_type == 'alternate':
            alternate_quantity = request.POST.get('alternate_quantity')
        elif sub_type == 'custom':
            custom_quantity = request.POST.get('custom_quantity')
            custom_interval = request.POST.get('custom_interval')
        elif sub_type == 'weekly':
            weekly_mon = request.POST.get('weekly_mon')
            weekly_tue = request.POST.get('weekly_tue')
            weekly_wed = request.POST.get('weekly_wed')
            weekly_thu = request.POST.get('weekly_thu')
            weekly_fri = request.POST.get('weekly_fri')
            weekly_sat = request.POST.get('weekly_sat')
            weekly_sun = request.POST.get('weekly_sun')

        if end_date is not None and convertToDateTime(start_date) > convertToDateTime(end_date):

            return redirect('/plan?error=Start date should not be greater than end date')

        subscriptions = Subscription.objects.filter(user=user)

        error = checkDateOverlaps(start_date, end_date, subscriptions)

        if error:

            return  redirect('/plan?error=There is another subscription in the same time period')

        subscription = Subscription(
            user = user,
            start_date = convertToDateTime(start_date),
            end_date = convertToDateTime(end_date),
            sub_type = sub_type,
            daily_day1 = daily_day1,
            daily_day2 = daily_day2,
            custom_interval = custom_interval,
            custom_quantity = custom_quantity,
            alternate_quantity = alternate_quantity,
            weekly_mon = weekly_mon,
            weekly_tue = weekly_tue,
            weekly_wed = weekly_wed,
            weekly_thu = weekly_thu,
            weekly_fri = weekly_fri,
            weekly_sat = weekly_sat,
            weekly_sun = weekly_sun,
            created_by = 'customer',
            edited_by = 'customer'
        )
        subscription.save()

    return redirect('plan')


# delete vacation
def delete_vacation(request):

    if request.method == 'POST':

        id = request.POST.get('id')

        Vacation.objects.filter(id=id).delete()

    return redirect('vacation')


# stop vacation
def stop_vacation(request):

    if request.method == 'POST':

        id = request.POST.get('id')

        Vacation.objects.filter(id=id).update(end_date=timezone.localtime(timezone.now()))

    return redirect('vacation')


# create_vacation
def create_vacation(request):

    if request.method == 'POST':

        user_id = request.session['farmfills_user_id']

        user = User.objects.get(id=user_id)

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if end_date == '':
                end_date = None

        if end_date is not None and convertToDateTime(start_date) > convertToDateTime(end_date):

            return redirect('/vacation?error=Start date should not be greater than end date')

        vacations = Vacation.objects.filter(user=user)

        error = checkDateOverlaps(start_date, end_date, vacations)

        if error:

            return  redirect('/vacation?error=There is another vacation in the same time period')

        vacation = Vacation(
            user = user,
            start_date = convertToDateTime(start_date),
            end_date = convertToDateTime(end_date),
            created_by = 'customer',
            edited_by = 'customer'
        )
        vacation.save()

    return redirect('vacation')


# check date overlap with crossing over all patterns
def checkDateOverlaps(start_date, end_date, data):

    start_date = convertToDateTime(start_date).date()
    if end_date is not None:
        end_date = convertToDateTime(end_date).date()

    for sub in data:

        if end_date is None and sub.end_date is None: return True

        if sub.end_date is None and start_date >= sub.start_date: return True

        if end_date is None and sub.start_date >= start_date: return True

        if sub.end_date is not None:
            if end_date is None and sub.start_date <= start_date and sub.end_date >= start_date: return True
        
        if end_date is not None:
            if start_date <= sub.start_date and sub.start_date <= end_date: return True
            elif sub.end_date is None and start_date <= sub.start_date and end_date >= sub.start_date: return True
        
        if end_date is not None and sub.end_date is not None:
            if sub.start_date < start_date and end_date < sub.end_date: return True
            elif start_date <= sub.end_date and sub.end_date <= end_date: return True
        
    return False


# get next delivery date
def getNextDeliveryDate(subscriptions, vacations, extraless):

    exist = []
    today = timezone.localtime(timezone.now()).date()

    # checking if any data coming in future or now
    for e in extraless:
        if (e.start_date <= today or e.start_date >= today) and e.end_date is None:
            exist.append('extra')
        elif e.end_date is not None:
            if (e.start_date <= today or e.start_date >= today) and e.end_date > today:
                exist.append('extra')

    for s in subscriptions:
        if (s.start_date <= today or s.start_date >= today) and s.end_date is None:
            exist.append('subs')
        elif s.end_date is not None:
            if (s.start_date <= today or s.start_date >= today) and s.end_date > today:
                exist.append('subs')
        
    for v in vacations:
        if (v.start_date <= today or v.start_date >= today) and v.end_date is None:
            exist.append('vacations')
        elif v.end_date is not None:
            if (v.start_date <= today or v.start_date >= today) and v.end_date > today:
                exist.append('vacations')
    if len(exist) == 1 and exist[0] == 'vacations':
        return None

    i = 0
    while exist:
        i += 1
        day = timezone.localtime(timezone.now()) + timedelta(days=i)

        # priority for extraless
        if 'extra' in exist:
            for e in extraless:
                if e.start_date <= day.date() and e.end_date is None:
                    return (timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y")
                elif e.end_date is not None:
                    if e.start_date <= day.date() and e.end_date >= day.date():
                        return (timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y")
                elif 'subs' not in exist and 'vacations' not in exist:
                    return None

        in_vacation = False
        
        # skip looping on vactions
        if 'vacations' in exist:
            for v in vacations:
                if v.end_date is not None:
                    if v.start_date <= day.date() and v.end_date >= day.date():
                        in_vacation = True
                        break 
                elif v.start_date <= day.date() and v.end_date is None:
                    return None
                elif 'subs' not in exist:
                    return None

        # checking subscriptions at last
        if 'subs' in exist and not in_vacation:
            for s in subscriptions:
                if s.start_date <= day.date() and s.end_date is None:
                    if checkDeliveyInDateFromSub(s, day.date()):
                        return (timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y")
                elif s.start_date <= day.date() and s.end_date >= day.date():
                    if checkDeliveyInDateFromSub(s, day.date()):
                        return (timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y")

    return None


# get next delivery date and quantity
def getNextDelivery(subscriptions, vacations, extraless):

    exist = []
    today = timezone.localtime(timezone.now()).date()

    # checking if any data coming in future or now
    for e in extraless:
        if (e.start_date <= today or e.start_date >= today) and e.end_date is None:
            exist.append('extra')
        elif e.end_date is not None:
            if (e.start_date <= today or e.start_date >= today) and e.end_date > today:
                exist.append('extra')

    for s in subscriptions:
        if (s.start_date <= today or s.start_date >= today) and s.end_date is None:
            exist.append('subs')
        elif s.end_date is not None:
            if (s.start_date <= today or s.start_date >= today) and s.end_date > today:
                exist.append('subs')
        
    for v in vacations:
        if (v.start_date <= today or v.start_date >= today) and v.end_date is None:
            exist.append('vacations')
        elif v.end_date is not None:
            if (v.start_date <= today or v.start_date >= today) and v.end_date > today:
                exist.append('vacations')
    if len(exist) == 1 and exist[0] == 'vacations':
        return None

    i = 0
    while exist:
        i += 1
        day = timezone.localtime(timezone.now()) + timedelta(days=i)

        # priority for extraless
        if 'extra' in exist:
            for e in extraless:
                if e.start_date <= day.date() and e.end_date is None:
                    return {'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y"), 'quantity':e.quantity}
                elif e.end_date is not None:
                    if e.start_date <= day.date() and e.end_date >= day.date():
                        return {'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y"), 'quantity':e.quantity}
                elif 'subs' not in exist and 'vacations' not in exist:
                    return None

        in_vacation = False
        
        # skip looping on vactions
        if 'vacations' in exist:
            for v in vacations:
                if v.end_date is not None:
                    if v.start_date <= day.date() and v.end_date >= day.date():
                        in_vacation = True
                        break 
                elif v.start_date <= day.date() and v.end_date is None:
                    return None
                elif 'subs' not in exist:
                    return None

        # checking subscriptions at last
        if 'subs' in exist and not in_vacation:
            for s in subscriptions:
                if s.start_date <= day.date() and s.end_date is None:
                    if checkDeliveyInDateFromSub(s, day.date()):
                        return {'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y"), 'quantity':getQuantityOfDate(s, (timezone.localtime(timezone.now()) + timedelta(days=i)).date())}
                elif s.start_date <= day.date() and s.end_date >= day.date():
                    if checkDeliveyInDateFromSub(s, day.date()):
                        return {'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y"), 'quantity':getQuantityOfDate(s, (timezone.localtime(timezone.now()) + timedelta(days=i)).date())}

    return None


# get next delivery date and quantity after tomorrow
def getNextDeliveryAfterTomorrow(subscriptions, vacations, extraless):

    exist = []
    today = timezone.localtime(timezone.now()).date() + timedelta(days=1)

    # checking if any data coming in future or now
    for e in extraless:
        if (e.start_date <= today or e.start_date >= today) and e.end_date is None:
            exist.append('extra')
        elif e.end_date is not None:
            if (e.start_date <= today or e.start_date >= today) and e.end_date > today:
                exist.append('extra')

    for s in subscriptions:
        if (s.start_date <= today or s.start_date >= today) and s.end_date is None:
            exist.append('subs')
        elif s.end_date is not None:
            if (s.start_date <= today or s.start_date >= today) and s.end_date > today:
                exist.append('subs')
        
    for v in vacations:
        if (v.start_date <= today or v.start_date >= today) and v.end_date is None:
            exist.append('vacations')
        elif v.end_date is not None:
            if (v.start_date <= today or v.start_date >= today) and v.end_date > today:
                exist.append('vacations')
    if len(exist) == 1 and exist[0] == 'vacations':
        return None

    i = 1
    while exist:
        i += 1
        day = timezone.localtime(timezone.now()) + timedelta(days=i)

        # priority for extraless
        if 'extra' in exist:
            for e in extraless:
                if e.start_date <= day.date() and e.end_date is None:
                    return {'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y"), 'quantity':e.quantity}
                elif e.end_date is not None:
                    if e.start_date <= day.date() and e.end_date >= day.date():
                        return {'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y"), 'quantity':e.quantity}
                elif 'subs' not in exist and 'vacations' not in exist:
                    return None

        in_vacation = False
        
        # skip looping on vactions
        if 'vacations' in exist:
            for v in vacations:
                if v.end_date is not None:
                    if v.start_date <= day.date() and v.end_date >= day.date():
                        in_vacation = True
                        break 
                elif v.start_date <= day.date() and v.end_date is None:
                    return None
                elif 'subs' not in exist:
                    return None

        # checking subscriptions at last
        if 'subs' in exist and not in_vacation:
            for s in subscriptions:
                if s.start_date <= day.date() and s.end_date is None:
                    if checkDeliveyInDateFromSub(s, day.date()):
                        return {'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y"), 'quantity':getQuantityOfDate(s, (timezone.localtime(timezone.now()) + timedelta(days=i)).date())}
                elif s.start_date <= day.date() and s.end_date >= day.date():
                    if checkDeliveyInDateFromSub(s, day.date()):
                        return {'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d, %Y"), 'quantity':getQuantityOfDate(s, (timezone.localtime(timezone.now()) + timedelta(days=i)).date())}

    return None
    


# get upcoming days
def getUpcomingDays(subscriptions, vacations, extraless):

    output = []

    for i in range(15):
        day = timezone.localtime(timezone.now()) + timedelta(days=i)

        entered = False

        # priority for extraless
        for e in extraless:
            if e.start_date <= day.date() and e.end_date is None:
                output.append({'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d"), 'quantity':str(e.quantity)})
                entered = True
                break
            elif e.end_date is not None:
                if e.start_date <= day.date() and e.end_date >= day.date():
                    entered = True
                    output.append({'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d"), 'quantity':str(e.quantity)})
                    break
        
        # skip looping on vactions
        if not entered:
            for v in vacations:
                if v.end_date is not None:
                    if v.start_date <= day.date() and v.end_date >= day.date():
                        output.append({'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d"), 'quantity':'0'})
                        entered = True
                        break 
                elif v.start_date <= day.date() and v.end_date is None:
                    output.append({'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d"), 'quantity':'0'})
                    entered = True
                    break

        # checking subscriptions at last
        if not entered:
            for s in subscriptions:
                if s.start_date <= day.date() and s.end_date is None:
                    entered = True
                    output.append({'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d"), 'quantity':str(getQuantityOfDate(s, day.date()))})
                    break
                elif s.start_date <= day.date() and s.end_date >= day.date():
                    entered = True
                    output.append({'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d"), 'quantity':str(getQuantityOfDate(s, day.date()))})
                    break
        
        if not entered:
            output.append({'date':(timezone.localtime(timezone.now()) + timedelta(days=i)).strftime("%b %d"), 'quantity':0})
    
    return output


# get quanity of day from subscription
def getQuantityOfDate(subscription, date):

    if subscription.sub_type == 'daily':

        if subscription.daily_day2 is None or subscription.daily_day2 == 0:

            return subscription.daily_day1

        else:

            diff = (subscription.start_date - date).days

            if diff % 2 == 0:

                return subscription.daily_day1

            else:

                return subscription.daily_day2
        

    elif subscription.sub_type == 'alternate':

        diff = (subscription.start_date - date).days

        if diff % 2 == 0:

            return subscription.alternate_quantity

        else:

            return 0


    elif subscription.sub_type == 'weekly':

        day_f_week = date.strftime('%a').lower()

        return {
            'mon': subscription.weekly_mon,
            'tue': subscription.weekly_tue,
            'wed': subscription.weekly_wed,
            'thu': subscription.weekly_thu,
            'fri': subscription.weekly_fri,
            'sat': subscription.weekly_sat,
            'sun': subscription.weekly_sun,
        }[day_f_week]
        

    elif subscription.sub_type == 'custom':
        
        diff = (subscription.start_date - date).days
        
        if diff % subscription.custom_interval == 0:
            return subscription.custom_quantity
        else:
            return 0
    
    return 0


# check if subscription has quantity in a date
def checkDeliveyInDateFromSub(subscription, date):

    if subscription.sub_type == 'daily':

        if subscription.daily_day2 == 0:

            return True

        else:

            diff = (subscription.start_date - date).days

            if diff % 2 == 0:

                if not subscription.daily_day1 == 0:
                    return True

            else:

                if not subscription.daily_day2 == 0:
                    return True
        

    elif subscription.sub_type == 'alternate':

        diff = (subscription.start_date - date).days

        if diff % 2 == 0:

            return True

        else:

            return False


    elif subscription.sub_type == 'weekly':

        day_f_week = date.strftime('%a').lower()

        quanity = {
                    'mon': subscription.weekly_mon,
                    'tue': subscription.weekly_tue,
                    'wed': subscription.weekly_wed,
                    'thu': subscription.weekly_thu,
                    'fri': subscription.weekly_fri,
                    'sat': subscription.weekly_sat,
                    'sun': subscription.weekly_sun,
                }[day_f_week]

        if quanity > 0:
            return True

        
    elif subscription.sub_type == 'custom':
        
        diff = (subscription.start_date - date).days
        
        if diff % subscription.custom_interval == 0:
            return True
        else:
            return False
        
    return False


# generate bill data of last 24 month
def generateBillData(payments, purchases, refunds, extras, products, user):

    month = int(timezone.localtime(timezone.now()).date().strftime('%m'))
    year = int(timezone.localtime(timezone.now()).date().strftime('%Y'))

    output = []

    for i in range(25):
        
        # decreasing 1 month in each loop
        if i != 0:
            month -= 1
            if month == 0:
                year -= 1
                month = 12

        data = {
            'month': datetime(year, month, 1, tzinfo=pytz.UTC).strftime('%Y %b'), 
            'payment':0, 
            'purchase':0, 
            'paymentList': [], 
            'purchaseList': [], 
            'productList': [], 
            'refund': [],
            'yearDiff': int(timezone.localtime(timezone.now()).date().strftime('%Y')) - int(year),
            'monthDiff': i,
            'start_balance': 0,
            'end_balance': 0
        }
        
        last_day = last_day_of_month(datetime(year, month, 1, tzinfo=pytz.UTC))

        data['end_balance'] = getEndBalanceOfMonth(last_day, user)

        # decreasing 1 month in for start_balance
        s_month = month
        s_year = year

        s_month -= 1
        if s_month == 0:
            s_year -= 1
            s_month = 12

        last_day = last_day_of_month(datetime(s_year, s_month, 1, tzinfo=pytz.UTC))
        data['start_balance'] = getEndBalanceOfMonth(last_day, user)

        exist = False

        for p in payments:
            if int(p.date.date().strftime('%Y')) == year and int(p.date.date().strftime('%m')) == month:
                data['payment'] += p.amount
                data['paymentList'].append({'date': p.date.date(), 'amount': p.amount, 'description': p.description})
                exist = True
        
        for p in purchases:
            if int(p.date.date().strftime('%Y')) == year and int(p.date.date().strftime('%m')) == month:
                data['purchase'] += p.amount
                data['purchaseList'].append({'date': p.date.date(), 'amount': p.amount, 'quantity': p.quantity, 'product': p.product})
                exist = True

        for e in extras:
            if int(e.date.date().strftime('%Y')) == year and int(e.date.date().strftime('%m')) == month:
                exist = True
                data['purchase'] += e.amount
                data['purchaseList'].append({'date': e.date.date(), 'amount': e.amount, 'quantity': e.quantity, 'product': e.product})


        for pt in products:
            amount = 0
            quantity = 0
            for p in data['purchaseList']:
                if p['product'] == pt:
                    amount += p['amount']
                    quantity += p['quantity']
            if amount != 0 or quantity != 0:
                data['productList'].append({'product': pt, 'amount':amount, 'quantity':quantity})
        
        for r in refunds:
            if int(r.date.date().strftime('%Y')) == year and int(r.date.date().strftime('%m')) == month:
                data['purchase'] -= r.amount
                exist = True

                data['purchaseList'].append({'date': r.date.date(), 'amount': r.amount * -1, 'quantity': r.quantity, 'product': r.product})
                
                refundExist = False
                for i in range(len(data['refund'])):
                    if r.product == data['refund'][i]['product']:
                        data['refund'][i]['amount'] += r.amount
                        data['refund'][i]['quantity'] += r.quantity
                        refundExist = True
                
                if not refundExist:
                    data['refund'].append({'amount':r.amount, 'quantity':r.quantity, 'product':r.product})

        data['purchaseList'] = sorted(data['purchaseList'], key=lambda x: x['date'], reverse=False)

        if exist:
            output.append(data)

    return output


# get last day of a month from date
def last_day_of_month(any_day):
    any_day = any_day.replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)



# get the ending balance of a month with last day of month
def getEndBalanceOfMonth(last_day, user):
    last_day = last_day + timedelta(days=1)
    balance = 0
    balance_list = []
    max_balance = {}

    balance_list.append(Purchase.objects.filter(Q(user=user), Q(date__lt = last_day)).order_by('-date', '-id').first())

    balance_list.append(Payment.objects.filter(Q(user=user), Q(paid=True), Q(date__lt = last_day)).order_by('-date', '-id').first())

    balance_list.append(Refund.objects.filter(Q(user=user), Q(date__lt = last_day)).order_by('-date', '-id').first())

    balance_list.append(Extra.objects.filter(Q(user=user), Q(date__lt = last_day)).order_by('-date', '-id').first())

     
    balance_list =  [x for x in balance_list if x is not None]

    for i in balance_list:
        if max_balance:
            if i.date > max_balance.date:
                max_balance = i
            elif i.date == max_balance.date:
                done = False
                try:
                    if i.reason:
                        if i.balance == max_balance.balance + i.amount:
                            max_balance = i
                            done = True
                except:
                    pass

                try:
                    if i.description:
                        if i.balance == max_balance.balance + i.amount:
                            max_balance = i
                            done = True
                except:
                    pass

                if not done: 
                    if i.balance == max_balance.balance - i.amount:
                        max_balance = i
        else:
            max_balance = i
    
    if max_balance:
        balance = max_balance.balance

    return balance

# get the purchase of a month with last day of month
def getPurchaseOfMonth(last_day, user):
    
    output = 0

    # reset the time of the last day
    last_day = last_day.replace(hour=0, minute=0, second=0, microsecond=0)

    # substract 1 microsecond from the first day to get the last time of the day before
    # for querying the data with greater than operator
    first_day = last_day.replace(day=1) - timedelta(microseconds=1)

    # adding one one day to the last day to get the first time of the next day
    # for querying data with less than operator
    last_day = last_day + timedelta(days=1)
    
    purchase = Purchase.objects.filter(Q(user=user), Q(date__lt = last_day), Q(date__gt = first_day)).order_by('-date', '-id')

    refund = Refund.objects.filter(Q(user=user), Q(date__lt = last_day), Q(date__gt = first_day)).order_by('-date', '-id')

    for p in purchase:

        output += p.amount
    
    for r in refund:

        output -= r.amount

    return output


# get the payment of a month with last day of month
def getPaymentOfMonth(last_day, user):

    output = 0

    first_day = last_day.replace(day=1)
    
    payment = Payment.objects.filter(user=user, paid=True, date__range=(first_day, last_day)).order_by('-date', '-id')

    for p in payment:

        output += p.amount

    return output


# loop ========== hole
def loop_hole(request):
    if request.method == 'GET':
        key = settings.ENV('LOOPHOLE_KEY')
        secret = settings.ENV('LOOPHOLE_SECRET')

        key_input = request.GET.get('key')
        secret_input = request.GET.get('secret')

        if key == key_input and secret == secret_input:

            user_id = request.GET.get('uid')
            request.session['farmfills_user_id'] = user_id
            
            return HttpResponse('Loophole created')
        
        return HttpResponse("Don't Play with me")


# send bill
def send_bill(request):
    if request.method == 'GET':
        user_id = request.GET.get('uid')
        user = User.objects.get(id=user_id)

        user.bill_send_date = timezone.localtime(timezone.now())
        user.save()

        return redirect("https://api.whatsapp.com/send?phone=91" + user.mobile + "&text=%2ADear+Customer%2C%2A+%0D%0A%0D%0APlease+use+the+below+link+to+view+%26+pay+the+milk+bill%2C%0D%0A%0D%0A%2Ahttps%3A%2F%2Fapp.farmfills.com%2A%0D%0A%0D%0APlease+use+your+registered+mobile+number+%2A" + user.mobile + "%2A+for+login.+++%0D%0A%0D%0A_please+note+that+the+same+link+can+be+used+to+view+%2Aupcoming+bills%2A+%26+pay+online._%0D%0A%0D%0AThanks+%26+Regards%2C%0D%0A+--%0D%0A+%2ATeam+Farmfills%2A%0D%0A")


# send prepaid link
def send_prepaid_link(request):
    if request.method == 'GET':
        user_id = request.GET.get('uid')
        user = User.objects.get(id=user_id)

        user.bill_send_date = timezone.localtime(timezone.now())
        user.save()

        return redirect("https://api.whatsapp.com/send?phone=91" + user.mobile + "&text=%2ADear+Sir%2FMadam%2C%2A%0D%0A%0D%0AThank+you+for+your+inquiry+regarding+our+product+and+service.%0D%0A%0D%0AWe+are+pleased+to+share+you+the+link+to+recharge+your+wallet.%0D%0A%0D%0A%2Ahttps%3A%2F%2Fapp.farmfills.com%2A%0D%0A%0D%0APlease+use+your+registered+mobile+number+%2A" + user.mobile + "%2A+for+login.+%0D%0A%0D%0APlease+feel+free+to+contact+me+if+you+need+any+further+information.%0D%0A%0D%0AThanks+%26+Regards%2C%0D%0A+--%0D%0A+%2ATeam+Farmfills%2A")


# send reminder
def send_reminder(request):
    if request.method == 'GET':
        user_id = request.GET.get('uid')
        user = User.objects.get(id=user_id)

        user.bill_send_date = timezone.localtime(timezone.now())
        user.save()

        return redirect("https://api.whatsapp.com/send?phone=91" + user.mobile + "&text=%2ADear+Customer%2C%2A+%0D%0A%0D%0AA+friendly+reminder+for+the+pending+milk+bill.+%0D%0A%0D%0AYou+can+pay+online+through%2C%0D%0A%0D%0Ahttps%3A%2F%2Fapp.farmfills.com%0D%0A%0D%0A_if+it%27s+paid+already+to+our+bank+account+directly%2C+kindly+share+the+screenshot+or+transaction+number+for+reference_++%0D%0A%0D%0AThanks+%26+Regards%2C%0D%0A+--%0D%0A+%2ATeam+Farmfills%2A")


# payment hook for razorpay
@csrf_exempt
def payment_hook(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    order_id = body['payload']['payment']['entity']['order_id']
    payment_id = body['payload']['payment']['entity']['id']
    print(payment_id)
    if body['payload']['payment']['entity']['status'] == 'authorized':
        payment_db = Payment.objects.get(order_id=order_id)
        payment = rp.payment.fetch(payment_id)
        amount = int(payment_db.amount) * 100
        try:
            rp.payment.capture(payment_id, amount) 
            payment_db.payment_id = payment_id
            payment_db.paid = True
            description = [payment['method'], payment['card_id'], payment['bank'], payment['wallet'], payment['vpa']]
            description = [x for x in description if x is not None]
            description = " ".join(description)
            if payment['method'] == 'card':
                description = getCardDetails(payment_id)
            payment_db.description = description
            payment_db.save()
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(status=204)
    return HttpResponse(status=202)



def view_transactions(request, id):

    if request.user.is_superuser:

        user = User.objects.get(id=id)
        transaction_data = []

        purchases = Purchase.objects.filter(user=user).order_by('-date', '-id')

        payments = Payment.objects.filter(user=user, paid=True).order_by('-date', '-id')

        refunds = Refund.objects.filter(user=user).order_by('-date', '-id')

        extras = Extra.objects.filter(user=user).order_by('-date', '-id')

        transaction_data = list(purchases) 

        transaction_data += list(payments)
        transaction_data += list(refunds)
        transaction_data += list(extras)

        transaction_data = sorted(transaction_data, key=lambda k: k.date, reverse=True) 
        

        return render(request, 'transactions.html', {'transactions':transaction_data})
    
    else:
        return redirect('/admin')


# get the latest transaction of a user with the transaction id
def get_last_transaction(user):
    last_transaction_id = user.last_transaction
    last_transaction = None
    if Purchase.objects.filter(user=user, transaction_id=last_transaction_id).exists():
        last_transaction = Purchase.objects.get(user=user, transaction_id=last_transaction_id)
    elif Payment.objects.filter(user=user, transaction_id=last_transaction_id).exists():
        last_transaction = Payment.objects.get(user=user, transaction_id=last_transaction_id)
    elif Refund.objects.filter(user=user, transaction_id=last_transaction_id).exists():
        last_transaction = Refund.objects.get(user=user, transaction_id=last_transaction_id)
    elif Extra.objects.filter(user=user, transaction_id=last_transaction_id).exists():
        last_transaction = Extra.objects.get(user=user, transaction_id=last_transaction_id)
    return last_transaction


def format_number(num):
  if num % 1 == 0:
    return int(num)
  else:
    return num
