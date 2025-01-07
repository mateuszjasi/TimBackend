from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .permissions import IsAdmin


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        if IsAuthenticated and IsAdmin:
            is_staff = validated_data.pop('is_staff', False)
            is_superuser = validated_data.pop('is_superuser', False)
        else:
            is_staff = False
            is_superuser = False

        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        return user

    def update(self, instance, validated_data):
        if IsAuthenticated and IsAdmin:
            is_staff = validated_data.pop('is_staff', instance.is_staff)
            is_superuser = validated_data.pop('is_superuser', instance.is_superuser)
        else:
            is_staff = instance.is_staff
            is_superuser = instance.is_superuser

        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.is_staff = is_staff
        instance.is_superuser = is_superuser
        instance.save()
        return instance