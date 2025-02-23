from logging import PlaceHolder
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from .models import CustomUser, UserProfile, Hobby, DealbreakerAnswer, DealbreakerQuestion
from cities_light.models import City, Country


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control w-100'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control w-100'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control w-100'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(attrs={
            'class': 'form-control w-100',
            'style': 'height: 50px;'
        })
    )
    password = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control w-100',
            'style': 'height: 50px;'
        })
    )


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'text': 'Text',
        }
        for field in self.fields:
            placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['required'] = True
            self.fields[field].label = False


class DealbreakerAnswerForm(forms.ModelForm):
    class Meta:
        model = DealbreakerAnswer
        fields = ('question', 'answer_yn')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'question': 'question',
            'answer_yn': 'answer_yn',
        }

        for field in self.fields:
            placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['required'] = True
            self.fields[field].label = False

