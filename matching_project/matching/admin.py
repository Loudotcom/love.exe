from django.contrib import admin
from .models import CustomUser, Hobby

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'age', 'location', 'profile_picture')
    search_fields = ('username', 'email')
    filter_horizontal = ('hobbies',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Hobby)
