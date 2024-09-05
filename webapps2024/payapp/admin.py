from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Transaction, Notifications

User = get_user_model()

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'sender', 'recipient', 'amount', 'transaction_date', 'status')
    list_filter = ('status', 'transaction_date')
    search_fields = ('transaction_id', 'sender__username', 'recipient__username')

admin.site.register(Transaction, TransactionAdmin)


class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'user', 'message', 'notification_date', 'type')
    list_filter = ('notification_date', 'type')
    search_fields = ('notification_id', 'user__username')

admin.site.register(Notifications, NotificationsAdmin)