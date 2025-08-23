from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from . models import Traveller,Profile

import requests


@receiver(user_logged_in)
def send_login_email(sender, request, user, **kwargs):

    send_mail(
        subject='Login Alert - SmartVoyager',
        message=(
            f"Hi {user.username},\n\n"
            f"You just logged into your SmartVoyager account on {now().strftime('%Y-%m-%d %H:%M:%S')}.\n"
            f"If this wasn't you, please reset your password immediately."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True
    )


@receiver(post_save, sender=Profile)
def create_traveller_for_profile(sender, instance, created, **kwargs):

    if created and instance.role == 'User':

        Traveller.objects.create(profile =instance,
                                 name=f'{instance.first_name} {instance.last_name}',
                                 email=instance.email)