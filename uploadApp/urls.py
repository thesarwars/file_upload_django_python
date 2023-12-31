from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register_view, name='register'),
    path('upload/', views.FileUploadView.as_view(), name='upload'),
    path('documents/<int:pk>/download/', views.DocumentDownloadView.as_view(), name='document-download'),
    path('documents/<int:pk>/share/', views.DocumentShareView.as_view(), name='document-sahre'),
    path('documents/files/', views.FileListView.as_view(), name='document-list'),
    path('documents/update/<int:pk>/', views.FilesUpdateDelete.as_view(), name='document-list'),
    path('doc2pdf/', views.ConvertDocToPDFView.as_view(), name='convert_doc_to_pdf'),
]