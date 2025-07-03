from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login,logout

from django.views import View

from .forms import LoginForm,TravellerRegisterForm,ProfileForm

from django.db import transaction

from .models import Profile,Traveller

import threading

from django.contrib.auth.hashers import make_password

from django.utils.decorators import method_decorator

from django.views.decorators.cache import never_cache

# Create your views here.



class LoginView(View):

    def get(self, request, *args , **kwargs):

        form = LoginForm()

        data = {
            'page' : 'login-page',
            'form'  : form
        }
        return render(request, 'authentication/login.html',context=data)
    

    def post(self, request, *args, **kwargs):

        form = LoginForm(request.POST)

        error = None

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request,username=username , password=password)

            if user :

                login(request, user)

                return redirect('diary-list')
            
            error ='Invalid credencials'

            data = {
                'form' : form,
                'error' : error,
                'page' : LoginForm
            }

            return render(request,'authentication/login.html', context=data)
        
@method_decorator(never_cache, name='dispatch')
class LogoutView(View):
        
        def get(self,request, *args, **kwargs):
             
            logout(request)

            request.session.flush()

            return redirect('home')
        

class RegisterTravellerView(View):
     
    def get(self, request, *args, **kwargs):

        profile_form = ProfileForm()

        traveller_form = TravellerRegisterForm()



        data ={
            'traveller_form' : traveller_form,
            'profile_form' :profile_form
        }
         
        return render(request, 'authentication/register_user.html',context=data)
    
    def post(self, request, *args, **kwargs):

        form= TravellerRegisterForm ( request.POST, request.FILES)

        print(form.errors)

        if form.is_valid():

            with transaction.atomic():

                first_name = form.cleaned_data['first_name']

                last_name = form.cleaned_data['last_name']

                # profile = form.save(commit=False)

                email = form.cleaned_data.get('email')

                password = form.cleaned_data.get('password')

                number = form.cleaned_data['number']

                image = form.cleaned_data['image']

                profile = Profile.objects.create(

                    username = email,
                    first_name= first_name,
                    last_name = last_name,
                    email=email,
                    role= 'User',
                    password = make_password(password)
                )

                Traveller.objects.create(

                    profile=profile,
                    name=f'{first_name} {last_name}',
                    email= email,
                    number= number,
                    image= image

                )
                return redirect ('login')
            
        return render(request, 'authentication/register_user.html', {'traveller_form': form})    



            



        

