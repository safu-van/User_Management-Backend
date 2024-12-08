from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_img_id", "name", "email", "mobile", "bio"]
        read_only_fields = ["email"]

        def update(self, instance, validated_data):
            instance.profile_img_id = validated_data.get(
                "profile_img_id", instance.profile_img_id
            )
            instance.name = validated_data.get("name", instance.name)
            instance.mobile = validated_data.get("mobile", instance.mobile)
            instance.bio = validated_data.get("bio", instance.bio)
            instance.save()

            return instance
