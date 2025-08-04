from django.forms import ModelForm, Select
from users.models import User, Payment, Refund, Extra, Subscription, ExtraLess, Vacation, FollowUp, Message, Staff, Manager, Route
from django import forms

# Create the form class.
class StaffForm(ModelForm):
    class Meta:
        model = Staff
        exclude = ['id', 'ip']


class ManagerForm(ModelForm):
    class Meta:
        model = Manager
        exclude = ['id']

class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ['id', 'location', 'bill_send_date', 'last_transaction', 'balance']

class ManagerUserForm(ModelForm):
    def __init__(self, routes, *args, **kwargs):
        super (ManagerUserForm, self ).__init__(*args,**kwargs) # populates the post
        self.fields['route'].queryset = routes

    class Meta:
        model = User
        exclude = ['id', 'location', 'bill_send_date', 'last_transaction', 'balance']

class MessageForm(ModelForm):
    class Meta:
        model = Message
        exclude = ['id', 'created_date']

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        exclude = ['id', 'payment_id', 'order_id', 'transaction_id']
        auttocomplete_fields = ['user',]
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'date'}),
        }

class ManagerPaymentForm(ModelForm):
    def __init__(self, routes, *args, **kwargs):
        super (ManagerPaymentForm, self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].queryset = User.objects.filter(route__in=routes)

    class Meta:
        model = Payment
        exclude = ['id', 'payment_id', 'order_id', 'transaction_id']
        auttocomplete_fields = ['user',]
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'date'}),
        }

class RefundForm(ModelForm):
    class Meta:
        model = Refund
        exclude = ['id', 'transaction_id']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date'}),
        }

class ManagerRefundForm(ModelForm):
    def __init__(self, routes, *args, **kwargs):
        super (ManagerRefundForm, self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].queryset = User.objects.filter(route__in=routes)

    class Meta:
        model = Refund
        exclude = ['id', 'transaction_id']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date'}),
        }

class ExtraForm(ModelForm):
    class Meta:
        model = Extra
        exclude = ['id', 'transaction_id']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date'}),
        }

class ManagerExtraForm(ModelForm):
    def __init__(self, routes, *args, **kwargs):
        super (ManagerExtraForm, self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].queryset = User.objects.filter(route__in=routes)

    class Meta:
        model = Extra
        exclude = ['id', 'transaction_id']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date'}),
        }

class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        exclude = ['id', ]
        widgets = {
            'start_date': forms.TextInput(attrs={'type': 'date'}),
            'end_date': forms.TextInput(attrs={'type': 'date'}),
        }

class ManagerSubscriptionForm(ModelForm):
    def __init__(self, routes, *args, **kwargs):
        super (ManagerSubscriptionForm, self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].queryset = User.objects.filter(route__in=routes)

    class Meta:
        model = Subscription
        exclude = ['id', ]
        widgets = {
            'start_date': forms.TextInput(attrs={'type': 'date'}),
            'end_date': forms.TextInput(attrs={'type': 'date'}),
        }

class ExtraLessForm(ModelForm):
    class Meta:
        model = ExtraLess
        exclude = ['id', ]
        widgets = {
            'start_date': forms.TextInput(attrs={'type': 'date'}),
            'end_date': forms.TextInput(attrs={'type': 'date'}),
        }

class ManagerExtraLessForm(ModelForm):
    def __init__(self, routes, *args, **kwargs):
        super (ManagerExtraLessForm, self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].queryset = User.objects.filter(route__in=routes)

    class Meta:
        model = ExtraLess
        exclude = ['id', ]
        widgets = {
            'start_date': forms.TextInput(attrs={'type': 'date'}),
            'end_date': forms.TextInput(attrs={'type': 'date'}),
        }

class VacationForm(ModelForm):
    class Meta:
        model = Vacation
        exclude = ['id', ]
        widgets = {
            'start_date': forms.TextInput(attrs={'type': 'date'}),
            'end_date': forms.TextInput(attrs={'type': 'date'}),
        }

class ManagerVacationForm(ModelForm):
    def __init__(self, routes, *args, **kwargs):
        super (ManagerVacationForm, self ).__init__(*args,**kwargs) # populates the post
        self.fields['user'].queryset = User.objects.filter(route__in=routes)

    class Meta:
        model = Vacation
        exclude = ['id', ]
        widgets = {
            'start_date': forms.TextInput(attrs={'type': 'date'}),
            'end_date': forms.TextInput(attrs={'type': 'date'}),
        }


class FollowUpForm(ModelForm):
    class Meta:
        model = FollowUp
        exclude = ['id', 'nex_date', 'note']