from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.

# user registration model 
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    shared_with = models.ManyToManyField(User, related_name='shared_documents', blank=True)
    
    def __str__(self):
        return self.file.name
    
    # def get_download_url(self):
    #     return reverse('document-download', kwargs={'pk': self.pk})