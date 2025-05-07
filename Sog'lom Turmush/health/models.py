from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Food(models.Model):
    MEAL_CHOICES = [
        ('Nonushta', 'Nonushta'),
        ('Tushlik', 'Tushlik'),
        ('Kechki ovqat', 'Kechki ovqat'),
        ('Yengil ovqat', 'Yengil ovqat'),
    ]

    FOOD_CHOICES = [
        ('Tuxum (qaynatilgan)', 'Tuxum (qaynatilgan)'),
        ('Osh', 'Osh'),
        ('Shorva', 'Shorva'),
        ('Salat (sabzavotli)', 'Salat (sabzavotli)'),
        ('Sut', 'Sut'),
        ('Qaymoq', 'Qaymoq'),
        ('Non', 'Non'),
        ('Guruch', 'Guruch'),
        ('Kartoshka (qaynatilgan)', 'Kartoshka (qaynatilgan)'),
        ('Mol go\'shti', 'Mol go\'shti'),
        ('Tovuq go\'shti', 'Tovuq go\'shti'),
        ('Baliq (qovurilgan)', 'Baliq (qovurilgan)'),
        ('Yogurt', 'Yogurt'),
        ('Pishloq', 'Pishloq'),
        ('Mevzalar (uzum)', 'Mevzalar (uzum)'),
        ('Olma', 'Olma'),
        ('Banan', 'Banan'),
        ('Apelsin', 'Apelsin'),
        ('Shokolad', 'Shokolad'),
        ('Muzqaymoq', 'Muzqaymoq'),
        ('Kek', 'Kek'),
        ('Pechene', 'Pechene'),
        ('Somsa', 'Somsa'),
        ('Manti', 'Manti'),
        ('Lag\'mon', 'Lag\'mon'),
        ('Choy', 'Choy'),
        ('Kofe', 'Kofe'),
        ('Sharbat', 'Sharbat'),
        ('Pomidor', 'Pomidor'),
        ('Bodring', 'Bodring'),
        ('Sabzi', 'Sabzi'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='foods')
    food_name = models.CharField(max_length=100, choices=FOOD_CHOICES)
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    calories = models.PositiveIntegerField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.food_name} - {self.user.username} ({self.date})"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date']),
        ]


class Workout(models.Model):
    INTENSITY_CHOICES = [
        ('Kam', 'Kam'),
        ('O\'rta', 'O\'rta'),
        ('Yuqori', 'Yuqori'),
    ]

    STATUS_CHOICES = [
        ('Rejalashtirilgan', 'Rejalashtirilgan'),
        ('Bajarilgan', 'Bajarilgan'),
    ]

    WORKOUT_CHOICES = [
        ('Yugurish', 'Yugurish'),
        ('Velosiped', 'Velosiped'),
        ('Suvda suzish', 'Suvda suzish'),
        ('Og\'ir atletika', 'Og\'ir atletika'),
        ('Yoga', 'Yoga'),
        ('Piyoda yurish', 'Piyoda yurish'),
        ('Tosh ko\'tarish', 'Tosh ko\'tarish'),
        ('Anjumaniya (squat)', 'Anjumaniya (squat)'),
        ('Push-up', 'Push-up'),
        ('Plank', 'Plank'),
        ('Burpee', 'Burpee'),
        ('Jumping jacks', 'Jumping jacks'),
        ('Lunges', 'Lunges'),
        ('Pull-up', 'Pull-up'),
        ('Deadlift', 'Deadlift'),
        ('Bench press', 'Bench press'),
        ('Kardio mashqlar', 'Kardio mashqlar'),
        ('Zumba', 'Zumba'),
        ('Pilates', 'Pilates'),
        ('Interval trening', 'Interval trening'),
        ('Kettlebell mashqlari', 'Kettlebell mashqlari'),
        ('Boxing', 'Boxing'),
        ('Qilichbozlik', 'Qilichbozlik'),
        ('Tennis', 'Tennis'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=100, choices=WORKOUT_CHOICES)
    duration = models.PositiveIntegerField()  # daqiqalarda
    intensity = models.CharField(max_length=10, choices=INTENSITY_CHOICES)
    calories_burned = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Rejalashtirilgan')
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.user.username} ({self.date})"

    @staticmethod
    def calculate_calories_burned(name, duration, intensity, weight):
        """Mashg'ulot davomida yo'qotilgan kaloriyalarni hisoblash"""
        # Mashg'ulot turlari uchun MET qiymatlari (o'rtacha, intensivlikka qarab sozlanadi)
        workout_met_values = {
            'Yugurish': {'Kam': 4.0, 'O\'rta': 7.0, 'Yuqori': 10.0},
            'Velosiped': {'Kam': 3.5, 'O\'rta': 5.5, 'Yuqori': 8.0},
            'Suvda suzish': {'Kam': 4.5, 'O\'rta': 7.0, 'Yuqori': 10.0},
            'Og\'ir atletika': {'Kam': 3.0, 'O\'rta': 5.0, 'Yuqori': 7.0},
            'Yoga': {'Kam': 2.5, 'O\'rta': 3.5, 'Yuqori': 5.0},
            'Piyoda yurish': {'Kam': 2.5, 'O\'rta': 4.0, 'Yuqori': 6.0},
            'Tosh ko\'tarish': {'Kam': 3.5, 'O\'rta': 5.5, 'Yuqori': 8.0},
            'Anjumaniya (squat)': {'Kam': 3.0, 'O\'rta': 5.0, 'Yuqori': 7.0},
            'Push-up': {'Kam': 3.0, 'O\'rta': 5.0, 'Yuqori': 7.0},
            'Plank': {'Kam': 2.5, 'O\'rta': 4.0, 'Yuqori': 6.0},
            'Burpee': {'Kam': 4.0, 'O\'rta': 6.0, 'Yuqori': 8.0},
            'Jumping jacks': {'Kam': 3.5, 'O\'rta': 5.5, 'Yuqori': 7.5},
            'Lunges': {'Kam': 3.0, 'O\'rta': 5.0, 'Yuqori': 7.0},
            'Pull-up': {'Kam': 3.5, 'O\'rta': 5.5, 'Yuqori': 7.5},
            'Deadlift': {'Kam': 3.5, 'O\'rta': 5.5, 'Yuqori': 7.5},
            'Bench press': {'Kam': 3.0, 'O\'rta': 5.0, 'Yuqori': 7.0},
            'Kardio mashqlar': {'Kam': 4.0, 'O\'rta': 6.0, 'Yuqori': 8.0},
            'Zumba': {'Kam': 4.0, 'O\'rta': 6.0, 'Yuqori': 8.0},
            'Pilates': {'Kam': 2.5, 'O\'rta': 3.5, 'Yuqori': 5.0},
            'Interval trening': {'Kam': 5.0, 'O\'rta': 7.0, 'Yuqori': 9.0},
            'Kettlebell mashqlari': {'Kam': 4.0, 'O\'rta': 6.0, 'Yuqori': 8.0},
            'Boxing': {'Kam': 4.5, 'O\'rta': 6.5, 'Yuqori': 9.0},
            'Qilichbozlik': {'Kam': 4.0, 'O\'rta': 6.0, 'Yuqori': 8.0},
            'Tennis': {'Kam': 5.0, 'O\'rta': 7.0, 'Yuqori': 9.0},
        }

        # MET qiymatini olish
        met = workout_met_values.get(name, {'Kam': 3.0, 'O\'rta': 5.0, 'Yuqori': 8.0})[intensity]

        # Kaloriya hisoblash: calories = MET * weight(kg) * duration(hours)
        return round(met * weight * (duration / 60))