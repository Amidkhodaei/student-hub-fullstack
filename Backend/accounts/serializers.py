from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = User
        fields = [
            'id', 
            'student_no', 
            'fullname',
            'first_name',
            'last_name', 
            'email', 
            'phone', 
            'password', 
            'fullname'
        ]

        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'first_name': {'write_only': True,'required': True},
            'last_name': {'write_only': True,'required': True},
            'email': {'required': True}
        }

    def get_fullname(self, user):
        return f"{user.first_name} {user.last_name}"
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)