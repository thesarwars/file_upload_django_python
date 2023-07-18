from django.shortcuts import render
from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, serializers
from .serializers import UserRegistrationSerializer, FileUploadedSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def Home(request):
    return HttpResponse('Hello World')

# user login view
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = User.objects.filter(username=username).first()

            if user is not None and user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)
                return Response({'message': 'User logged in successfully.', 'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'message': 'Missing username or password.'}, status=status.HTTP_400_BAD_REQUEST)


# user logout view
@api_view(['POST',])
def user_logout(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response({'Message': 'Logged Out'}, status=status.HTTP_200_OK)


# user registration view
@api_view(['POST'])
def user_register_view(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        data = {}
        
        if serializer.is_valid():
            account = serializer.save()
            
            data['response'] = 'Account has been created'
            data['username'] = account.username 
            data['email'] = account.email
            data['is_staff'] = account.is_staff
            data['is_superuser'] = account.is_superuser 
            
            token = Token.objects.get(user=account).key
            data['token'] = token
            
        else:
            data = serializer.errors
        return Response(data)
    
    
    
# Define the allowed file formats and maximum file size
ALLOWED_FILE_FORMATS = ['pdf', 'doc', 'docx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadedFile):
    # Check if the file format is allowed
    file_format = file.name.split('.')[-1].lower()
    if file_format not in ALLOWED_FILE_FORMATS:
        raise ValidationError(f'Invalid file format. Only {", ".join(ALLOWED_FILE_FORMATS)} formats are allowed.')

    # Check the file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f'File size exceeds the limit of {MAX_FILE_SIZE} bytes.')


# User upload the file and username will be saved
class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadedSerializer(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data['file']
            try:
                validate_file(file)
            except serializers.ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            serializer.validated_data['uploader'] = request.user
            
            serializer.save()

            return Response({'success': True}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)