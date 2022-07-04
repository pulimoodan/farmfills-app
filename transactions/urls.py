from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name="transactions_home"),
    path('get/transactions', views.get_transactions_bill, name="get_transactions_bill")
]