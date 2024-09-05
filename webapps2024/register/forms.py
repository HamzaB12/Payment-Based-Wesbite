from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from register.models import UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    currency = forms.ChoiceField(choices=UserProfile.CURRENCY_CHOICES, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2", "currency"]

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            user.profile.currency = self.cleaned_data['currency']
            user.profile.save()
            print("User saved in DB")
        else:
            print("User couldn't be saved")
        return user