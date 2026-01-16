from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail

from SubTracker import settings


@shared_task
def send_email_task(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'subtrackeralert@gmail.com', # Your verified sender
        recipient_list,
        fail_silently=False,
    )




@shared_task
def send_welcome_email(user_email, sub_name):
    send_mail(
        subject=f"Added: {sub_name}",
        message=f"Success! You are now tracking your {sub_name} subscription.",
        from_email='subtrackeralert@gmail.com',
        recipient_list=[user_email],
        fail_silently=False,
    )

@shared_task
def send_signup_email(user_email, sub_name):
    send_mail(
        subject=f"SignUp successful!",
        message=f"Thank you for signing up for SubTracker! {sub_name}",
        from_email='subtrackeralert@gmail.com',
        recipient_list=[user_email],
        fail_silently=False,
    )

from django.utils import timezone
from .models import Subscription


@shared_task
def daily_renewal_check():
    from .models import Subscription

    today = timezone.now().date()

    # This logic finds subs where: next_billing_date - reminder_days_before = today
    # Example: Billed on Jan 10th, Remind 3 days before -> Notify on Jan 7th
    subs_to_notify = Subscription.objects.filter(is_active=True)

    for sub in subs_to_notify:
        # Calculate when this specific sub should send an alert
        trigger_date = sub.next_billing_date - timedelta(days=sub.reminder_days_before)

        if trigger_date == today:
            send_mail(
                subject=f"Upcoming Renewal: {sub.name}",
                message=f"Hi {sub.user.username}, your {sub.name} subscription ({sub.cost}) renews on {sub.next_billing_date}.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[sub.user.email],
                fail_silently=False,
            )

    return f"Processed alerts for {today}"

@shared_task
def rollover_billing_dates():
    from .models import Subscription
    today = timezone.now().date()

    # Find active subs where the billing date has already passed
    expired_subs = Subscription.objects.filter(next_billing_date__lt=today, is_active=True)

    for sub in expired_subs:
        # This will trigger your calculate_initial_billing_date() logic again
        sub.next_billing_date = None
        sub.save()