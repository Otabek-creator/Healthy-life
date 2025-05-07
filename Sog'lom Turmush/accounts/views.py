from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm, UserLoginForm
from .models import UserProfile


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create user profile
            UserProfile.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                age=form.cleaned_data['age'],
                gender=form.cleaned_data['gender'],
                weight=form.cleaned_data['weight'],
                height=form.cleaned_data['height'],
                activity_level=form.cleaned_data['activity_level']
            )

            # Log the user in
            login(request, user)
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.username,
            'age': 30,
            'gender': 'Erkak',
            'weight': 70,
            'height': 170,
            'activity_level': "O'rtacha faol"
        }
    )

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil ma'lumotlari muvaffaqiyatli yangilandi!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'bmi': profile.calculate_bmi(),
        'bmi_category': profile.get_bmi_category(),
        'daily_calories': profile.calculate_daily_calories(),
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')
