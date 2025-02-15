from logging import PlaceHolder
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile, Hobby, DealbreakerAnswer, DealbreakerQuestion

class CustomUserCreationForm(UserCreationForm):
    """
    age = forms.IntegerField(required=True)
    location = forms.CharField(max_length=255)
    profile_picture = forms.ImageField(required=False)
    hobbies = forms.ModelMultipleChoiceField(
        queryset=Hobby.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2',)


class UserProfileForm(forms.ModelForm):
    age = forms.IntegerField(max_value=100, min_value=18)
    class Meta:
        model = UserProfile
        fields = ('user', 'bio', 'profile_picture', 'age', 'city', 'country', 'hobbies')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'hobbies': forms.CheckboxSelectMultiple(),
        }



class DealbreakerQuestionForm(forms.ModelForm):
    class Meta:
        model = DealbreakerQuestion
        fields = ('text',)


class DealbreakerAnswerForm(forms.ModelForm):
    class Meta:
        model = DealbreakerAnswer
        fields = ('question', 'answer_yn')
