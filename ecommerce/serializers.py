from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    order_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'is_active', 'is_staff', 'created_at', 'updated_at', 'order_count',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'order_count',
        ]

    def get_order_count(self, obj):
        return obj.order.count()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)

    class Meta:
        model = User
        fields = [
            'name', 'email', 'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(
            **validated_data
        )

        user.set_password(password)
        user.save()

        return user