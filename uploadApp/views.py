from django.shortcuts import render
from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, serializers, filters
from .serializers import UserRegistrationSerializer, FileUploadedSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from .models import UploadedFile
import mimetypes


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
        
        
        
# class DocumentDownloadView(generics.RetrieveAPIView):
#     queryset = UploadedFile.objects.all()
#     serializer_class = FileUploadedSerializer
#     permission_classes = [permissions.IsAuthenticated]  # Requires authentication

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
        
#         # Check if the user is the document owner or an admin
#         if request.user == instance.uploader or request.user.is_staff:
#             # Perform any additional checks if needed
            
#             # Download the file
#             file = instance.file
#             response = HttpResponse(file, content_type='application/octet-stream')
#             response['Content-Disposition'] = f'attachment; filename="{file.name}"'
#             return response
        
#         # Return a 403 Forbidden response if the user is not allowed to download the file
#         return HttpResponse(status=403)


# File download
class DocumentDownloadView(generics.RetrieveAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = FileUploadedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user == instance.uploader or request.user.is_staff:
            file = instance.file
            file_path = file.path
            file_name = file.name

            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read())

            content_type, _ = mimetypes.guess_type(file_name)
            response['Content-Type'] = content_type
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        return HttpResponse(status=403)
    
    

class DocumentShareView(generics.UpdateAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = FileUploadedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user == instance.uploader or request.user.is_staff:
            user_ids = request.data.get('shared_with', [])
            shared_with_users = User.objects.filter(id__in=user_ids)
            instance.shared_with.set(shared_with_users)
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return HttpResponse(status=403)
    
    

# Search Filter
class FileListView(generics.ListAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = FileUploadedSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['file', 'title', 'description', 'uploaded_at']
    
# File update, delete    
class FilesUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = UploadedFile
    serializer_class = FileUploadedSerializer