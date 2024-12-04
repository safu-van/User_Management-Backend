from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)


# Custom manager for UserAccount model
class UserAccountManager(BaseUserManager):
    def create_user(self, name, email, mobile, password=None):
        if not email:
            raise ValueError("email is required")

        email = self.normalize_email(email).lower()

        user = self.model(
            name=name,
            email=email,
            mobile=mobile,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, name, email, mobile, password=None):
        user = self.create_user(
            name=name, email=email, mobile=mobile, password=password
        )
        user.is_verified = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


# Custom user model
class UserAccount(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Specify the custom manager for the model
    objects = UserAccountManager()

    USERNAME_FIELD = "email"  # Field used as the unique identifier for authentication
    REQUIRED_FIELDS = [
        "name",
        "mobile",
    ]  # Additional required fields when creating a superuser


# OTP model
class UserOTP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        # Define the expiration time (5 minutes)
        expiration_time = timedelta(minutes=5)

        # Calculate the expired time by adding the expiration time to the created_at time
        expired_time = self.created_at + expiration_time

        # If current time is greater than the expiration time, the OTP has expired
        return timezone.now() > expired_time
