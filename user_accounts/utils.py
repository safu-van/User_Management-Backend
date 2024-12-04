import random
from django.conf import settings
from django.core.mail import send_mail

from .models import UserOTP


def generate_otp_for_user(user):
    # Generate otp
    otp = random.randint(1000, 9999)

    # Save otp to database
    otp_instance, _  = UserOTP.objects.get_or_create(user=user)
    otp_instance.otp = otp
    otp_instance.save()

    return otp


def send_otp_via_email(user_email, otp):
    subject = "User Management OTP Code"
    message = f"Your OTP code is : {otp}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)