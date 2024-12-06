import re
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    mobile = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    def validate_email(self, email):
        email = email.lower()

        # Check if the email already exists
        user = User.objects.filter(email=email).first()
        if user:
            if user.is_verified:
                raise serializers.ValidationError("email already exists")
            else:
                user.delete()

        return email

    def validate_mobile(self, mobile):
        if not mobile.isdigit() or len(mobile) != 10:
            raise serializers.ValidationError("Invalid number")

        if User.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError("mobile number already exists")

        return mobile

    def validate_password(self, password):
        pattern = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        )
        if not re.match(pattern, password):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long, include one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return password

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class OTPSerializer(serializers.Serializer):
    """
    Serializer for handling OTP-related operations, used in two distinct scenarios:

    1. Send OTP:
       - In this scenario, the 'email' field is required, and the 'otp' field is optional.
       - The serializer validates the provided 'email' for sending an OTP to the user.

    2. Verify OTP:
       - In this scenario, both the 'email' and 'otp' fields are required.
       - The serializer ensures that 'otp' validation is required (indicated by the 'otp_field' context).

    Context:
        - 'otp_field' (bool): A boolean flag passed via the serializer context to indicate whether
          OTP validation is required. When 'True', the serializer ensures the 'otp' field is present.
    """

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4, required=False)

    def validate(self, data):
        # Check the context for the 'otp_field' flag
        is_otp = self.context.get("otp_field")

        # If OTP validation is required, ensure the otp field is not empty
        if is_otp and not data.get("otp"):
            raise serializers.ValidationError({"otp": "OTP is required"})

        return data
