from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.utils import timezone
from django.db import transaction,IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password
from travelbloom.utility import send_email
from .forms import LoginForm, TravellerRegisterForm, ProfileForm
from .models import Profile, Traveller
import threading
from django.contrib import messages

# Optional: your email function



class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html', {
            'form': LoginForm(),
            'page': 'login-page'
        })

    def post(self, request):
        form = LoginForm(request.POST)
        error = None

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # try:
                #     traveller = user.traveller  # because of related_name='traveller'
                #     request.session['show_premium_modal'] = not traveller.has_premium_access
                # except Traveller.DoesNotExist:
                #     request.session['show_premium_modal'] = True  # show if no record found

                return redirect('diary-list')

            error = 'Invalid credentials'

        return render(request, 'authentication/login.html', {
            'form': form,
            'error': error,
            'page': 'login-page'
        })


@method_decorator(never_cache, name='dispatch')
class LogoutView(View):
    def get(self, request):
        logout(request)
        request.session.flush()
        return redirect('home')


class RegisterTravellerView(View):
   

    def get(self, request, *args, **kwargs):
       
       profile_form = ProfileForm()

       traveller_form = TravellerRegisterForm()

       print(profile_form.errors)

       print(traveller_form.errors)

       data  = {
           'profile_form' :profile_form,
           'traveller_form' :traveller_form
       }

       return render(request,'authentication/register_user.html',context=data)
   



    # def post(self, request, *args, **kwargs):
    #     profile_form = ProfileForm(request.POST)
    #     traveller_form = TravellerRegisterForm(request.POST, request.FILES)

    #     print("Profile Form Errors:", profile_form.errors)
    #     print("Traveller Form Errors:", traveller_form.errors)

    #     if profile_form.is_valid() and traveller_form.is_valid():

    #         try:
    #             with transaction.atomic():
    #                 profile = profile_form.save(commit=False)

    #                 email = profile_form.cleaned_data.get('email')
    #                 password = profile_form.cleaned_data.get('password')

    #                 profile.username = email
    #                 profile.role = 'User'
    #                 profile.date_joined = timezone.now()
    #                 profile.password = make_password(password)

    #                 profile.save()
                    

    #                 traveller = traveller_form.save(commit=False)
    #                 traveller.profile = profile
    #                 traveller.name = f'{profile.first_name} {profile.last_name}'
    #                 traveller.email = profile.email
    #                 traveller.save()

    #                 # send email
    #                 subject = 'Successfully Registered !!!'
    #                 recipient = profile.email
    #                 template = 'emails/success-registration.html'
    #                 context = {'name': traveller.name, 'username': profile.username, 'password': password}
    #                 threading.Thread(target=send_email, args=(subject, recipient, template, context)).start()

    #                 return redirect('login')
    #         except IntegrityError:

    #             profile_form.add_error(None, "A traveller with this profile already exists.")


    #     # Show errors if form is invalid
    #     return render(request, 'authentication/register_user.html', {
    #         'profile_form': profile_form,
    #         'traveller_form': traveller_form
    #     })

    def post(self, request):
        form = ProfileForm(request.POST)
        traveller_form = TravellerRegisterForm(request.POST, request.FILES)

        if form.is_valid() and traveller_form.is_valid():
            profile = form.save(commit=False)
            profile.role = 'User'
            profile.save()

            # Get auto-created traveller from signal
            traveller = profile.traveller

            # Now update it using form data (number, image, etc.)
            traveller.number = traveller_form.cleaned_data['number']
            traveller.image = traveller_form.cleaned_data.get('image')
            traveller.save()

            login(request, profile)
            messages.success(request, 'Registration successful!')
            return redirect('home')  # Replace with your desired redirect
        else:
            messages.error(request, 'Registration failed. Please fix the errors below.')

        return render(request, 'authentication/register.html', {
            'form': form,
            'traveller_form': traveller_form
        })

