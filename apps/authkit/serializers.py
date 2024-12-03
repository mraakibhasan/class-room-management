from rest_framework import serializers
from apps.authkit.models import *

#====== User Serializer ======#
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['groups', 'user_permissions', 'is_active']
        extra_kwargs = {
            "password": {"write_only": True}
        }
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        password = validated_data.get('password')
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
    
#==== Login Serializer ====#
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()