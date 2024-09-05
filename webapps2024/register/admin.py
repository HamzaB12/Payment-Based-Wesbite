from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'balance')
    list_filter = ('currency',)
    search_fields = ('user__username', 'currency')

admin.site.register(UserProfile, UserProfileAdmin)