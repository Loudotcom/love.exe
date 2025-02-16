from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('profile/', views.profile, name='profile'),
    path('match/', views.matching_view, name='match'),
    path('get_dealbreaker_questions/<int:profile_id>/', views.get_dealbreaker_questions, name='get_dealbreaker_questions'),
    path('answer-dealbreaker/<int:profile_id>/', views.answer_dealbreaker_questions, name='answer_dealbreaker_questions'),
]

