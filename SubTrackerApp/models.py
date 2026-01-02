from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import date


class Subscription(models.Model):
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    # Link every subscription to a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')

    name = models.CharField(max_length=100, help_text="e.g. Netflix, Spotify")
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost per cycle")

    # We use start_date to calculate all future dates
    start_date = models.DateField(help_text="When did this subscription start?")

    # This field is crucial for our query: "Find subs due in 3 days"
    next_billing_date = models.DateField(blank=True, null=True)

    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='monthly')
    reminder_days_before = models.IntegerField(default=3, help_text="Days before to notify")
    # User Preferences
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Override the save method.
        If next_billing_date isn't set, calculate it based on the start_date.
        """
        self.next_billing_date = self.calculate_initial_billing_date()
        super().save(*args, **kwargs)

    def calculate_initial_billing_date(self):
        """
        Calculates the next upcoming billing date relative to today.
        """
        today = date.today()
        billing_date = self.start_date

        # If the start date is in the future, that is the next billing date
        if billing_date >= today:
            return billing_date

        # If start date is in the past, keep adding the frequency until we pass today
        while billing_date < today:
            if self.frequency == 'weekly':
                billing_date += relativedelta(weeks=1)
            elif self.frequency == 'monthly':
                billing_date += relativedelta(months=1)
            elif self.frequency == 'yearly':
                billing_date += relativedelta(years=1)

        return billing_date

    @property
    def monthly_equivalent(self):
        """
        Normalizes the cost to a monthly value for analytics.
        """
        # We need to import Decimal to avoid float math errors
        from decimal import Decimal

        if self.frequency == 'weekly':
            # 52 weeks / 12 months = 4.333 weeks per month
            return self.cost * Decimal(52) / Decimal(12)
        elif self.frequency == 'yearly':
            return self.cost / Decimal(12)
        else:
            # Default is monthly
            return self.cost

    @property
    def days_until_due(self):
        """Returns the number of days between today and the next bill."""
        if self.next_billing_date:
            delta = self.next_billing_date - date.today()
            return delta.days
        return None

    @property
    def is_near_due(self):
        """Returns True only if the bill is due within the user's reminder window."""
        days = self.days_until_due
        # Check if it's in the future and within the reminder threshold (e.g., 3 days)
        return days is not None and 0 <= days <= self.reminder_days_before

    def __str__(self):
        return f"{self.name} ({self.cost})"