from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

BASE_WIDGET_ATTRS = {
    "class": "w-full px-3 py-2 border-2 border-green-400 rounded-md focus:outline-none focus:ring-2 focus:ring-green-200",
    "placeholder": "",
}

class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True)
    age = forms.IntegerField(min_value=10, max_value=100, initial=30)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    weight = forms.FloatField(min_value=30, max_value=200, initial=70)
    height = forms.FloatField(min_value=100, max_value=250, initial=170)
    activity_level = forms.ChoiceField(choices=UserProfile.ACTIVITY_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'name', 'age', 'gender', 'weight', 'height', 'activity_level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for each field, attach a consistent widget attrs
        for field_name, field in self.fields.items():
            widget = field.widget
            # placeholder uchun label’dan foydalanish
            widget.attrs.update({
                **BASE_WIDGET_ATTRS,
                "placeholder": field.label
            })

class UserLoginForm(AuthenticationForm):
    """AuthenticationForm ga widget attrs qo‘shamiz."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                **BASE_WIDGET_ATTRS,
                "placeholder": field.label,
            })

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'age', 'gender', 'weight', 'height', 'activity_level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                **BASE_WIDGET_ATTRS,
                "placeholder": field.label
            })
