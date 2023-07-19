from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UploadedFile


#I'm using User model for registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password',
                  'password2', 'is_staff', 'is_superuser')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError(
                {'error': 'Password does not match'})

        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError(
                {'error': 'Email already exists'})

        account = User(email=self.validated_data['email'],
                       username=self.validated_data['username'],
                       is_staff=self.validated_data.get('is_staff', False),
                       is_superuser=self.validated_data.get('is_superuser', False))
        account.set_password(password)
        account.save()

        return account

# This serializer for upload, delete, modify, share, download
class FileUploadedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ('file', 'uploader', 'shared_with', 'title', 'description')
