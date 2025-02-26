from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class CustomUser(AbstractUser):
    
    
    def __str__(self):
        return self.username


class Hobby(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    

class LikeDislike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='like_dislikes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    like = models.BooleanField(null=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'user')

    def __str__(self):
        return f'{self.user} - {self.content_object} - {self.like}'


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.sender} -> {self.recipient}'



class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to='profile_pics/')
    age = models.IntegerField(default=18)
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True)
    hobbies = models.ManyToManyField('Hobby', related_name='users')
    questions = models.ManyToManyField('DealbreakerQuestion', related_name='user_profiles', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = GenericRelation(LikeDislike)

    def __str__(self):
        return f'{self.user.username} Profile'


class DealbreakerQuestion(models.Model):
    QUESTION_TYPES = [
        ('YN', 'Yes/No'),
    ]

    text = models.CharField(max_length=500, help_text="The question text.")
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, help_text="Type of question (Yes/No).")
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_questions', help_text="The user who created this question.")

    def __str__(self):
        return self.text


class DealbreakerAnswer(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='dealbreaker_answers', help_text="The user profile that answered this question.")
    question = models.ForeignKey(DealbreakerQuestion, on_delete=models.CASCADE, help_text="The question being answered.")
    answer_yn = models.BooleanField(null=True, blank=True, help_text="The answer to the question (True for Yes, False for No).")

    class Meta:
        unique_together = ('user_profile', 'question')

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.question}"