from django import forms
from .models import HomeData

class HomeDataForm(forms.ModelForm):
    class Meta:
        model = HomeData
        fields = ["username", "azure_key", "azure_end", "wit_key", "weather_key", "bridge_ip"]
        exclude = ('username',)
