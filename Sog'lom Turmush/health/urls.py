from django.urls import path
from . import views

urlpatterns = [
    # Food tracking
    path('food/', views.food_list_view, name='food_list'),
    path('food/add/', views.add_food_view, name='add_food'),
    path('food/delete/<int:pk>/', views.delete_food_view, name='delete_food'),

    # Workout tracking
    path('workout/', views.workout_list_view, name='workout_list'),
    path('workout/add/', views.add_workout_view, name='add_workout'),
    path('workout/status/<int:pk>/', views.update_workout_status, name='update_workout_status'),
    path('workout/delete/<int:pk>/', views.delete_workout_view, name='delete_workout'),

    # Statistics
    path('stats/', views.stats_view, name='stats'),
    path('stats/pdf/', views.download_stats_pdf, name='download_stats_pdf'),
]