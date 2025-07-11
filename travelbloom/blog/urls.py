from django.urls import path
from . import views

urlpatterns = [
    path('blog-list/', views.BlogListCreateView.as_view(), name='blog-list'),
    ]