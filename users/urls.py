from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login', views.login, name="login"),
    path('', views.home, name="home"),
    re_path(r'^plan/$', views.plan, name="plan"),
    re_path(r'^vacation/$', views.vacation, name="vacation"),
    re_path(r'^extra-less/$', views.extraLess, name="extra-less"),
    re_path(r'^bill/$', views.bill, name="bill"),
    re_path(r'^account/$', views.account, name="account"),
    re_path(r'^address/$', views.address, name="address"),
    path('address/save', views.save_address, name="save_address"),
    path('transactions/<int:id>', views.view_transactions, name="view_transactions"),
    # path('register', views.register, name="register"),
    path('update-personal-details', views.update_personal_details, name="update_personal_details"),
    path('payment', views.payment, name="payment"),
    path('history', views.history, name="history"),
    path('payments/handle', views.payment_handle_request, name="payment_handle_request"),
    path('payments/webhook', views.payment_hook, name="payment_hook"),
    path('get-ip', views.get_client_ip, name="get-ip"),
    path('logout', views.logout, name='logout'),
    path('subscription/delete', views.delete_subscription, name='delete_subscription'),
    path('subscription/stop', views.stop_subscription, name='stop_subscription'),
    path('subscription/create', views.create_subscription, name='create_subscription'),
    path('vacation/create', views.create_vacation, name='create_vacation'),
    path('vacation/delete', views.delete_vacation, name='delete_vacation'),
    path('vacation/stop', views.stop_vacation, name='stop_vacation'),
    path('extra-less/create', views.create_extraless, name='create_extraless'),
    path('extra-less/delete', views.delete_extraless, name='delete_extraless'),
    path('extra-less/stop', views.stop_extraless, name='stop_extraless'),
    path('send/bill', views.send_bill, name='send_bill'),
    path('send/reminder', views.send_reminder, name='send_reminder'),
    path('send/prepaid-link', views.send_prepaid_link, name='send_prepaid_link'),
    re_path(r'^ajax/check_registered/$', views.check_registered, name='check_registered'),
    re_path(r'^ajax/payments/order/create$', views.create_payment_order, name='create_payment_order'),
    re_path(r'^ajax/calculator/date$', views.calculator_get_amount_uptodate, name='calculator_get_amount_uptodate'),
    re_path(r'^ajax/calculator/delivery$', views.calculator_get_deliveries_amount, name='calculator_get_deliveries_amount'),
    re_path(r'^otp/send/$', views.send_otp, name='send_otp'),
    re_path(r'^otp/verify/$', views.verify_otp, name='verify_otp'),
    re_path(r'^developer/loophole/$', views.loop_hole, name='loop_hole'),
]