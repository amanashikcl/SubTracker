from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Subscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'cost', 'frequency', 'next_billing_date', 'start_date', 'reminder_days_before']

        widgets = {
            # Added 'input input-bordered' and removed manual border/padding
            'next_billing_date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'e.g. Netflix'}),
            'cost': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            # Selects use the 'select select-bordered' class
            'frequency': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'reminder_days_before': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'input input-bordered w-full',
        'placeholder': 'Enter your email'
    }))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)