from django import forms
from .models import Subscription


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'cost', 'frequency', 'start_date', 'reminder_days_before']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'border p-2 rounded w-full'}),
            'name': forms.TextInput(attrs={'class': 'border p-2 rounded w-full', 'placeholder': 'e.g. Netflix'}),
            'cost': forms.NumberInput(attrs={'class': 'border p-2 rounded w-full'}),
            'frequency': forms.Select(attrs={'class': 'border p-2 rounded w-full'}),

            'reminder_days_before': forms.NumberInput(attrs={'class': 'border p-2 rounded w-full'}),
        }