from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from payapp.forms import PaymentForm, RequestForm
from payapp.models import Notifications, Transaction
from payapp.services import make_payment, request_payment
from register.models import UserProfile


@login_required
def index(request):
    payment_form = PaymentForm(request.POST or None)
    request_form = RequestForm(request.POST or None)
    if request.method == "POST":
        if "make_payment" in request.POST and payment_form.is_valid():
            recipient_email = payment_form.cleaned_data['recipient_email']
            payed_amount = payment_form.cleaned_data['payed_amount']
            success, message = make_payment(request.user.email, recipient_email, payed_amount)
            if success == True:
                messages.success(request, message)
            else:
                messages.error(request, message)
        elif "request_payment" in request.POST and request_form.is_valid():
            payer_email = request_form.cleaned_data['payer_email']
            requested_amount = request_form.cleaned_data['requested_amount']
            success, message = request_payment(payer_email, request.user.email, requested_amount)
            if success == True:
                messages.success(request, message)
            else:
                messages.error(request, message)
    return render(request, 'payapp/payapp.html', {'payment_form':payment_form, 'request_form':request_form})

@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    notifications = Notifications.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(recipient=request.user)
    transactions = transactions.order_by('-transaction_date')
    context = {
        'user': request.user,
        'profile': user_profile,
        'notifications': notifications,
        'transactions': transactions,
    }
    return render(request, "payapp/dashboard.html", context)

@login_required
@require_POST
def delete_notification(request, notification_id):
    print(f"button delete pressed for notification {notification_id}")
    try:
        notification = Notifications.objects.get(notification_id=notification_id, user=request.user)
        notification.delete()
        messages.success(request, "Notification deleted successfully")
    except Notifications.DoesNotExist:
        messages.error(request, "Notification not found")
    return redirect('dashboard')

@login_required
@transaction.atomic
@require_POST
def accept_payment(request, notification_id):
    try:
        notification = Notifications.objects.get(notification_id=notification_id, user=request.user)
        transaction = notification.transaction

        if transaction and transaction.status == 'P':

            success, message = make_payment(request.user.email, transaction.recipient.email, transaction.amount)
            if success:
                transaction.status = 'C'
                transaction.save()

                Notifications.objects.create(
                    user=transaction.recipient,
                    transaction=transaction,
                    message=f"Payment of {transaction.amount} accepted by {request.user.username}",
                    type='S'
                )

                messages.success(request, "Payment accepted successfully.")
            else:
                messages.error(request, message)
            messages.error(request, "Invalid transaction or transaction already processed.")
    except Notifications.DoesNotExist:
        messages.error(request, "Notification not found.")

    return redirect('dashboard')

@login_required
@transaction.atomic
@require_POST
def refuse_payment(request, notification_id):
    try:
        notification = Notifications.objects.get(notification_id=notification_id, user=request.user)

        if notification.transaction:
            transaction = notification.transaction
            transaction.status = 'F'
            transaction.save()

            Notifications.objects.create(
                user=transaction.sender,
                message=f"{request.user.username} has declined your payment request of {transaction.amount}",
                type='F'
            )
            messages.success(request, "Payment refused successfully.")

    except Notifications.DoesNotExist:
        messages.error(request, "Notification not found.")

    return redirect('dashboard')