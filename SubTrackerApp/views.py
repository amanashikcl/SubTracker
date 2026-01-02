from celery import shared_task
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import SubscriptionForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from decimal import Decimal
from .tasks import send_welcome_email, send_signup_email
from .models import Subscription


@login_required  # This ensures only logged-in users can access this page
def add_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False) # Pause saving for a moment...
            subscription.user = request.user       # ...so we can attach the logged-in user
            subscription.save()
            send_welcome_email.delay(request.user.email, subscription.name)
            return redirect('dashboard')           # Redirect to a dashboard (we will build this next)
    else:
        form = SubscriptionForm()

    return render(request, 'add_subscription.html', {'form': form})





from datetime import date, timedelta
from dateutil.relativedelta import relativedelta  # Ensure this is installed: pip install python-dateutil


@login_required
def dashboard(request):
    # 1. Fetch all active subscriptions
    subs = request.user.subscriptions.filter(is_active=True).order_by('next_billing_date')
    today = date.today()

    # 2. AUTO-ROLLOVER LOGIC: Update dates that have already passed
    for sub in subs:
        updated = False
        # If the bill date is in the past, move it to the next future occurrence
        while sub.next_billing_date < today:
            if sub.frequency == 'weekly':
                sub.next_billing_date += timedelta(days=7)
            elif sub.frequency == 'monthly':
                sub.next_billing_date += relativedelta(months=1)
            elif sub.frequency == 'yearly':
                sub.next_billing_date += relativedelta(years=1)
            updated = True

        if updated:
            sub.save()  # Commit the new future date to the database

    # 3. Calculate totals (using updated dates if necessary)
    total_monthly_spend = sum(sub.monthly_equivalent for sub in subs)

    # 4. Prepare Chart Data
    sub_names = [sub.name for sub in subs]
    sub_costs = [float(sub.monthly_equivalent) for sub in subs]

    # 5. UPCOMING REMINDER LOGIC
    # Get the subscription due soonest (since we ordered by next_billing_date)
    upcoming_sub = subs.first()
    show_alert = False

    if upcoming_sub:
        days_until = (upcoming_sub.next_billing_date - today).days
        upcoming_sub.days_until = days_until
        # Show alert if due within 7 days
        if 0 <= days_until <= 7:
            show_alert = True

    context = {
        'subscriptions': subs,
        'total_cost': round(total_monthly_spend, 2),
        'sub_names': sub_names,
        'sub_costs': sub_costs,
        'upcoming_sub': upcoming_sub,
        'show_alert': show_alert,
        'today': today,  # Useful for highlighting "due today" in the template
    }

    return render(request, 'dashboard.html', context)


@login_required
def edit_subscription(request, id):
    # Get the specific subscription or return 404 if not found
    # We also check 'user=request.user' to ensure they can't edit someone else's sub!
    subscription = get_object_or_404(Subscription, id=id, user=request.user)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription)  # Load existing data
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        # Pre-fill the form with the current data
        form = SubscriptionForm(instance=subscription)

    # Re-use the same template as 'add', or create a new one if you prefer
    return render(request, 'add_subscription.html', {'form': form, 'is_edit': True})


@login_required
def delete_subscription(request, id):
    subscription = get_object_or_404(Subscription, id=id, user=request.user)

    if request.method == 'POST':
        subscription.delete()
        return redirect('dashboard')

    # We ask for confirmation before deleting
    return render(request, 'delete_confirm.html', {'subscription': subscription})


from .forms import UserRegisterForm # Import your new custom form



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST) # Use the custom one
        if form.is_valid():
            user = form.save()
            send_signup_email.delay(user.email, "SubTracker")
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('dashboard')