from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login', views.login, name="followup_login"),
    path('', views.followup, name="followup_home"),
    path('login/validation', views.login_validation, name="followup_login_validation"),
    path('next-followup-date/change', views.change_next_followup_date, name="change_next_followup_date"),
    path('last-followup-date/change', views.change_last_followup_date, name="change_last_followup_date"),
    path('note/change', views.change_followup_note, name="change_followup_note"),
    path('get/bill', views.get_followup_bill, name="get_followup_bill")
]