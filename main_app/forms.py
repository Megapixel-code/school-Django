from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import gettext_lazy as _

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    last_name = forms.CharField(max_length=50, label=_('Nom'))
    first_name = forms.CharField(max_length=50, label=_('Prenom'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')