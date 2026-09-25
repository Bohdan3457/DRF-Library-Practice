from django.contrib.auth import get_user_model
from rest_framework import serializers

user = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
            "first_name",
            "last_name"
        )
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 10,
                "style": {"input_type": "password"}
            }
        }

    def create(self, validated_data):
        return user.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
