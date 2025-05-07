from django.contrib import admin
from .models import Food, Workout


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_type', 'calories', 'protein', 'carbs', 'fat', 'date')
    list_filter = ('meal_type', 'date')
    search_fields = ('name', 'user__username')
    date_hierarchy = 'date'



@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'duration', 'intensity', 'calories_burned', 'status', 'date')
    list_filter = ('intensity', 'status', 'date')
    search_fields = ('name', 'user__username')
    date_hierarchy = 'date'
