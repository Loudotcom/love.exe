from django.contrib import admin
from .models import CustomUser, Hobby, UserProfile, DealbreakerQuestion, DealbreakerAnswer

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',)
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)

class HobbyAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Hobby, HobbyAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'city', 'country')
    search_fields = ('user__username', 'city', 'country')

admin.site.register(UserProfile, UserProfileAdmin)

class DealbreakerQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'creator')
    search_fields = ('text', 'creator__username')

admin.site.register(DealbreakerQuestion, DealbreakerQuestionAdmin)

class DealbreakerAnswerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'question', 'answer_yn')
    search_fields = ('user_profile__user__username', 'question__text')

admin.site.register(DealbreakerAnswer, DealbreakerAnswerAdmin)
