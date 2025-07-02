from django import forms

from .models import Traveller, Profile



class LoginForm(forms.Form):

    username = forms.CharField(max_length= 25, widget=forms.TextInput(attrs={
                            'class' : 'form-control',
                            'required' : 'required'
    }))

    password = forms.CharField(max_length=25,widget= forms.PasswordInput(attrs={
                            'class' : 'form-control',
                            'required' : 'required'
    }))

class TravellerRegisterForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'required': 'required'
        })
    )


    class Meta:

        model = Traveller

        exclude = ['profile','uuid','active_status','name']

        widgets = {

           
            'image' : forms.FileInput(attrs={

                                        'class' :   'form-control',
                                        'required'  :   'required'
                                    }),
            
            'number' : forms.TextInput(attrs={
                                            'class' : 'form-control',
                                            'required' : 'required'
            })
            
        }    



class ProfileForm(forms.ModelForm):

    class Meta:

        confirm_password    =   forms.CharField(widget=forms.PasswordInput(attrs={
                                                    'class' :   'form-control',
                                                    'required'  :   'required'
                                            }))
         
        model = Profile

        exclude = ['profile','uuid', 'active_status']

        widgets = {

            'first_name'    :   forms.TextInput(attrs={
                                                    'class' :   'form-control',
                                                    'required'  :   'required'
                                                }),
            'last_name'    :   forms.TextInput(attrs={
                                                    'class' :   'form-control',
                                                    'required'  :   'required'
                                                }),
            'email'    :   forms.EmailInput(attrs={
                                                    'class' :   'form-control',
                                                    'required'  :   'required'
                                                }),
            'password'    :   forms.PasswordInput(attrs={
                                                    'class' :   'form-control',
                                                    'required'  :   'required'
                                                }),
           
            }
        
        def clean(self):

            validated_data =super().clean()

            if validated_data.get('email') in Profile.objects.values_list('username',flat=True):

                self.add_error('email','email already taken')

            if validated_data.get('password') != validated_data.get('confirm_password'):

                self.add_error('confirm_password','password mismatch') 
