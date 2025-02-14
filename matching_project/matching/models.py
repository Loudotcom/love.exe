from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    
    
    def __str__(self):
        return self.username


class Hobby(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to='profile_pics/')
    age = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=30, blank=True,)
    country = models.CharField(max_length=30, blank=True)
    hobbies = models.ManyToManyField('Hobby', related_name='users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'
