from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from payapp.models import User, Transaction, Notifications

# Rates picked on the 10/04/2024
CONVERSION_RATES = {
    ('USD', 'GBP'): 0.80,
    ('GBP', 'USD'): 1.25,
    ('EUR', 'USD'): 1.07,
    ('USD', 'EUR'): 0.93,
    ('GBP', 'EUR'): 1.17,
    ('EUR', 'GBP'): 0.86,
}

def convert_currency(amount, from_cur, to_cur):
    if from_cur == to_cur:
        return amount
    conv_rate =  CONVERSION_RATES.get((from_cur, to_cur))
    if conv_rate:
        return float(amount) * conv_rate
    else:
        raise ValueError("Conversion rate does not exist")

@transaction.atomic
def make_payment(sender_email, recipient_email, amount):
    try:
        if sender_email == recipient_email:
            return False, "Cannot send money to yourself."

        sender = User.objects.get(email=sender_email)
        recipient = User.objects.get(email=recipient_email)

        sender_currency = sender.profile.currency
        recipient_currency = recipient.profile.currency
        conv_amount = convert_currency(amount, sender_currency, recipient_currency)

        if sender.profile.balance >= amount:
            sender.profile.balance = F('balance') - amount
            recipient.profile.balance = F('balance') + conv_amount

            sender.profile.save()
            recipient.profile.save()

            Transaction.objects.create(
                sender=sender,
                recipient=recipient,
                amount=amount,
                transaction_date=timezone.now(),
                status='C'
            )

            Notifications.objects.create(
                user=sender,
                message=f"You sent {amount} to {recipient.username}.",
                notification_date=timezone.now(),
                type='S'
            )

            Notifications.objects.create(
                user=recipient,
                message=f"You received {conv_amount} from {sender.username}.",
                notification_date=timezone.now(),
                type='P'
            )

            return True, "Transaction successful."
        else:
            Transaction.objects.create(
                sender=sender,
                recipient=recipient,
                amount=amount,
                transaction_date=timezone.now(),
                status='F'
            )
            Notifications.objects.create(
                user=sender,
                message=f"You don't have enough fund to send {amount} to {recipient.username}",
                notification_date=timezone.now(),
                type='F'
            )
            return False, "Insufficient funds on your account."
    except ObjectDoesNotExist:
        return False, "User does not exist."
    except ValueError:
        return False, "Conversion between currency didn't work as expected."


@transaction.atomic
def request_payment(payer_email, recipient_email, amount):
    try:
        payer = User.objects.get(email=payer_email)
        recipient = User.objects.get(email=recipient_email)

        transaction = Transaction.objects.create(
            sender=payer,
            recipient=recipient,
            amount=amount,
            transaction_date=timezone.now(),
            status='P'
        )

        Notifications.objects.create(
            user=payer,
            transaction=transaction,
            message=f"You have been requested to pay {payer.profile.currency}{amount} to {recipient.username}",
            notification_date=timezone.now(),
            type='R'
        )

        Notifications.objects.create(
            user=recipient,
            transaction=transaction,
            message=f"You have requested {payer.username} to pay {payer.profile.currency}{amount} to you",
            notification_date=timezone.now(),
            type='R'
        )

        return True, f"Payment request of {payer.profile.currency}{amount} sent to {payer.username}"
    except ObjectDoesNotExist:
        return False, "Recipient does not exist."
    except:
        return False, "Something went wrong"
