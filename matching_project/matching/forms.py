from logging import PlaceHolder
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from .models import CustomUser, UserProfile, Hobby, DealbreakerAnswer, DealbreakerQuestion
from cities_light.models import City, Country


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


class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())

    password = forms.CharField(widget=PasswordInput())


class UserProfileForm(forms.ModelForm):
    country = forms.CharField(
        widget=forms.TextInput(attrs={'list': 'country-list', 'placeholder': 'Enter your country...'}),
        required=True
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'list': 'city-list', 'placeholder': 'Enter your city...'}),
        required=True
    )
    age = forms.IntegerField(max_value=100, min_value=18)
    
    class Meta:
        model = UserProfile
        fields = ('bio', 'profile_picture', 'age', 'city', 'country', 'hobbies')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'hobbies': forms.CheckboxSelectMultiple(),
        }

    def clean_city(self):
        city_name = self.cleaned_data['city']
        city = City.objects.filter(name__iexact=city_name).first()
        if not city:
            raise forms.ValidationError("Selected city is not valid.")
        return city

    def clean_country(self):
        country_name = self.cleaned_data['country']
        country = Country.objects.filter(name__iexact=country_name).first()
        if not country:
            raise forms.ValidationError("Selected country is not valid.")
        return country


class DealbreakerQuestionForm(forms.ModelForm):
    class Meta:
        model = DealbreakerQuestion
        fields = ('text',)


class DealbreakerAnswerForm(forms.ModelForm):
    class Meta:
        model = DealbreakerAnswer
        fields = ('question', 'answer_yn')
