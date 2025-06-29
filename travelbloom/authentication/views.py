from django.shortcuts import render

from django.contrib.auth import authenticate, login,logout

from django.views import View

from .forms import LoginForm
# Create your views here.



class LoginView(View):

    def get(self, request, *args , **kwargs):

        form = LoginForm()

        data = {
            'page' : 'login-page',
            'form'  : form
        }
        return render(request, 'authentication/login.html',context=data)