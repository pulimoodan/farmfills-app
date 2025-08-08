from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login', views.login, name="dispatch_login"),
    path('', views.dispatch, name="dispatch_home"),
    # path('notifications', views.notification, name="delivery_notification"),
    # path('allowance', views.allowance, name="delivery_allowance"),
    path('start', views.start_dispatch, name="start_dispatch"),
    path('end', views.end_dispatch, name="end_dispatch"),
    # path('end', views.end_delivery, name="end_delivery"),
    path('login/validation', views.login_validation, name="dispatch_login_validation")
]
