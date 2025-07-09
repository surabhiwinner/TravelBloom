from django import forms
from .models import Traveller, Profile


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=25,
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
    )
    password = forms.CharField(
        max_length=25,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'})
    )


class TravellerRegisterForm(forms.ModelForm):
    class Meta:
        model = Traveller
        exclude = ['profile', 'uuid', 'active_status', 'name','email']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'required': 'required'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }


class ProfileForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'})
    )

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'password']  # ✅ Include only these fields      
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def clean(self):
        validated_data = super().clean()

        email = validated_data.get('email')
        password = validated_data.get('password')
        confirm_password = validated_data.get('confirm_password')

        if email and Profile.objects.filter(username=email).exists():
            self.add_error('email', 'Email already taken')

        if password != confirm_password:
            self.add_error('confirm_password', 'Password mismatch')
