from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    # This makes the list view nice and informative
    list_display = ('name', 'user', 'cost', 'frequency', 'next_billing_date', 'is_active')

    # Allows you to filter by active status or billing cycle in the admin
    list_filter = ('is_active', 'frequency')

    # Helps you find subscriptions quickly
    search_fields = ('name', 'user__username')