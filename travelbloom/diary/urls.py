from django.urls import path

from . import views


urlpatterns = [
    path('create/', views.DiaryEntryWriteView.as_view(), name= 'create'),
    path('entries/',views.DiaryListView.as_view(), name='diary-list'), 
    path('entries-detail/<str:uuid>/', views.DiaryEntryDetailView.as_view(), name='diary_detail'),
]