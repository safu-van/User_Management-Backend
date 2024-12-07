from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_img_id", "name", "email", "mobile", "bio"]
