from django.shortcuts import render, redirect
from .forms import RegisterForm

# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            print("Form is valid")
            form.save()
        else:
            print("Form is invalid")
        return redirect("/")
    else:
        print("Empty form")
        form = RegisterForm()
    return render(response, "register/register.html", {"form": form})