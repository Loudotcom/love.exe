from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Hobby

class CustomUserCreationForm(UserCreationForm):
    age = forms.IntegerField(required=True)
    location = forms.CharField(max_length=255)
    profile_picture = forms.ImageField(required=False)
    hobbies = forms.ModelMultipleChoiceField(
        queryset=Hobby.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'age', 'location', 'profile_picture', 'hobbies')
