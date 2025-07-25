"""
URL configuration for travelbloom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from diary.views import HomeView
from django.conf.urls.static import static
from django.http import HttpResponse
from django.conf import settings

def test_home(request):
    return HttpResponse("✅ Render is working!")

urlpatterns = [
    #  path('', test_home),
    path('admin/', admin.site.urls),
    path('explore/',include('explore.urls')),
    path('diary/',include('diary.urls')),
    path('authentication/', include('authentication.urls')),
    path('chatbot/',include('chatbot.urls')),
    path('blogs/',include('blog.urls')),
    path('payment/', include('payments.urls')),
    path('', HomeView.as_view(), name= 'home'),
    

]


urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)