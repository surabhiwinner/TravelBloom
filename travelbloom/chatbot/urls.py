from django.urls import path

from . import views

from .views import ChatBotView

urlpatterns = [

    path('chat/', views.ChatBotView.as_view(), name='chatbot')
]