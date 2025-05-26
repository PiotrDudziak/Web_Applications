from django import forms
from .models import Route, RoutePoint, GameBoard, Path

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'background']

class RoutePointForm(forms.ModelForm):
    class Meta:
        model = RoutePoint
        fields = ['x', 'y']

class GameBoardForm(forms.ModelForm):
    class Meta:
        model = GameBoard
        fields = ['name', 'rows', 'cols']

class PathForm(forms.ModelForm):
    class Meta:
        model = Path
        fields = ['name', 'board']
        labels = {
            'name': 'Nazwa ścieżki',
            'board': 'Plansza',
        }
        widgets = {
            'name': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].initial = ''