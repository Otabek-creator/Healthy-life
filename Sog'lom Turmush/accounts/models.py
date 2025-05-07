from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Erkak', 'Erkak'),
        ('Ayol', 'Ayol'),
    ]

    ACTIVITY_CHOICES = [
        ('Kam faol', 'Kam faol'),
        ('Biroz faol', 'Biroz faol'),
        ("O'rtacha faol", "O'rtacha faol"),
        ('Juda faol', 'Juda faol'),
        ('Juda yuqori faol', 'Juda yuqori faol'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(default=30)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Erkak')
    weight = models.FloatField(default=70)  # in kg
    height = models.FloatField(default=170)  # in cm
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default="O'rtacha faol")

    def __str__(self):
        return f"{self.user.username}'s profile"

    def calculate_bmi(self):
        """Calculate BMI (Body Mass Index)"""
        height_in_meters = self.height / 100
        return self.weight / (height_in_meters * height_in_meters)

    def get_bmi_category(self):
        """Get BMI category"""
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return "Vazn yetishmovchiligi"
        elif bmi < 25:
            return "Normal vazn"
        elif bmi < 30:
            return "Ortiqcha vazn"
        else:
            return "Semizlik"

    def calculate_daily_calories(self):
        """Calculate recommended daily calorie intake"""
        # Basal Metabolic Rate (BMR)
        if self.gender == "Erkak":
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.33 * self.age)

        # Activity multipliers
        activity_multipliers = {
            "Kam faol": 1.2,
            "Biroz faol": 1.375,
            "O'rtacha faol": 1.55,
            "Juda faol": 1.725,
            "Juda yuqori faol": 1.9,
        }

        # Daily calorie goal
        return round(bmr * activity_multipliers[self.activity_level])