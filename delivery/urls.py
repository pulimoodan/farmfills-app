from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login', views.login, name="delivery_login"),
    path('', views.delivery, name="delivery_list"),
    path('notifications', views.notification, name="delivery_notification"),
    path('allowance', views.allowance, name="delivery_allowance"),
    path('start', views.start_delivery, name="start_delivery"),
    path('end', views.end_delivery, name="end_delivery"),
    path('login/validation', views.login_validation, name="delivery_login_validation")
]