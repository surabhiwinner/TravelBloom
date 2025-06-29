from django.urls import path

from . import views


urlpatterns = [
    path('create/', views.DiaryEntryWriteView.as_view(), name= 'create'),
    path('entry-list/',views.DiaryListView.as_view(), name='entry-list')
]