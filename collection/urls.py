from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login', views.login, name="collection_login"),
    path('', views.collection, name="cash_collection_home"),
    path('delete', views.delete_collection, name="delete_collection"),
    path('collected', views.get_collected_payments, name="get_collected_payments"),
    path('report', views.collection_report, name="cash_collection_report"),
    path('handover', views.collection_hand_over, name="cash_collection_hand_over"),
    path('expenses', views.collection_expenses, name="cash_collection_expenses"),
    path('report/generate', views.collection_report_generator, name="collection_report_generator"),
    path('handover/generate', views.handover_report_generator, name="handover_report_generator"),
    path('expenses/generate', views.expenses_report_generator, name="expenses_report_generator"),
    path('login/validation', views.login_validation, name="collection_login_validation"),
    path('new', views.add_collection, name="add_collection"),
    path('handover/new', views.add_handover, name="add_handover"),
    path('expenses/new', views.add_expenses, name="add_expenses"),
    path('handover/delete', views.delete_handover, name="delete_handover"),
    path('expenses/delete', views.delete_expenses, name="delete_expenses")
]