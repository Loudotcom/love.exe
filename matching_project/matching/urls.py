from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('profile/', views.profile, name='profile'),
    path('match/like_dislike/', views.like_dislike, name='like_dislike'),
    path('liked-profiles/', views.liked_profiles, name='liked-profiles'),
    path('match/', views.matching_view, name='match'),
    path('get_dealbreaker_questions/<int:profile_id>/', views.get_dealbreaker_questions, name='get_dealbreaker_questions'),
    path('answer-dealbreaker/<int:profile_id>/', views.answer_dealbreaker_questions, name='answer_dealbreaker_questions'),
    path('message_detail/<int:profile_id>/', views.message_detail, name='message_detail'),
]