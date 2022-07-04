from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login', views.login, name="vendor_login"),
    path('', views.today, name="vendor_today"),
    path('tomorrow', views.tomorrow, name="vendor_tomorrow"),
    path('login/validation', views.login_validation, name="vendor_login_validation")
]