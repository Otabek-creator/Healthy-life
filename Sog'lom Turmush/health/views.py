from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
import json

from .models import Food, Workout
from .forms import FoodForm, WorkoutForm
from .pdf_utils import download_stats_pdf
from .utils import FOOD_NUTRIENTS

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from health.models import Food
from health.forms import FoodForm
from django.db.models import Sum


@login_required
def food_list_view(request):
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    try:
        selected_date = timezone.datetime.fromisoformat(date_str).date()
    except ValueError:
        selected_date = timezone.now().date()

    foods = Food.objects.filter(user=request.user, date=selected_date)
    total_calories = foods.aggregate(Sum('calories'))['calories__sum'] or 0
    total_protein = foods.aggregate(Sum('protein'))['protein__sum'] or 0
    total_carbs = foods.aggregate(Sum('carbs'))['carbs__sum'] or 0
    total_fat = foods.aggregate(Sum('fat'))['fat__sum'] or 0
    daily_calories = request.user.profile.calculate_daily_calories()
    remaining_calories = daily_calories - total_calories

    context = {
        'foods': foods,
        'form': FoodForm(),
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat,
        'daily_calories': daily_calories,
        'remaining_calories': remaining_calories,
        'today': selected_date,
        'food_nutrients': FOOD_NUTRIENTS,
    }
    return render(request, 'health/food_list.html', context)


@login_required
def add_food_view(request):
    if request.method == 'POST':
        form = FoodForm(request.POST)
        if form.is_valid():
            food = form.save(commit=False)
            food.user = request.user
            food.date = timezone.datetime.fromisoformat(request.POST.get('date')).date()
            food.save()
            messages.success(request, "Ovqat muvaffaqiyatli qo'shildi!")
            return redirect('food_list')
        else:
            print(form.errors)  # Xatolarni konsolda ko'rish
            date_str = request.POST.get('date', timezone.now().date().isoformat())
            try:
                selected_date = timezone.datetime.fromisoformat(date_str).date()
            except ValueError:
                selected_date = timezone.now().date()

            foods = Food.objects.filter(user=request.user, date=selected_date)
            total_calories = foods.aggregate(Sum('calories'))['calories__sum'] or 0
            total_protein = foods.aggregate(Sum('protein'))['protein__sum'] or 0
            total_carbs = foods.aggregate(Sum('carbs'))['carbs__sum'] or 0
            total_fat = foods.aggregate(Sum('fat'))['fat__sum'] or 0
            daily_calories = request.user.profile.calculate_daily_calories()
            remaining_calories = daily_calories - total_calories

            context = {
                'foods': foods,
                'form': form,
                'total_calories': total_calories,
                'total_protein': total_protein,
                'total_carbs': total_carbs,
                'total_fat': total_fat,
                'daily_calories': daily_calories,
                'remaining_calories': remaining_calories,
                'today': selected_date,
                'food_nutrients': FOOD_NUTRIENTS,
            }
            return render(request, 'health/food_list.html', context)
    return redirect('food_list')


@login_required
def delete_food_view(request, pk):
    food = get_object_or_404(Food, id=pk, user=request.user)
    food.delete()
    messages.success(request, "Ovqat muvaffaqiyatli o'chirildi!")
    return redirect('food_list')


@login_required
def workout_list_view(request):
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    try:
        selected_date = timezone.datetime.fromisoformat(date_str).date()
    except ValueError:
        selected_date = timezone.now().date()

    workouts = Workout.objects.filter(user=request.user, date=selected_date)
    total_calories_burned = workouts.filter(status='Bajarilgan').aggregate(Sum('calories_burned'))[
                                'calories_burned__sum'] or 0
    total_duration = workouts.filter(status='Bajarilgan').aggregate(Sum('duration'))['duration__sum'] or 0
    completed_workouts = workouts.filter(status='Bajarilgan').count()
    planned_workouts = workouts.filter(status='Rejalashtirilgan').count()

    context = {
        'workouts': workouts,
        'form': WorkoutForm(),
        'total_calories_burned': total_calories_burned,
        'total_duration': total_duration,
        'completed_workouts': completed_workouts,
        'planned_workouts': planned_workouts,
        'today': selected_date,
    }
    return render(request, 'health/workout_list.html', context)


@login_required
def add_workout_view(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.date = timezone.datetime.fromisoformat(request.POST.get('date')).date()
            try:
                weight = request.user.profile.weight
            except AttributeError:
                weight = 70.0  # Standart vazn (kg), agar profil yoki weight mavjud bo'lmasa
            workout.calories_burned = Workout.calculate_calories_burned(
                workout.name,
                workout.duration,
                workout.intensity,
                weight
            )
            workout.save()
            messages.success(request, "Mashg'ulot muvaffaqiyatli qo'shildi!")
            return redirect('workout_list')
        else:
            print(form.errors)  # Xatolarni konsolda ko'rish
            date_str = request.POST.get('date', timezone.now().date().isoformat())
            try:
                selected_date = timezone.datetime.fromisoformat(date_str).date()
            except ValueError:
                selected_date = timezone.now().date()

            workouts = Workout.objects.filter(user=request.user, date=selected_date)
            total_calories_burned = workouts.filter(status='Bajarilgan').aggregate(Sum('calories_burned'))[
                                        'calories_burned__sum'] or 0
            total_duration = workouts.filter(status='Bajarilgan').aggregate(Sum('duration'))['duration__sum'] or 0
            completed_workouts = workouts.filter(status='Bajarilgan').count()
            planned_workouts = workouts.filter(status='Rejalashtirilgan').count()

            context = {
                'workouts': workouts,
                'form': form,
                'total_calories_burned': total_calories_burned,
                'total_duration': total_duration,
                'completed_workouts': completed_workouts,
                'planned_workouts': planned_workouts,
                'today': selected_date,
            }
            return render(request, 'health/workout_list.html', context)
    return redirect('workout_list')


@login_required
def update_workout_status(request, pk):
    workout = get_object_or_404(Workout, id=pk, user=request.user)
    if workout.status == 'Rejalashtirilgan':
        workout.status = 'Bajarilgan'
        messages.success(request, "Mashg'ulot bajarilgan deb belgilandi!")
    else:
        workout.status = 'Rejalashtirilgan'
        messages.success(request, "Mashg'ulot rejalashtirilgan deb belgilandi!")
    workout.save()
    return redirect('workout_list')


@login_required
def delete_workout_view(request, pk):
    workout = get_object_or_404(Workout, id=pk, user=request.user)
    workout.delete()
    messages.success(request, "Mashg'ulot muvaffaqiyatli o'chirildi!")
    return redirect('workout_list')


@login_required
def stats_view(request):
    try:
        # Get date range (default: last 7 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)

        if isinstance(start_date, str):
            start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return redirect('stats')

    # Ma'lumotlarni bazadan olish
    # calorie_data = Calorie.objects.filter(
    #     user=request.user,
    #     date__range=[start_date, end_date]
    # )

    # Get foods and workouts for the date range
    foods = Food.objects.filter(user=request.user, date__range=[start_date, end_date])
    workouts = Workout.objects.filter(user=request.user, date__range=[start_date, end_date])

    # Prepare data for charts
    dates = []
    calories_consumed = []
    calories_burned = []

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))

        # Calculate calories consumed on this date
        day_foods = foods.filter(date=current_date)
        day_calories = day_foods.aggregate(Sum('calories'))['calories__sum'] or 0
        calories_consumed.append(day_calories)

        # Calculate calories burned on this date
        day_workouts = workouts.filter(date=current_date, status='Bajarilgan')
        day_burned = day_workouts.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        calories_burned.append(day_burned)

        current_date += timedelta(days=1)

    # Calculate averages and totals
    avg_daily_calories = sum(calories_consumed) / len(calories_consumed) if calories_consumed else 0
    avg_burned_calories = sum(calories_burned) / len(calories_burned) if calories_burned else 0
    total_net_calories = sum(calories_consumed) - sum(calories_burned)

    # Workout statistics
    total_workout_count = workouts.filter(status='Bajarilgan').count()
    total_workout_duration = workouts.filter(status='Bajarilgan').aggregate(Sum('duration'))['duration__sum'] or 0
    total_workout_calories = workouts.filter(status='Bajarilgan').aggregate(Sum('calories_burned'))[
                                 'calories_burned__sum'] or 0

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'dates': json.dumps(dates),
        'calories_consumed': json.dumps(calories_consumed),
        'calories_burned': json.dumps(calories_burned),
        'avg_daily_calories': round(avg_daily_calories),
        'avg_burned_calories': round(avg_burned_calories),
        'total_net_calories': round(total_net_calories),
        'total_workout_count': total_workout_count,
        'total_workout_duration': total_workout_duration,
        'total_workout_calories': total_workout_calories,
    }

    return render(request, 'health/stats.html', context)


@login_required
def download_pdf_report(request):
    """PDF hisobotini yuklab olish ko'rinishi"""
    # Bu funksiya to'g'ridan-to'g'ri PDF generator funksiyasini chaqiradi
    return download_stats_pdf(request)
