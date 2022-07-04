from datetime import time, timedelta
from django.utils import timezone
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse
from .models import ExtraLess, Route, User, Subscription, Vacation, UserType, Otp, Payment, Purchase
from .views import getEndBalanceOfMonth, last_day_of_month, getPurchaseOfMonth, getPaymentOfMonth
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter


# bill notification filter
class BillNotificationFilter(SimpleListFilter):
    title = 'Bill Notification'
    parameter_name = 'bill_notification'

    def lookups(self, request, model_admin):
        return [('sent', 'Sent'), ('not sent', 'Not Sent')]

    def queryset(self, request, queryset):
        if self.value() == 'sent':
            date = timezone.localtime(timezone.now())
            return queryset.filter(bill_send_date__year=date.strftime('%Y'), bill_send_date__month=date.strftime('%m'))
        elif self.value() == 'not sent':
            date = timezone.localtime(timezone.now())
            return queryset.exclude(bill_send_date__year=date.strftime('%Y'), bill_send_date__month=date.strftime('%m'))




# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ( 'delivery_name', 'name', 'transactions_link', 'mobile', 'payment_mode', 'route', 'user_type', 'balance3', 'payment2', 'purchase2', 'balance2', 'payment1', 'balance2Updated', 'balance1', 'bill_link', 'reminder_link', 'prepaid_link', 'bill_send_date', 'status')
    search_fields = ('delivery_name', 'mobile', 'email')
    list_editable = ('status',)
    ordering = ('route_order',)
    list_filter = (('user_type', RelatedDropdownFilter), ('route', RelatedDropdownFilter), 'address_type', BillNotificationFilter, 'status')

    def transactions_link(self, obj):
        return format_html('<a target="_blank" href="%s">View</a>' % ('/transactions/' + str(obj.id)))
    transactions_link.short_description = "Transactions"

    def bill_link(self, obj):
        return format_html('<a target="_blank" href="%s">Send</a>' % ('/send/bill?uid=' + str(obj.id)))
    bill_link.short_description = "Bill"

    def reminder_link(self, obj):
        return format_html('<a target="_blank" href="%s">Send</a>' % ('/send/reminder?uid=' + str(obj.id)))
    reminder_link.short_description = "Reminder"

    def prepaid_link(self, obj):
        return format_html('<a target="_blank" href="%s">Send</a>' % ('/send/prepaid-link?uid=' + str(obj.id)))
    prepaid_link.short_description = "Prepaid Link"

    def balance1(self, obj):
        last_day = last_day_of_month(timezone.localtime(timezone.now()))
        return getEndBalanceOfMonth(last_day, obj)
    
    balance1.short_description = 'Balance: Today'

    def payment1(self, obj):
        last_day = last_day_of_month(timezone.localtime(timezone.now()))
        return getPaymentOfMonth(last_day, obj)
    
    payment1.short_description = 'Payment : ' + timezone.localtime(timezone.now()).strftime('%b')
    
    def balance2(self, obj):
        last_day = last_day_of_month(timezone.localtime(timezone.now()))
        last_day = last_day.replace(day=1)
        last_day = last_day - timedelta(days=1)
        return getEndBalanceOfMonth(last_day, obj)
    
    balance2.short_description = 'Balance: ' + last_day_of_month((timezone.localtime(timezone.now()).replace(day=1) - timedelta(days=1))).strftime('%b')

    def balance2Updated(self, obj):
        last_day = last_day_of_month(timezone.localtime(timezone.now()))
        last_day = last_day.replace(day=1)
        last_day = last_day - timedelta(days=1)
        balance2 =  getEndBalanceOfMonth(last_day, obj)
        last_day = last_day_of_month(timezone.localtime(timezone.now()))
        payment1 =  getPaymentOfMonth(last_day, obj)
        return balance2 + payment1
    
    balance2Updated.short_description = 'Updated Balance: ' + last_day_of_month((timezone.localtime(timezone.now()).replace(day=1) - timedelta(days=1))).strftime('%b')

    payment1.short_description = 'Payment : ' + timezone.localtime(timezone.now()).strftime('%b')

    def purchase2(self, obj):
        last_day = last_day_of_month(timezone.localtime(timezone.now()))
        last_day = last_day.replace(day=1)
        last_day = last_day - timedelta(days=1)
        return getPurchaseOfMonth(last_day, obj)
    
    purchase2.short_description = 'Purchase: ' + last_day_of_month((timezone.localtime(timezone.now()).replace(day=1) - timedelta(days=1))).strftime('%b')
    
    def payment2(self, obj):
        last_day = last_day_of_month(timezone.localtime(timezone.now()))
        last_day = last_day.replace(day=1)
        last_day = last_day - timedelta(days=1)
        return getPaymentOfMonth(last_day, obj)
    
    payment2.short_description = 'Payment: ' + last_day_of_month((timezone.localtime(timezone.now()).replace(day=1) - timedelta(days=1))).strftime('%b')

    def balance3(self, obj):
        last_day = last_day_of_month(timezone.localtime(timezone.now()))
        last_day = last_day.replace(day=1)
        last_day = last_day - timedelta(days=1)
        last_day = last_day.replace(day=1)
        last_day = last_day - timedelta(days=1)
        return getEndBalanceOfMonth(last_day, obj)
    
    balance3.short_description = 'Balance: ' + last_day_of_month(((timezone.localtime(timezone.now()).replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=1))).strftime('%b')



# Vacation admin model.
class VacationAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    list_display = ('user', 'vacation_start_date', 'vacation_end_date')
    list_filter = (('user', AutocompleteListFilter),)
    autocomplete_fields = ['user']

    def vacation_start_date(self, obj):
        return obj.start_date.strftime("%b %d, %Y")

    def vacation_end_date(self, obj):
        if obj.end_date is None:
            return None
        else:
            return obj.end_date.strftime("%b %d, %Y")


# Subscription admin model.
class SubscriptionAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    list_display = ('user', 'sub_type', 'subscription_start_date', 'subscription_end_date')
    list_filter = (('user', AutocompleteListFilter), 'sub_type')
    autocomplete_fields = ['user']

    def subscription_start_date(self, obj):
        return obj.start_date.strftime("%b %d, %Y")

    def subscription_end_date(self, obj):
        if obj.end_date is None:
            return None
        else:
            return obj.end_date.strftime("%b %d, %Y")


# ExtraLess admin model.
class ExtraLessAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    list_display = ('user', 'quantity', 'extraless_start_date', 'extraless_end_date')
    list_filter = (('user', AutocompleteListFilter),)
    autocomplete_fields = ['user']

    def extraless_start_date(self, obj):
        return obj.start_date.strftime("%b %d, %Y")

    def extraless_end_date(self, obj):
        if obj.end_date is None:
            return None
        else:
            return obj.end_date.strftime("%b %d, %Y")

# Payment admin model.
class PaymentAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_date', 'description', 'balance')
    list_filter = (('user', AutocompleteListFilter), 'paid')
    autocomplete_fields = ['user']

    def payment_date(self, obj):
        return obj.date.strftime("%b %d, %Y")

# Purchase admin model.
class PurchaseAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    list_display = ('user', 'quantity', 'amount', 'purchase_date', 'balance')
    list_filter = (('user', AutocompleteListFilter),)
    autocomplete_fields = ['user']

    def purchase_date(self, obj):
        return obj.date.strftime("%b %d, %Y")





admin.site.register(User, UserAdmin)

admin.site.register(Vacation, VacationAdmin)   
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(ExtraLess, ExtraLessAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Purchase, PurchaseAdmin)

admin.site.register(Otp)
admin.site.register(UserType)
admin.site.register(Route)