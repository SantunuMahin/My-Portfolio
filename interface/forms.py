from django import forms
from .models import ConnectMe


class ConnectForm(forms.ModelForm):
    class Meta:
        model = ConnectMe
        fields = ['name','email','comment']