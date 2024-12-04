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
        """
        - Convert email to lowercase.
        - Check if the email already exists.
        - If the email exists but is not verified, delete the user.
        """
        email = email.lower()
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
        # At least one uppercase letter, one lowercase letter, one digit, one special character, and minimum 8 characters
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
        user = User.objects.create_user(
            name=validated_data["name"],
            email=validated_data["email"],
            mobile=validated_data["mobile"],
            password=validated_data["password"],
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
