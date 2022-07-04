from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login', views.login, name="manager_login"),
    path('logout', views.logout, name="manager_logout"),
    path('login/validate', views.login_validation, name="manager_login_validation"),
    path('', views.dashboard, name="manager_dashboard"),
    path('message/<int:id>/send/<int:uid>', views.send_message_customers, name="manager_send_message_customers"),

    # view
    path('customers/list', views.customers_list, name="manager_customers_list"),
    path('customers/followup', views.customers_followup, name="manager_customers_followup"),
    path('customers/transactions/<int:id>', views.customer_transactions, name="manager_customers_transactions"),
    path('customers/subscriptions', views.customer_subscriptions, name="manager_customers_subscriptions"),
    path('customers/extraless', views.customer_extraless, name="manager_customers_extraless"),
    path('customers/vacations', views.customer_vacations, name="manager_customers_vacations"),
    path('customers/transactions/purchases', views.customers_purchases, name="manager_customers_purchases"),
    path('ajax/datatables/payments', views.manager_datatable_ajax_customers_payments, name="manager_datatable_ajax_customers_payments"),
    path('customers/transactions/payments', views.customers_payments, name="manager_customers_payments"),
    path('customers/transactions/refunds', views.customers_refunds, name="manager_customers_refunds"),
    path('customers/transactions/extras', views.customers_extras, name="manager_customers_extras"),
    path('message', views.message, name="manager_message"),
    path('message/<int:id>/customers', views.message_customers, name="manager_message_customers"),
    path('route/order', views.route_ordering, name="manager_route_ordering"),

    # ajax
    path('ajax/datatables/customers', views.manager_datatable_ajax_customers_list, name="manager_datatable_ajax_customers_list"),
    path('ajax/datatables/customers/followup', views.manager_datatable_ajax_customers_followup, name="manager_datatable_ajax_customers_followup"),
    path('ajax/datatables/subscriptions', views.manager_datatable_ajax_customers_subscriptions, name="manager_datatable_ajax_customers_subscriptions"),
    path('ajax/datatables/extraless', views.manager_datatable_ajax_customers_extraless, name="manager_datatable_ajax_customers_extraless"),
    path('ajax/datatables/vacations', views.manager_datatable_ajax_customers_vacations, name="manager_datatable_ajax_customers_vacations"),
    path('ajax/datatables/purchases', views.manager_datatable_ajax_customers_purchases, name="manager_datatable_ajax_customers_purchases"),
    path('ajax/datatables/refunds', views.manager_datatable_ajax_customers_refunds, name="manager_datatable_ajax_customers_refunds"),
    path('ajax/datatables/extras', views.manager_datatable_ajax_customers_extras, name="manager_datatable_ajax_customers_extras"),
    path('ajax/datatables/message', views.manager_datatable_ajax_message, name="manager_datatable_ajax_message"),
    path('ajax/message/customers/date', views.get_message_date_of_customer, name="manager_get_message_date_of_customer"),
    path('ajax/message/customers/date', views.get_message_date_of_customer, name="admin_get_message_date_of_customer"),
    path('ajax/routes/route-order/save', views.save_route_order, name="manager_save_route_order"),
    path('ajax/routes/customers', views.get_customers_of_route, name="manager_get_customers_of_route"),
    path('ajax/routes/customers/change', views.change_customers_route, name="manager_change_customers_route"),
    path('ajax/routes/customers/assign', views.assign_customers_route, name="manager_assign_customers_route"),
    path('ajax/routes/customers/assignations/clear', views.clear_customers_route_assignation, name="manager_clear_customers_route_assignation"),
    path('ajax/routes/customers/assignations/clear/all', views.clear_all_route_assignation, name="manager_clear_all_route_assignation"),
    path('ajax/delivery/info', views.get_delivery_info, name="manager_get_delivery_info"),

    # create
    path('customers/create', views.customers_create, name="manager_customers_create"),
    path('subscriptions/create', views.subscriptions_create, name="manager_subscriptions_create"),
    path('extraless/create', views.extraless_create, name="manager_extraless_create"),
    path('vacations/create', views.vacations_create, name="manager_vacations_create"),
    path('payments/create', views.payments_create, name="manager_payments_create"),
    path('refunds/create', views.refunds_create, name="manager_refunds_create"),
    path('extras/create', views.extras_create, name="manager_extras_create"),
    path('message/create', views.message_create, name="manager_message_create"),

    #edit
    path('customers/edit/<int:id>', views.customers_edit, name="manager_customers_edit"),
    path('subscriptions/<int:id>', views.subscriptions_edit, name="manager_subscriptions_edit"),
    path('extraless/<int:id>', views.extraless_edit, name="manager_extraless_edit"),
    path('vacations/<int:id>', views.vacations_edit, name="manager_vacations_edit"),
    path('payments/edit/<int:id>', views.payments_edit, name="manager_payments_edit"),
    path('refunds/edit/<int:id>', views.refunds_edit, name="manager_refunds_edit"),
    path('extras/edit/<int:id>', views.extras_edit, name="manager_extras_edit"),

    # delete
    path('customers/delete/<int:id>', views.customer_delete, name="manager_customer_delete"),
    path('subscriptions/delete/<int:id>', views.subscription_delete, name="manager_subscription_delete"),
    path('extraless/delete/<int:id>', views.extraless_delete, name="manager_extraless_delete"),
    path('vacation/delete/<int:id>', views.vacation_delete, name="manager_vacation_delete"),
    path('payments/delete/<int:id>', views.payment_delete, name="manager_payment_delete"),
    path('refunds/delete/<int:id>', views.refund_delete, name="manager_refund_delete"),
    path('extras/delete/<int:id>', views.extra_delete, name="manager_extra_delete"),
    path('message/delete/<int:id>', views.delete_message, name="manager_delete_message"),

    # end
    path('subscriptions/end/<int:id>', views.subscription_end, name="manager_subscription_end"),
    path('extraless/end/<int:id>', views.extraless_end, name="manager_extraless_end"),
    path('vacations/end/<int:id>', views.vacation_end, name="manager_vacation_end"),
]