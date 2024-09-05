from django import forms

from register.models import *


class PaymentForm(forms.Form):
    recipient_email = forms.EmailField(label="Recipient's Email", required=True)
    payed_amount = forms.DecimalField(label="Amount", max_digits=10, decimal_places=2, required=True)


class RequestForm(forms.Form):
    payer_email = forms.EmailField(label="Payer's email", required=True)
    requested_amount = forms.DecimalField(label="Amount", max_digits=10, decimal_places=2, required=True)