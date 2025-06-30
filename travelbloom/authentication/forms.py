from django import forms


class LoginForm(forms.Form):

    username = forms.CharField(max_length= 25, widget=forms.TextInput(attrs={
                            'class' : 'form-control',
                            'required' : 'required'
    }))

    password = forms.CharField(max_length=25,widget= forms.PasswordInput(attrs={
                            'class' : 'form-control',
                            'required' : 'required'
    }))

    