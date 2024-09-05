from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('F', 'Failed'),
    )

    transaction_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')


class Notifications(models.Model):
    TYPE_CHOICES = (
        ('P', 'Payment received'),
        ('R', 'Payment request'),
        ('S', 'Payment sent'),
        ('A', 'System message'),
        ('F', 'Payment failed'),
        ('I', 'Information')
    )

    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    transaction = models.ForeignKey(Transaction, related_name='notifications', on_delete=models.SET_NULL,
                                null=True, blank=True)
    notification_date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='I')