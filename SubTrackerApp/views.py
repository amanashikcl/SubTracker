from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SubscriptionForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from decimal import Decimal

from .models import Subscription


@login_required  # This ensures only logged-in users can access this page
def add_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False) # Pause saving for a moment...
            subscription.user = request.user       # ...so we can attach the logged-in user
            subscription.save()                    # Now save to DB
            return redirect('dashboard')           # Redirect to a dashboard (we will build this next)
    else:
        form = SubscriptionForm()

    return render(request, 'add_subscription.html', {'form': form})


@login_required
def dashboard(request):
    # 1. Fetch all active subscriptions
    # (Assuming related_name='subscriptions' is set in your Model)
    subs = request.user.subscriptions.filter(is_active=True)

    # 2. Calculate totals
    total_monthly_spend = sum(sub.monthly_equivalent for sub in subs)

    # 3. PREPARE CHART DATA (This was missing!)
    # Create simple lists of names and costs for the frontend to digest
    sub_names = [sub.name for sub in subs]

    # We use 'monthly_equivalent' so the chart compares apples-to-apples
    # We convert to float because JavaScript doesn't understand Python Decimals
    sub_costs = [float(sub.monthly_equivalent) for sub in subs]

    context = {
        'subscriptions': subs,
        'total_cost': round(total_monthly_spend, 2),
        'sub_names': sub_names,  # <--- Now passing this
        'sub_costs': sub_costs,  # <--- Now passing this
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


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})