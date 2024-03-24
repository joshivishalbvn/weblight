# users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone_number',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True},'id': {'read_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField()
    verify_password = serializers.CharField()

    def validate(self, data):
        password = data.get('password')
        verify_password = data.get('verify_password')
        if password != verify_password:
            raise serializers.ValidationError("Passwords do not match.")
        return data
