from django import forms
from django.forms import CharField


class NameForm(forms.Form):
    login = CharField(label='Enter your name', max_length=100)
    password = CharField(label='Password ', widget=forms.PasswordInput())