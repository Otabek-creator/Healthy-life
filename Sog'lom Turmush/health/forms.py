from django import forms
from .models import Food, Workout
from .utils import FOOD_NUTRIENTS

# Barcha form maydonlariga bir xil attribútlar beramiz
BASE_WIDGET_ATTRS = {
    "class": (
        "w-full px-3 py-2 "
        "border-2 border-green-600 rounded-md "
        "focus:outline-none focus:ring-2 focus:ring-green-200"
    ),
}


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['food_name', 'meal_type', 'calories', 'protein', 'carbs', 'fat']
        widgets = {
            'food_name': forms.Select(
                attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'id': 'id_food_name'}),
            'meal_type': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'calories': forms.NumberInput(
                attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'placeholder': '0',
                       'id': 'id_calories'}),
            'protein': forms.NumberInput(
                attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'placeholder': '0', 'step': '0.1',
                       'id': 'id_protein'}),
            'carbs': forms.NumberInput(
                attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'placeholder': '0', 'step': '0.1',
                       'id': 'id_carbs'}),
            'fat': forms.NumberInput(
                attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'placeholder': '0', 'step': '0.1',
                       'id': 'id_fat'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        food_name = cleaned_data.get('food_name')
        if food_name and food_name in FOOD_NUTRIENTS:
            nutrients = FOOD_NUTRIENTS[food_name]
            cleaned_data['calories'] = nutrients['calories']
            cleaned_data['protein'] = nutrients['protein']
            cleaned_data['carbs'] = nutrients['carbs']
            cleaned_data['fat'] = nutrients['fat']
        return cleaned_data

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'duration', 'intensity', 'status']
        widgets = {
            'name': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'id': 'id_name'}),
            'duration': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'id': 'id_duration', 'min': '1', 'max': '360', 'value': '30'}),
            'intensity': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'id': 'id_intensity'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        duration = cleaned_data.get('duration')
        if duration and duration <= 0:
            self.add_error('duration', "Davomiylik 0 dan katta bo'lishi kerak")
        return cleaned_data