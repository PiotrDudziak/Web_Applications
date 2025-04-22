from django import forms
from .models import Route, RoutePoint

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'background']
        labels = {
            'name': 'Nazwa trasy:',
            'background': 'Wybór tła dla trasy:'
        }

class RoutePointForm(forms.ModelForm):
    class Meta:
        model = RoutePoint
        fields = ['x', 'y']