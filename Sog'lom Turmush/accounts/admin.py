from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'age', 'gender', 'weight', 'height', 'activity_level')
    search_fields = ('user__username', 'name')
    list_filter = ('gender', 'activity_level')